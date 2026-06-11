<template>
  <div class="image-list">
    <h4>图片列表</h4>
    <div class="images">
      <div
        v-for="img in images"
        :key="img.id"
        class="image-thumb"
        :class="{ active: img.id === currentId }"
      >
        <span>{{ img.filename }}</span>
      </div>
      <p v-if="!images.length" class="empty-hint">暂无图片</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { DatasetImage } from '@/types/dataset'

const images = ref<DatasetImage[]>([])
const currentId = ref('')
</script>

<style scoped>
.image-list h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
}

.image-thumb {
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.image-thumb:hover {
  background-color: #f0f2f5;
}

.image-thumb.active {
  background-color: #ecf5ff;
  color: #409eff;
}

.empty-hint {
  color: #999;
  font-size: 12px;
  text-align: center;
}
</style>
