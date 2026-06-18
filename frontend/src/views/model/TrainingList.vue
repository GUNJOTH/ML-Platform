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
          <el-tag :type="statusTag(row.status)">{{ row.status }}</el-tag>
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
          >取消</el-button>
          <el-button
            v-if="row.status === 'completed'"
            size="small"
            type="success"
            link
            @click="handleExport(row.id)"
          >导出</el-button>
          <el-button
            v-if="row.status === 'completed' || row.status === 'failed'"
            size="small"
            type="primary"
            link
            @click="handleDetail(row)"
          >详情</el-button>
          <el-button
            v-if="row.status !== 'running'"
            size="small"
            type="danger"
            link
            @click="handleDelete(row.id)"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <TrainingForm v-model="showForm" @created="handleCreated" />

    <el-dialog v-model="detailVisible" title="训练详情" width="700px">
      <template v-if="selectedTask">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="任务名称" :span="2">{{ selectedTask.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusTag(selectedTask.status)">{{ selectedTask.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="进度">{{ selectedTask.progress }}%</el-descriptions-item>
        </el-descriptions>

        <template v-if="selectedTask.status === 'completed' && selectedTask.result">
          <el-descriptions :column="4" border size="small" style="margin-top: 12px">
            <el-descriptions-item label="mAP50">{{ fmtMetric(selectedTask.result.map50) }}</el-descriptions-item>
            <el-descriptions-item label="mAP50-95">{{ fmtMetric(selectedTask.result.map50_95) }}</el-descriptions-item>
            <el-descriptions-item label="Precision">{{ fmtMetric(selectedTask.result.precision) }}</el-descriptions-item>
            <el-descriptions-item label="Recall">{{ fmtMetric(selectedTask.result.recall) }}</el-descriptions-item>
          </el-descriptions>
        </template>

        <div ref="chartRef" style="width: 100%; height: 320px; margin-top: 16px"></div>

        <template v-if="selectedTask.status === 'failed' && selectedTask.error_message">
          <el-alert type="error" :closable="false" show-icon style="margin-top: 12px">
            {{ selectedTask.error_message }}
          </el-alert>
        </template>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { getTasks, cancelTask, syncTask, deleteTask, getTaskHistory, exportTaskModel } from '@/api/task'
import TrainingForm from './components/TrainingForm.vue'
import type { Task } from '@/types/task'

const tasks = ref<Task[]>([])
const showForm = ref(false)
const activeTaskId = ref('')
const liveProgress = ref(0)
const detailVisible = ref(false)
const selectedTask = ref<Task | null>(null)
const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

let ws: WebSocket | null = null
let pollTimer: ReturnType<typeof setInterval> | null = null

onMounted(loadTasks)

async function loadTasks() {
  try {
    tasks.value = await getTasks({ task_type: 'training' })
  } catch {
    tasks.value = []
  }
  const runningTasks = tasks.value.filter((t) => t.status === 'running')
  for (const t of runningTasks) {
    try { await syncTask(t.id) } catch { /* still running */ }
  }
  if (runningTasks.length) {
    tasks.value = await getTasks({ task_type: 'training' })
    const stillRunning = tasks.value.find((t) => t.status === 'running')
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
  if (pollTimer) return
  pollTimer = setInterval(async () => {
    try {
      const res = await fetch(`/api/v1/tasks/${taskId}/progress`)
      const data = await res.json()
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

function statusTag(status: string): string {
  const map: Record<string, string> = {
    pending: 'info',
    running: '',
    completed: 'success',
    failed: 'danger',
    cancelled: 'warning',
  }
  return map[status] || 'info'
}

async function handleDetail(task: Task) {
  selectedTask.value = task
  detailVisible.value = true
  await nextTick()
  try {
    const history = await getTaskHistory(task.id)
    renderChart(history)
  } catch {
    // no history available
  }
}

function renderChart(history: Array<{ epoch: number; train_loss?: number; map50?: number; map50_95?: number }>) {
  if (!chartRef.value || !history.length) return
  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Train Loss', 'mAP50', 'mAP50-95'] },
    xAxis: { type: 'category', data: history.map(h => `${h.epoch}`) },
    yAxis: [
      { type: 'value', name: 'Loss', position: 'left' },
      { type: 'value', name: 'mAP', position: 'right', min: 0, max: 1 },
    ],
    series: [
      { name: 'Train Loss', type: 'line', data: history.map(h => h.train_loss ?? null), smooth: true },
      { name: 'mAP50', type: 'line', yAxisIndex: 1, data: history.map(h => h.map50 ?? null), smooth: true },
      { name: 'mAP50-95', type: 'line', yAxisIndex: 1, data: history.map(h => h.map50_95 ?? null), smooth: true },
    ],
  })
}

async function handleDelete(id: string) {
  try {
    await ElMessageBox.confirm('确定删除该训练任务？', '确认', { type: 'warning' })
    await deleteTask(id)
    ElMessage.success('已删除')
    loadTasks()
  } catch { /* cancelled */ }
}

async function handleExport(id: string) {
  try {
    await exportTaskModel(id)
    ElMessage.success('模型已导出到模型管理')
    loadTasks()
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : '导出失败'
    ElMessage.error(msg)
  }
}

function fmtMetric(value: unknown): string {
  if (value === undefined || value === null) return '--'
  return ((value as number) * 100).toFixed(1) + '%'
}

onUnmounted(() => {
  cleanup()
  if (chartInstance) chartInstance.dispose()
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
