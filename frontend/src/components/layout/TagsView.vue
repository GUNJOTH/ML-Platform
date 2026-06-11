<template>
  <div class="tags-view">
    <el-tag
      v-for="tag in tagsStore.tags"
      :key="tag.path"
      :closable="tag.closable"
      :type="tag.path === tagsStore.activeTag ? '' : 'info'"
      :effect="tag.path === tagsStore.activeTag ? 'dark' : 'plain'"
      class="tag-item"
      @click="handleClick(tag)"
      @close="tagsStore.removeTag(tag.path)"
    >
      {{ tag.title }}
    </el-tag>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useTagsStore, type TagItem } from '@/stores/tags'

const router = useRouter()
const tagsStore = useTagsStore()

function handleClick(tag: TagItem) {
  router.push(tag.path)
}
</script>

<style scoped>
.tags-view {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  overflow-x: auto;
  white-space: nowrap;
}

.tag-item {
  cursor: pointer;
}
</style>
