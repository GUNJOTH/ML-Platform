<template>
  <el-dialog :model-value="visible" title="训练详情" width="880px" @close="emit('update:visible', false)">
    <template v-if="task">
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="任务名称" :span="2">{{ task.name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTag(task.status)">{{ task.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="进度">{{ task.progress }}%</el-descriptions-item>
      </el-descriptions>

      <template v-if="task.status === 'completed' && task.result">
        <el-descriptions :column="4" border size="small" style="margin-top: 12px">
          <el-descriptions-item label="mAP50">{{ fmtMetric(task.result.map50) }}</el-descriptions-item>
          <el-descriptions-item label="mAP50-95">{{ fmtMetric(task.result.map50_95) }}</el-descriptions-item>
          <el-descriptions-item label="Precision">{{ fmtMetric(task.result.precision) }}</el-descriptions-item>
          <el-descriptions-item label="Recall">{{ fmtMetric(task.result.recall) }}</el-descriptions-item>
        </el-descriptions>
      </template>

      <div ref="chartRef" class="history-chart"></div>

      <TaskArtifactPanel
        v-if="artifacts.length"
        title="任务产物"
        :artifacts="artifacts"
      />

      <template v-if="task.status === 'failed' && task.error_message">
        <el-alert type="error" :closable="false" show-icon style="margin-top: 12px">
          {{ task.error_message }}
        </el-alert>
      </template>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import * as echarts from 'echarts'
import type { Task, TaskArtifactItem } from '@/types/task'
import TaskArtifactPanel from './TaskArtifactPanel.vue'

const props = defineProps<{
  visible: boolean
  task: Task | null
  artifacts: TaskArtifactItem[]
  history: Array<{ epoch: number; train_loss?: number; map50?: number; map50_95?: number }>
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

watch(
  () => [props.visible, props.history] as const,
  async ([visible, history]) => {
    if (!visible || !history.length) {
      return
    }
    await nextTick()
    renderChart(history)
  },
  { deep: true },
)

function renderChart(
  history: Array<{ epoch: number; train_loss?: number; map50?: number; map50_95?: number }>,
) {
  if (!chartRef.value || !history.length) {
    return
  }
  if (chartInstance) {
    chartInstance.dispose()
  }
  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Train Loss', 'mAP50', 'mAP50-95'] },
    xAxis: { type: 'category', data: history.map((item) => `${item.epoch}`) },
    yAxis: [
      { type: 'value', name: 'Loss', position: 'left' },
      { type: 'value', name: 'mAP', position: 'right', min: 0, max: 1 },
    ],
    series: [
      {
        name: 'Train Loss',
        type: 'line',
        data: history.map((item) => item.train_loss ?? null),
        smooth: true,
      },
      {
        name: 'mAP50',
        type: 'line',
        yAxisIndex: 1,
        data: history.map((item) => item.map50 ?? null),
        smooth: true,
      },
      {
        name: 'mAP50-95',
        type: 'line',
        yAxisIndex: 1,
        data: history.map((item) => item.map50_95 ?? null),
        smooth: true,
      },
    ],
  })
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

function fmtMetric(value: unknown): string {
  if (value === undefined || value === null) {
    return '--'
  }
  return `${((value as number) * 100).toFixed(1)}%`
}
</script>

<style scoped>
.history-chart {
  width: 100%;
  height: 320px;
  margin-top: 16px;
}
</style>
