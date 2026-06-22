<template>
  <el-card class="report-row">
    <template #header>分类别指标</template>
    <el-table :data="rows" border stripe max-height="360">
      <el-table-column prop="class_name" label="类别" min-width="140" />
      <el-table-column prop="image_count" label="样本数" width="100" />
      <el-table-column label="Precision" width="110">
        <template #default="{ row }">{{ formatPercent(row.precision) }}</template>
      </el-table-column>
      <el-table-column label="Recall" width="110">
        <template #default="{ row }">{{ formatPercent(row.recall) }}</template>
      </el-table-column>
      <el-table-column label="F1" width="100">
        <template #default="{ row }">{{ formatPercent(row.f1) }}</template>
      </el-table-column>
      <el-table-column label="mAP50" width="110">
        <template #default="{ row }">{{ formatPercent(row.map50) }}</template>
      </el-table-column>
      <el-table-column label="mAP50-95" width="120">
        <template #default="{ row }">{{ formatPercent(row.map50_95) }}</template>
      </el-table-column>
    </el-table>
    <div v-if="!rows.length" class="empty-inline">
      当前评估结果未提供分类别指标。
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { formatPercent } from '@/types/evaluation'
import type { PerClassMetric } from '@/types/evaluation'

defineProps<{
  rows: PerClassMetric[]
}>()
</script>

<style scoped>
.report-row {
  margin-top: 20px;
}

.empty-inline {
  padding-top: 12px;
  color: #999;
  font-size: 13px;
}
</style>
