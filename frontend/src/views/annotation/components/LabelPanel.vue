<template>
  <div class="label-panel">
    <h4>类别标签</h4>
    <div
      v-for="label in labels"
      :key="label.id"
      class="label-item"
      :class="{ active: label.id === selectedLabelId }"
      @click="emit('select', label)"
    >
      <span class="color-dot" :style="{ background: label.color }" />
      <span class="label-name">{{ label.name }}</span>
    </div>
    <p v-if="labels.length === 0" class="empty">暂无类别</p>
  </div>
</template>

<script setup lang="ts">
interface LabelItem {
  id: string
  name: string
  color: string
}

defineProps<{
  labels: LabelItem[]
  selectedLabelId: string
}>()

const emit = defineEmits<{
  select: [label: LabelItem]
}>()
</script>

<style scoped>
h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #333;
}

.label-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.label-item:hover {
  background: #f0f2f5;
}

.label-item.active {
  background: #ecf5ff;
  border: 1px solid #409eff;
}

.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  flex-shrink: 0;
}

.label-name {
  font-size: 13px;
}

.empty {
  color: #999;
  font-size: 12px;
  text-align: center;
}
</style>
