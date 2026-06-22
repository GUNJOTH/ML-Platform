<template>
  <div class="image-list">
    <h4>图片列表 ({{ images.length }})</h4>
    <div
      v-for="image in images"
      :key="image.id"
      class="image-item"
      :class="{ active: image.id === selectedId }"
      @click="emit('select', image)"
    >
      <div class="image-main">
        <span class="image-name">{{ image.filename }}</span>
        <el-tag size="small" :type="image.draft_status === 'annotated' ? 'success' : 'info'">
          {{ image.draft_status === 'annotated' ? '已标' : '未标' }}
        </el-tag>
      </div>
    </div>
    <p v-if="images.length === 0" class="empty">无图片</p>
  </div>
</template>

<script setup lang="ts">
import type { WorkspaceImageListItem } from '@/types/annotation-workspace'

defineProps<{
  images: WorkspaceImageListItem[]
  selectedId: string
}>()

const emit = defineEmits<{
  select: [image: WorkspaceImageListItem]
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
}

.image-item:hover {
  background: #f0f2f5;
}

.image-item.active {
  background: #ecf5ff;
  color: #409eff;
}

.image-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.image-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.empty {
  color: #999;
  font-size: 12px;
  text-align: center;
}
</style>
