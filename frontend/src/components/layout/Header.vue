<template>
  <div class="header">
    <span class="page-title">{{ currentTitle }}</span>
    <div class="header-right">
      <span>AI Platform v0.1</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentTitle = computed(() => (route.meta?.title as string) || '')
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  font-size: 14px;
  color: #909399;
}
</style>
