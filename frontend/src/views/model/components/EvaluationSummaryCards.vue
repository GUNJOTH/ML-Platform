<template>
  <el-card>
    <template #header>评估摘要</template>
    <el-row :gutter="16">
      <el-col :span="8" v-for="item in cards" :key="item.label">
        <div class="metric-card">
          <span class="metric-label">{{ item.label }}</span>
          <span class="metric-value">{{ item.value }}</span>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{
  cards: Array<{ label: string; value: string }>
}>()
</script>

<style scoped>
.metric-card {
  text-align: center;
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 16px;
}

.metric-label {
  display: block;
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}
</style>
