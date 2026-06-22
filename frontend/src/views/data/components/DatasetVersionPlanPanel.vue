<template>
  <el-card class="plan-card">
    <template #header>当前阶段建议</template>
    <div class="plan-grid">
      <div v-for="item in items" :key="item.title" class="plan-item">
        <div class="plan-title">{{ item.title }}</div>
        <div class="plan-desc">{{ item.description }}</div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{
  items: Array<{ title: string; description: string }>
}>()
</script>

<style scoped>
.plan-card {
  margin-bottom: 20px;
  border-radius: 16px;
}

.plan-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.plan-item {
  padding: 14px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8fafc, #eef2ff);
  border: 1px solid #e2e8f0;
}

.plan-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.plan-desc {
  margin-top: 8px;
  font-size: 12px;
  color: #64748b;
  line-height: 1.6;
}
</style>
