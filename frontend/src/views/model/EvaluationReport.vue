<template>
  <div class="evaluation-page">
    <div class="page-header">
      <h3>模型评估</h3>
    </div>

    <el-row :gutter="20" class="config-row">
      <el-col :span="8">
        <el-card>
          <template #header>评估配置</template>
          <el-form label-width="90px">
            <el-form-item label="模型">
              <el-select v-model="selectedModel" placeholder="选择模型" style="width: 100%">
                <el-option
                  v-for="model in models"
                  :key="model.id"
                  :label="model.name"
                  :value="model.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="数据集">
              <el-select v-model="selectedDataset" placeholder="选择数据集" style="width: 100%">
                <el-option
                  v-for="dataset in datasets"
                  :key="dataset.id"
                  :label="dataset.name"
                  :value="dataset.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="startEval">
                开始评估
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="16">
        <EvaluationActiveTaskCard :task="activeTask" />

        <template v-if="report">
          <EvaluationReportPanel
            :report="report"
            :artifacts="artifacts"
            artifact-title="评估产物"
          />
        </template>

        <el-card v-else>
          <div class="empty-hint">
            {{ activeTask?.status === 'running'
              ? '评估正在后台执行，结果完成后会自动显示。'
              : '选择模型和数据集后开始评估。' }}
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getDatasets } from '@/api/dataset'
import { runEvaluation } from '@/api/evaluation'
import { getModels } from '@/api/model'
import { getTask, getTaskArtifacts, getTasks, syncTask } from '@/api/task'
import type { Dataset } from '@/types/dataset'
import { normalizeEvaluationReport } from '@/types/evaluation'
import type { EvaluationReport } from '@/types/evaluation'
import type { MLModel } from '@/types/model'
import type { Task, TaskArtifactItem } from '@/types/task'
import EvaluationActiveTaskCard from './components/EvaluationActiveTaskCard.vue'
import EvaluationReportPanel from './components/EvaluationReportPanel.vue'

const models = ref<MLModel[]>([])
const datasets = ref<Dataset[]>([])
const selectedModel = ref('')
const selectedDataset = ref('')
const loading = ref(false)
const activeTask = ref<Task | null>(null)
const report = ref<EvaluationReport | null>(null)
const artifacts = ref<TaskArtifactItem[]>([])
let pollTimer: ReturnType<typeof setInterval> | null = null

onMounted(async () => {
  const [modelList, datasetList] = await Promise.all([getModels(), getDatasets()])
  models.value = modelList
  datasets.value = datasetList
  await resumeLatestEvaluation()
})

onUnmounted(() => {
  clearPollTimer()
})

async function startEval() {
  if (!selectedModel.value || !selectedDataset.value) {
    ElMessage.warning('请选择模型和数据集')
    return
  }

  loading.value = true
  activeTask.value = null
  report.value = null
  artifacts.value = []

  try {
    const task = await runEvaluation({
      model_id: selectedModel.value,
      dataset_id: selectedDataset.value,
    })
    activeTask.value = task
    pollForResult(task.id)
  } catch (err: unknown) {
    loading.value = false
    const message = err instanceof Error ? err.message : '评估启动失败'
    ElMessage.error(message)
  }
}

async function resumeLatestEvaluation() {
  try {
    const tasks = await getTasks({ task_type: 'evaluation', page_size: 50 })
    const runningTask = tasks.find((task) => task.status === 'running')
    if (runningTask) {
      activeTask.value = runningTask
      selectedModel.value = runningTask.model_id || ''
      selectedDataset.value = runningTask.dataset_id || ''
      loading.value = true
      pollForResult(runningTask.id)
      return
    }

    const latestCompletedTask = tasks.find((task) => task.status === 'completed' && task.result)
    if (latestCompletedTask) {
      await applyCompletedTask(latestCompletedTask)
    }
  } catch {
    activeTask.value = null
  }
}

function pollForResult(taskId: string) {
  clearPollTimer()
  pollTimer = setInterval(async () => {
    try {
      await syncTask(taskId)
      const task = await getTask(taskId)
      activeTask.value = task

      if (task.status === 'completed' && task.result) {
        clearPollTimer()
        await applyCompletedTask(task)
      } else if (task.status === 'failed' || task.status === 'cancelled') {
        clearPollTimer()
        loading.value = false
        if (task.status === 'failed') {
          ElMessage.error(task.error_message || '评估失败')
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        ElMessage.error(err.message)
      }
      clearPollTimer()
      loading.value = false
    }
  }, 3000)
}

async function applyCompletedTask(task: Task) {
  activeTask.value = task
  loading.value = false
  report.value = task.result ? normalizeEvaluationReport(task.result) : null
  selectedModel.value = task.model_id || ''
  selectedDataset.value = task.dataset_id || ''

  try {
    const artifactResult = await getTaskArtifacts(task.id)
    artifacts.value = artifactResult.items
  } catch {
    artifacts.value = []
  }
}

function clearPollTimer() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}
</script>

<style scoped>
.page-header {
  margin-bottom: 16px;
}

.config-row {
  margin-bottom: 20px;
}

.empty-hint {
  text-align: center;
  color: #999;
  padding: 40px;
}
</style>
