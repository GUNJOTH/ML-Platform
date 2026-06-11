<template>
  <div class="image-canvas">
    <div class="canvas-placeholder">
      <p>Canvas 标注区域</p>
      <p class="hint">选择左侧图片开始标注</p>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.image-canvas {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.canvas-placeholder {
  text-align: center;
  color: #999;
}

.hint {
  font-size: 12px;
  margin-top: 8px;
}
</style>
