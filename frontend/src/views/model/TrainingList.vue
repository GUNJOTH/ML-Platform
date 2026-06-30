<template>
  <div class="training-list">
    <div class="page-header">
      <h3>训练任务</h3>
      <el-button type="primary" @click="showForm = true">新建训练</el-button>
    </div>

    <el-table :data="tasks" border stripe>
      <el-table-column prop="name" label="任务名称" />
      <el-table-column prop="task_type" label="类型" width="100" />
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="resolveTaskStatusTag(row.status)">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="进度" width="160">
        <template #default="{ row }">
          <el-progress
            :percentage="row.id === activeTaskId ? liveProgress : row.progress"
            :stroke-width="6"
          />
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="240">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 'running'"
            size="small"
            type="danger"
            link
            @click="handleCancel(row.id)"
          >
            取消
          </el-button>
          <el-button
            v-if="row.status === 'completed'"
            size="small"
            type="success"
            link
            @click="handleExport(row.id)"
          >
            导出
          </el-button>
          <el-button
            v-if="row.status === 'running' || row.status === 'completed' || row.status === 'failed'"
            size="small"
            type="primary"
            link
            @click="handleDetail(row)"
          >
            详情
          </el-button>
          <el-button
            v-if="row.status !== 'running'"
            size="small"
            type="danger"
            link
            @click="handleDelete(row.id)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <TrainingForm v-model="showForm" @created="handleCreated" />

    <TrainingDetailDialog
      v-model:visible="detailVisible"
      :task="selectedTask"
      :artifacts="selectedArtifacts"
      :history="selectedHistory"
      :context="selectedContext"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { buildTrainingDetailContext } from '@/composables/useTrainingDetailContext'
import { resolveTaskStatusTag } from '@/utils/task'
import {
  cancelTask,
  deleteTask,
  exportTaskModel,
  getTaskArtifacts,
  getTaskHistory,
  getTaskProgress,
  getTasks,
  syncTask,
} from '@/api/task'
import type {
  Task,
  TaskArtifactItem,
  TaskHistoryPoint,
  TrainingDetailContext,
} from '@/types/task'
import TrainingDetailDialog from './components/TrainingDetailDialog.vue'
import TrainingForm from './components/TrainingForm.vue'

const tasks = ref<Task[]>([])
const showForm = ref(false)
const activeTaskId = ref('')
const liveProgress = ref(0)
const detailVisible = ref(false)
const selectedTask = ref<Task | null>(null)
const selectedArtifacts = ref<TaskArtifactItem[]>([])
const selectedHistory = ref<TaskHistoryPoint[]>([])
const selectedContext = ref<TrainingDetailContext | null>(null)

let ws: WebSocket | null = null
let pollTimer: ReturnType<typeof setInterval> | null = null

onMounted(loadTasks)

async function loadTasks() {
  try {
    tasks.value = await getTasks({ task_type: 'training' })
  } catch {
    tasks.value = []
  }

  const runningTasks = tasks.value.filter((task) => task.status === 'running')
  for (const task of runningTasks) {
    try {
      await syncTask(task.id)
    } catch {
      // still running
    }
  }

  if (runningTasks.length) {
    tasks.value = await getTasks({ task_type: 'training' })
    const stillRunning = tasks.value.find((task) => task.status === 'running')
    if (stillRunning) {
      watchProgress(stillRunning.id)
    }
  }
}

function handleCreated(taskId: string) {
  loadTasks()
  if (taskId) {
    watchProgress(taskId)
  }
}

function watchProgress(taskId: string) {
  cleanup()
  activeTaskId.value = taskId

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const host = window.location.host
  ws = new WebSocket(`${protocol}://${host}/api/v1/ws/tasks/${taskId}`)

  ws.onmessage = (event: MessageEvent) => {
    const data = JSON.parse(event.data)
    if (data.progress !== undefined) {
      liveProgress.value = data.progress
    }
    if (data.type === 'complete') {
      liveProgress.value = 100
      cleanup()
      syncTask(taskId).finally(loadTasks)
    }
  }

  ws.onerror = () => {
    startPolling(taskId)
  }

  ws.onclose = () => {
    if (activeTaskId.value) {
      startPolling(taskId)
    }
  }
}

function startPolling(taskId: string) {
  if (pollTimer) {
    return
  }
  pollTimer = setInterval(async () => {
    try {
      const data = await getTaskProgress(taskId)
      liveProgress.value = data.progress || 0
      if (data.progress >= 100) {
        cleanup()
        await syncTask(taskId)
        loadTasks()
      }
    } catch {
      // silent
    }
  }, 3000)
}

function cleanup() {
  ws?.close()
  ws = null
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function handleCancel(id: string) {
  await cancelTask(id)
  cleanup()
  loadTasks()
}

async function handleDetail(task: Task) {
  selectedTask.value = task
  selectedArtifacts.value = []
  selectedHistory.value = []
  selectedContext.value = null
  detailVisible.value = true

  if (task.status === 'running') {
    return
  }

  try {
    const [history, artifacts, context] = await Promise.all([
      getTaskHistory(task.id),
      getTaskArtifacts(task.id),
      buildTrainingDetailContext(task),
    ])
    selectedHistory.value = history
    selectedArtifacts.value = artifacts.items
    selectedContext.value = context
  } catch {
    // no detail available
  }
}

async function handleDelete(id: string) {
  try {
    await ElMessageBox.confirm('确定删除该训练任务吗？', '确认', { type: 'warning' })
    await deleteTask(id)
    ElMessage.success('已删除')
    loadTasks()
  } catch {
    // cancelled
  }
}

async function handleExport(id: string) {
  try {
    await exportTaskModel(id)
    ElMessage.success('模型已导出到模型管理')
    loadTasks()
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : '导出失败'
    ElMessage.error(message)
  }
}

onUnmounted(() => {
  cleanup()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
