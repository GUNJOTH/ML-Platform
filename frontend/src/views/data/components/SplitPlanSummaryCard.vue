<template>
  <el-card class="split-plan-card">
    <template #header>{{ title }}</template>
    <div class="split-plan-topline">{{ strategyLabel }}</div>
    <div class="split-plan-subtitle">{{ subtitle }}</div>

    <div class="split-grid">
      <div
        v-for="item in items"
        :key="item.split"
        class="split-item"
      >
        <div class="split-name">{{ item.split }}</div>
        <div class="split-count">{{ item.count }}</div>
        <div class="split-help">{{ item.help }}</div>
      </div>
    </div>

    <div v-if="notes" class="split-notes">
      {{ notes }}
    </div>
  </el-card>
</template>

<script setup lang="ts">
export interface SplitPlanItem {
  split: string
  count: number
  help: string
}

defineProps<{
  title: string
  strategyLabel: string
  subtitle: string
  items: SplitPlanItem[]
  notes?: string
}>()
</script>

<style scoped>
.split-plan-card {
  border-radius: 16px;
}

.split-plan-topline {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.split-plan-subtitle {
  margin-top: 8px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.7;
}

.split-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.split-item {
  padding: 14px 12px;
  border-radius: 14px;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px solid #e2e8f0;
  text-align: center;
}

.split-name {
  font-size: 13px;
  color: #475569;
  text-transform: lowercase;
}

.split-count {
  margin-top: 8px;
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
}

.split-help {
  margin-top: 6px;
  font-size: 12px;
  color: #64748b;
}

.split-notes {
  margin-top: 14px;
  padding: 12px 14px;
  border-radius: 12px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1d4ed8;
  font-size: 12px;
  line-height: 1.7;
}
</style>
