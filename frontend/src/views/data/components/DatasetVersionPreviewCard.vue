<template>
  <el-card class="section-card">
    <template #header>版本预览</template>
    <div class="preview-grid">
      <div class="preview-item">
        <span class="preview-label">数据集</span>
        <span class="preview-value">{{ datasetName }}</span>
      </div>
      <div class="preview-item">
        <span class="preview-label">版本名</span>
        <span class="preview-value">{{ versionName || '--' }}</span>
      </div>
      <div class="preview-item">
        <span class="preview-label">来源</span>
        <span class="preview-value">{{ sourceLabel }}</span>
      </div>
      <div class="preview-item">
        <span class="preview-label">训练格式</span>
        <span class="preview-value">{{ exportFormat }}</span>
      </div>
      <div class="preview-item">
        <span class="preview-label">冻结范围</span>
        <span class="preview-value">{{ includeSplitText }}</span>
      </div>
      <div class="preview-item">
        <span class="preview-label">划分策略</span>
        <span class="preview-value">{{ splitStrategyLabel }}</span>
      </div>
      <div v-if="splitPlanText" class="preview-item preview-item-wide">
        <span class="preview-label">最终落地</span>
        <span class="preview-value">{{ splitPlanText }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{
  datasetName: string
  versionName: string
  sourceLabel: string
  exportFormat: string
  includeSplitText: string
  splitStrategyLabel: string
  splitPlanText?: string
}>()
</script>

<style scoped>
.section-card {
  margin-bottom: 20px;
  border-radius: 16px;
}

.preview-grid {
  display: grid;
  gap: 12px;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 14px;
  border-radius: 12px;
  background: #f8fafc;
}

.preview-label {
  color: #64748b;
  font-size: 13px;
}

.preview-value {
  color: #0f172a;
  font-weight: 600;
  text-align: right;
}

.preview-item-wide {
  align-items: flex-start;
}
</style>
