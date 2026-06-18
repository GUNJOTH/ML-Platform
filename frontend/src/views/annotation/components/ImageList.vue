<template>
  <div class="image-list">
    <h4>图片列表 ({{ images.length }})</h4>
    <div
      v-for="img in images"
      :key="img.id"
      class="image-item"
      :class="{ active: img.id === selectedId }"
      @click="emit('select', img)"
    >
      <span class="image-name">{{ img.filename }}</span>
    </div>
    <p v-if="images.length === 0" class="empty">无图片</p>
  </div>
</template>

<script setup lang="ts">
interface ImageItem {
  id: string
  filename: string
  file_path: string
}

defineProps<{
  images: ImageItem[]
  selectedId: string
}>()

const emit = defineEmits<{
  select: [image: ImageItem]
}>()
</script>

<style scoped>
h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #333;
}

.image-item {
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-item:hover {
  background: #f0f2f5;
}

.image-item.active {
  background: #ecf5ff;
  color: #409eff;
}

.empty {
  color: #999;
  font-size: 12px;
  text-align: center;
}
</style>
