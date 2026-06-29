<template>
  <el-dialog :model-value="visible" title="训练详情" width="880px" @close="emit('update:visible', false)">
    <template v-if="task">
      <el-card class="detail-card" shadow="never">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="任务名称" :span="2">{{ task.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="resolveTaskStatusTag(task.status)">{{ task.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="进度">{{ task.progress }}%</el-descriptions-item>
          <el-descriptions-item label="任务类型">{{ task.task_type }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(task.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(task.started_at) }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ formatDate(task.finished_at) }}</el-descriptions-item>
        </el-descriptions>

        <template v-if="context">
          <div class="detail-section-title">训练输入</div>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="数据集">{{ context.datasetName }}</el-descriptions-item>
            <el-descriptions-item label="预训练模型">
              {{ context.modelName }}<span v-if="context.modelVersion !== '--'"> ({{ context.modelVersion }})</span>
            </el-descriptions-item>
            <el-descriptions-item label="数据集版本">{{ context.versionName }}</el-descriptions-item>
            <el-descriptions-item label="导出记录">{{ context.exportName }}</el-descriptions-item>
            <el-descriptions-item label="导出格式">{{ context.exportFormat }}</el-descriptions-item>
            <el-descriptions-item label="导出时间">{{ formatDate(context.exportCreatedAt) }}</el-descriptions-item>
            <el-descriptions-item label="dataset.yaml" :span="2">{{ context.dataYamlPath }}</el-descriptions-item>
          </el-descriptions>
        </template>

        <div class="detail-section-title">训练配置</div>
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="Epochs">{{ readConfigValue('epochs') }}</el-descriptions-item>
          <el-descriptions-item label="Batch Size">{{ readConfigValue('batch_size') }}</el-descriptions-item>
          <el-descriptions-item label="图片尺寸">{{ readConfigValue('img_size') }}</el-descriptions-item>
          <el-descriptions-item label="优化器">{{ readConfigValue('optimizer') }}</el-descriptions-item>
          <el-descriptions-item label="学习率">{{ readConfigValue('lr0') }}</el-descriptions-item>
          <el-descriptions-item label="Device">{{ readConfigValue('device', 'auto') }}</el-descriptions-item>
          <el-descriptions-item label="Workers">{{ readConfigValue('workers', autoWorkersText) }}</el-descriptions-item>
          <el-descriptions-item label="Warmup Epochs">{{ readConfigValue('warmup_epochs') }}</el-descriptions-item>
          <el-descriptions-item label="Patience">{{ readConfigValue('patience') }}</el-descriptions-item>
          <el-descriptions-item label="余弦学习率">{{ formatBoolean(readConfigValue('cos_lr')) }}</el-descriptions-item>
          <el-descriptions-item label="Close Mosaic">{{ readConfigValue('close_mosaic') }}</el-descriptions-item>
          <el-descriptions-item label="使用预训练">{{ formatBoolean(readConfigValue('pretrained')) }}</el-descriptions-item>
          <el-descriptions-item label="Framework">{{ readConfigValue('framework') }}</el-descriptions-item>
        </el-descriptions>

        <template v-if="context">
          <div class="detail-section-title">数据摘要</div>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="图片总数">{{ context.imageCount || '--' }}</el-descriptions-item>
            <el-descriptions-item label="标注框总数">{{ context.boxCount || '--' }}</el-descriptions-item>
            <el-descriptions-item label="类别数">{{ context.classCount || '--' }}</el-descriptions-item>
            <el-descriptions-item label="划分统计">{{ context.splitSummary }}</el-descriptions-item>
            <el-descriptions-item label="类别名称" :span="2">
              {{ context.classNames.length ? context.classNames.join(' / ') : '--' }}
            </el-descriptions-item>
            <el-descriptions-item label="导出备注" :span="2">{{ context.exportNotes }}</el-descriptions-item>
          </el-descriptions>
        </template>

        <div class="detail-section-title">任务结果详情</div>
        <template v-if="task.status === 'completed' && task.result">
          <el-descriptions :column="4" border size="small">
            <el-descriptions-item label="Best Epoch">{{ readResultValue('best_epoch') }}</el-descriptions-item>
            <el-descriptions-item label="mAP50">{{ fmtMetric(task.result.map50) }}</el-descriptions-item>
            <el-descriptions-item label="mAP50-95">{{ fmtMetric(task.result.map50_95) }}</el-descriptions-item>
            <el-descriptions-item label="Precision">{{ fmtMetric(task.result.precision) }}</el-descriptions-item>
            <el-descriptions-item label="Recall">{{ fmtMetric(task.result.recall) }}</el-descriptions-item>
            <el-descriptions-item label="训练耗时">{{ formatDuration(task.result.train_duration_minutes) }}</el-descriptions-item>
            <el-descriptions-item label="权重大小">{{ formatSize(task.result.weight_size_mb) }}</el-descriptions-item>
            <el-descriptions-item label="模型参数量">{{ readResultValue('model_parameters') }}</el-descriptions-item>
          </el-descriptions>
        </template>

        <div ref="chartRef" class="history-chart"></div>

        <TaskArtifactPanel v-if="artifacts.length" title="任务产物" :artifacts="artifacts" />

        <template v-if="task.status === 'failed' && task.error_message">
          <el-alert type="error" :closable="false" show-icon style="margin-top: 12px">
            {{ task.error_message }}
          </el-alert>
        </template>
      </el-card>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import * as echarts from 'echarts'
import type { Task, TaskArtifactItem, TaskHistoryPoint, TrainingDetailContext } from '@/types/task'
import { resolveTaskStatusTag } from '@/utils/task'
import TaskArtifactPanel from './TaskArtifactPanel.vue'

const props = defineProps<{
  visible: boolean
  task: Task | null
  artifacts: TaskArtifactItem[]
  history: TaskHistoryPoint[]
  context: TrainingDetailContext | null
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null
const autoWorkersText = navigator.platform.toLowerCase().includes('win') ? '0' : '8'

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

function renderChart(history: TaskHistoryPoint[]) {
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

function fmtMetric(value: unknown): string {
  if (value === undefined || value === null) {
    return '--'
  }
  return `${(Number(value) * 100).toFixed(1)}%`
}

function formatDate(value?: string | null): string {
  if (!value || value === '--') {
    return '--'
  }
  return new Date(value).toLocaleString()
}

function readConfigValue(key: string, fallback = '--'): string {
  const value = props.task?.config?.[key]
  if (value === undefined || value === null || value === '') {
    return fallback
  }
  return String(value)
}

function readResultValue(key: string): string {
  const value = props.task?.result?.[key]
  if (value === undefined || value === null || value === '') {
    return '--'
  }
  return String(value)
}

function formatDuration(value: unknown): string {
  if (value === undefined || value === null || value === '') {
    return '--'
  }
  const minutes = Number(value)
  if (!Number.isFinite(minutes) || minutes <= 0) {
    return '--'
  }
  return `${minutes.toFixed(2)} min`
}

function formatSize(value: unknown): string {
  if (value === undefined || value === null || value === '') {
    return '--'
  }
  const size = Number(value)
  if (!Number.isFinite(size) || size <= 0) {
    return '--'
  }
  return `${size.toFixed(2)} MB`
}

function formatBoolean(value: string): string {
  if (value === 'true') {
    return '是'
  }
  if (value === 'false') {
    return '否'
  }
  return value
}
</script>

<style scoped>
.detail-card {
  border: none;
}

.detail-section-title {
  margin: 16px 0 10px;
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.history-chart {
  width: 100%;
  height: 320px;
  margin-top: 16px;
}
</style>
