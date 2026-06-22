<template>
  <template v-if="report">
    <EvaluationSummaryCards :cards="headlineCards" />
    <EvaluationReportDetails :report="report" />
    <EvaluationPerClassTable :rows="perClassRows" />
    <TaskArtifactPanel
      v-if="artifacts.length"
      :title="artifactTitle"
      :artifacts="artifacts"
    />
    <el-empty
      v-else-if="showArtifactEmpty"
      description="该评估记录暂无产物文件。"
      class="artifact-empty"
    />
  </template>

  <el-empty
    v-else-if="emptyDescription"
    :description="emptyDescription"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatPercent } from '@/types/evaluation'
import type { EvaluationReport } from '@/types/evaluation'
import type { TaskArtifactItem } from '@/types/task'
import EvaluationPerClassTable from './EvaluationPerClassTable.vue'
import EvaluationReportDetails from './EvaluationReportDetails.vue'
import EvaluationSummaryCards from './EvaluationSummaryCards.vue'
import TaskArtifactPanel from './TaskArtifactPanel.vue'

const props = withDefaults(defineProps<{
  report: EvaluationReport | null
  artifacts?: TaskArtifactItem[]
  artifactTitle?: string
  emptyDescription?: string
  showArtifactEmpty?: boolean
}>(), {
  artifacts: () => [],
  artifactTitle: '评估产物',
  emptyDescription: '',
  showArtifactEmpty: false,
})

const headlineCards = computed(() => {
  if (!props.report) {
    return []
  }

  return [
    { label: 'mAP50', value: formatPercent(props.report.map50) },
    { label: 'mAP75', value: formatPercent(props.report.map75 ?? props.report.map50_95) },
    { label: 'mAP50-95', value: formatPercent(props.report.map50_95) },
    { label: 'Precision', value: formatPercent(props.report.precision) },
    { label: 'Recall', value: formatPercent(props.report.recall) },
    { label: 'F1', value: formatPercent(props.report.f1) },
  ]
})

const perClassRows = computed(() => props.report?.per_class || [])
</script>

<style scoped>
.artifact-empty {
  margin-top: 20px;
}
</style>
