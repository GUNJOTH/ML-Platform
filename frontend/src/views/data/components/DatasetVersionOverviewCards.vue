<template>
  <el-row :gutter="16" class="overview-row">
    <el-col v-for="card in cards" :key="card.label" :xs="12" :sm="12" :md="6">
      <el-card class="overview-card" shadow="hover">
        <div class="overview-label">{{ card.label }}</div>
        <div class="overview-value">{{ card.value }}</div>
        <div class="overview-help">{{ card.help }}</div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
defineProps<{
  cards: Array<{ label: string; value: string | number; help: string }>
}>()
</script>

<style scoped>
.overview-row {
  margin-bottom: 20px;
}

.overview-card {
  border-radius: 14px;
}

.overview-label {
  font-size: 13px;
  color: #909399;
}

.overview-value {
  margin-top: 10px;
  font-size: 28px;
  font-weight: 700;
  color: #1f2a37;
}

.overview-help {
  margin-top: 8px;
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.5;
}
</style>
