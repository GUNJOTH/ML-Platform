<template>
  <div class="label-panel">
    <h4>类别</h4>
    <div class="label-list">
      <div class="label-item" v-for="label in labels" :key="label.id">
        <span class="label-color" :style="{ backgroundColor: label.color }"></span>
        <span>{{ label.name }}</span>
      </div>
    </div>
    <el-divider />
    <h4>标注列表</h4>
    <div class="annotation-list">
      <p class="empty-hint">暂无标注</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Label {
  id: string
  name: string
  color: string
}

const labels = ref<Label[]>([])
</script>

<style scoped>
.label-panel h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
}

.label-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  cursor: pointer;
}

.label-color {
  width: 14px;
  height: 14px;
  border-radius: 2px;
}

.empty-hint {
  color: #999;
  font-size: 12px;
  text-align: center;
}
</style>
