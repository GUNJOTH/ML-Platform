<template>
  <el-dialog
    :model-value="visible"
    title="评估详情"
    width="min(1100px, 92vw)"
    destroy-on-close
    @update:model-value="emit('update:visible', $event)"
  >
    <template v-if="task">
      <div class="detail-header">
        <div class="detail-main">
          <div class="detail-title">{{ task.name }}</div>
          <div class="detail-meta">
            <span>模型：{{ modelName }}</span>
            <span>数据集：{{ datasetName }}</span>
            <span>状态：{{ task.status }}</span>
          </div>
        </div>
      </div>

      <EvaluationReportPanel
        :report="report"
        :artifacts="artifacts"
        artifact-title="评估产物"
        empty-description="该评估记录暂无可展示的结构化报告，可能任务尚未完成或结果为空。"
        :show-artifact-empty="Boolean(report)"
      />
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import type { EvaluationReport } from '@/types/evaluation'
import type { Task, TaskArtifactItem } from '@/types/task'
import EvaluationReportPanel from './EvaluationReportPanel.vue'

defineProps<{
  visible: boolean
  task: Task | null
  report: EvaluationReport | null
  artifacts: TaskArtifactItem[]
  modelName: string
  datasetName: string
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()
</script>

<style scoped>
.detail-header {
  margin-bottom: 16px;
}

.detail-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  color: #606266;
  font-size: 13px;
}
</style>
