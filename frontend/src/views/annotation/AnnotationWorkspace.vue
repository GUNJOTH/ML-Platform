<template>
  <div class="annotation-workspace">
    <div class="workspace-left">
      <ImageList />
    </div>
    <div class="workspace-center">
      <ImageCanvas />
    </div>
    <div class="workspace-right">
      <LabelPanel />
    </div>
  </div>
</template>

<script setup lang="ts">
import ImageList from './components/ImageList.vue'
import ImageCanvas from './components/ImageCanvas.vue'
import LabelPanel from './components/LabelPanel.vue'
</script>

<style scoped>
.annotation-workspace {
  display: flex;
  height: calc(100vh - 120px);
  gap: 8px;
}

.workspace-left {
  width: 200px;
  background: #fff;
  border-radius: 4px;
  overflow-y: auto;
  padding: 8px;
}

.workspace-center {
  flex: 1;
  background: #2c2c2c;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.workspace-right {
  width: 240px;
  background: #fff;
  border-radius: 4px;
  padding: 12px;
  overflow-y: auto;
}
</style>
