<template>
  <el-row :gutter="20" class="report-row">
    <el-col :span="12">
      <el-card>
        <template #header>数据集概况</template>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="评估分集">
            {{ report.evaluation_config?.split || 'val' }}
          </el-descriptions-item>
          <el-descriptions-item label="图片数">
            {{ report.dataset_summary?.images ?? 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="标注实例数">
            {{ report.dataset_summary?.instances ?? 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="评估类别数">
            {{ report.dataset_summary?.classes ?? 0 }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card>
        <template #header>速度指标 (ms/图)</template>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="Preprocess">
            {{ formatMs(report.speed_ms?.preprocess) }}
          </el-descriptions-item>
          <el-descriptions-item label="Inference">
            {{ formatMs(report.speed_ms?.inference) }}
          </el-descriptions-item>
          <el-descriptions-item label="Loss">
            {{ formatMs(report.speed_ms?.loss) }}
          </el-descriptions-item>
          <el-descriptions-item label="Postprocess">
            {{ formatMs(report.speed_ms?.postprocess) }}
          </el-descriptions-item>
          <el-descriptions-item label="Total" :span="2">
            {{ formatMs(report.speed_ms?.total) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { formatMs } from '@/types/evaluation'
import type { EvaluationReport } from '@/types/evaluation'

defineProps<{
  report: EvaluationReport
}>()
</script>

<style scoped>
.report-row {
  margin-top: 20px;
}
</style>
