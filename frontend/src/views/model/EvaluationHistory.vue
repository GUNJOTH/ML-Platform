<template>
  <div class="evaluation-history">
    <div class="page-header">
      <h3>评估历史</h3>
      <div class="filters">
        <el-select
          v-model="selectedModelId"
          clearable
          placeholder="筛选模型"
          style="width: 200px"
        >
          <el-option v-for="model in models" :key="model.id" :label="model.name" :value="model.id" />
        </el-select>
        <el-select
          v-model="selectedDatasetId"
          clearable
          placeholder="筛选数据集"
          style="width: 200px"
        >
          <el-option
            v-for="dataset in datasets"
            :key="dataset.id"
            :label="dataset.name"
            :value="dataset.id"
          />
        </el-select>
        <el-button @click="loadTasks">刷新</el-button>
      </div>
    </div>

    <el-table :data="filteredTasks" border stripe>
      <el-table-column prop="name" label="评估名称" min-width="180" />
      <el-table-column label="模型" min-width="160">
        <template #default="{ row }">{{ modelName(row.model_id) }}</template>
      </el-table-column>
      <el-table-column label="数据集" min-width="160">
        <template #default="{ row }">{{ datasetName(row.dataset_id) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="statusTag(row.status)">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="mAP50" width="110">
        <template #default="{ row }">{{ fmtMetric(row.result?.map50) }}</template>
      </el-table-column>
      <el-table-column label="mAP50-95" width="120">
        <template #default="{ row }">{{ fmtMetric(row.result?.map50_95) }}</template>
      </el-table-column>
      <el-table-column label="Precision" width="110">
        <template #default="{ row }">{{ fmtMetric(row.result?.precision) }}</template>
      </el-table-column>
      <el-table-column label="Recall" width="110">
        <template #default="{ row }">{{ fmtMetric(row.result?.recall) }}</template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="完成时间" width="180">
        <template #default="{ row }">{{ formatDate(row.finished_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDetail(row)">详情</el-button>
          <el-button link type="danger" @click="handleDelete(row)">
            {{ row.status === 'running' ? '停止并删除' : '删除' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <EvaluationHistoryDetailDialog
      v-model:visible="detailVisible"
      :task="selectedTask"
      :report="selectedReport"
      :artifacts="selectedArtifacts"
      :model-name="selectedTask ? modelName(selectedTask.model_id) : '--'"
      :dataset-name="selectedTask ? datasetName(selectedTask.dataset_id) : '--'"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDatasets } from '@/api/dataset'
import { getModels } from '@/api/model'
import { deleteTask, getTask, getTaskArtifacts, getTasks, syncTask } from '@/api/task'
import type { Dataset } from '@/types/dataset'
import { normalizeEvaluationReport } from '@/types/evaluation'
import type { EvaluationReport } from '@/types/evaluation'
import type { MLModel } from '@/types/model'
import type { Task, TaskArtifactItem } from '@/types/task'
import EvaluationHistoryDetailDialog from './components/EvaluationHistoryDetailDialog.vue'

const tasks = ref<Task[]>([])
const models = ref<MLModel[]>([])
const datasets = ref<Dataset[]>([])
const selectedModelId = ref('')
const selectedDatasetId = ref('')

const detailVisible = ref(false)
const selectedTask = ref<Task | null>(null)
const selectedReport = ref<EvaluationReport | null>(null)
const selectedArtifacts = ref<TaskArtifactItem[]>([])

const filteredTasks = computed(() =>
  tasks.value.filter((task) => {
    const matchModel = !selectedModelId.value || task.model_id === selectedModelId.value
    const matchDataset = !selectedDatasetId.value || task.dataset_id === selectedDatasetId.value
    return matchModel && matchDataset
  }),
)

onMounted(async () => {
  await Promise.all([loadTasks(), loadFilters()])
})

async function loadTasks() {
  try {
    tasks.value = await getTasks({ task_type: 'evaluation', page_size: 50 })
    await syncRunningTasks()
  } catch {
    tasks.value = []
  }
}

async function syncRunningTasks() {
  const runningTasks = tasks.value.filter((task) => task.status === 'running')
  if (!runningTasks.length) {
    return
  }

  await Promise.all(
    runningTasks.map(async (task) => {
      try {
        await syncTask(task.id)
      } catch {
        // keep original status until next refresh
      }
    }),
  )

  tasks.value = await getTasks({ task_type: 'evaluation', page_size: 50 })

  if (selectedTask.value) {
    const latestTask = tasks.value.find((task) => task.id === selectedTask.value?.id)
    if (latestTask) {
      await openDetail(latestTask)
    }
  }
}

async function loadFilters() {
  try {
    const [modelList, datasetList] = await Promise.all([getModels(), getDatasets()])
    models.value = modelList
    datasets.value = datasetList
  } catch {
    models.value = []
    datasets.value = []
  }
}

function modelName(modelId: string | null): string {
  if (!modelId) {
    return '--'
  }
  return models.value.find((model) => model.id === modelId)?.name || '--'
}

function datasetName(datasetId: string | null): string {
  if (!datasetId) {
    return '--'
  }
  return datasets.value.find((dataset) => dataset.id === datasetId)?.name || '--'
}

function statusTag(status: string): string {
  const map: Record<string, string> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info',
  }
  return map[status] || 'info'
}

function fmtMetric(value: unknown): string {
  if (typeof value !== 'number') {
    return '--'
  }
  return `${(value * 100).toFixed(1)}%`
}

function formatDate(value: string | null): string {
  if (!value) {
    return '--'
  }
  return new Date(value).toLocaleString()
}

async function openDetail(task: Task) {
  let latestTask = task

  if (task.status === 'running') {
    try {
      await syncTask(task.id)
      latestTask = await getTask(task.id)
      tasks.value = tasks.value.map((item) => (item.id === latestTask.id ? latestTask : item))
    } catch {
      // keep current task snapshot
    }
  }

  selectedTask.value = latestTask
  selectedReport.value = latestTask.result ? normalizeEvaluationReport(latestTask.result) : null
  selectedArtifacts.value = []
  detailVisible.value = true

  try {
    const artifactResult = await getTaskArtifacts(latestTask.id)
    selectedArtifacts.value = artifactResult.items
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : '评估产物加载失败'
    ElMessage.error(message)
  }
}

async function handleDelete(task: Task) {
  const actionLabel = task.status === 'running' ? '停止并删除' : '删除'

  try {
    await ElMessageBox.confirm(
      `确定${actionLabel}评估记录“${task.name}”吗？该操作会同时移除该任务关联的历史记录与产物索引。`,
      '删除评估记录',
      {
        type: 'warning',
        confirmButtonText: actionLabel,
        cancelButtonText: '取消',
      },
    )
  } catch {
    return
  }

  try {
    await deleteTask(task.id)
    ElMessage.success(task.status === 'running' ? '评估已停止并删除' : '评估记录已删除')
    if (selectedTask.value?.id === task.id) {
      detailVisible.value = false
      selectedTask.value = null
      selectedReport.value = null
      selectedArtifacts.value = []
    }
    await loadTasks()
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : '删除评估记录失败'
    ElMessage.error(message)
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 16px;
}

.filters {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
