<template>
  <div class="image-canvas">
    <div class="toolbar">
      <el-radio-group v-model="canvas.mode.value" size="small">
        <el-radio-button value="draw">绘制</el-radio-button>
        <el-radio-button value="select">选择</el-radio-button>
      </el-radio-group>
      <el-button size="small" type="danger" :disabled="!canvas.selectedId.value" @click="handleDelete">
        删除标注
      </el-button>
      <el-button size="small" type="success" @click="handleSave">保存</el-button>
    </div>
    <canvas
      ref="canvasEl"
      :width="800"
      :height="600"
      class="annotation-canvas"
      @mousedown="canvas.onMouseDown"
      @mousemove="canvas.onMouseMove"
      @mouseup="canvas.onMouseUp"
      @keydown.delete="handleDelete"
      tabindex="0"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useCanvas, type BBox } from '@/composables/useCanvas'

interface AnnotationData {
  id?: string
  label_id: string
  label_name: string
  color: string
  bbox: { x: number; y: number; width: number; height: number }
}

const props = defineProps<{
  imageSrc: string | null
  annotations: AnnotationData[]
  currentLabel: { id: string; name: string; color: string } | null
}>()

const emit = defineEmits<{
  save: [boxes: BBox[]]
  delete: [annotationId: string]
}>()

const canvasEl = ref<HTMLCanvasElement | null>(null)
const canvas = useCanvas(canvasEl)

watch(() => props.imageSrc, async (src) => {
  if (src) {
    await canvas.loadImage(src)
    loadAnnotations()
  }
})

watch(() => props.currentLabel, (label) => {
  if (label) {
    canvas.setLabel(label.id, label.name, label.color)
  }
})

watch(() => props.annotations, loadAnnotations)

function loadAnnotations() {
  const boxes: BBox[] = props.annotations.map((a) => ({
    id: a.id || crypto.randomUUID(),
    x: a.bbox.x,
    y: a.bbox.y,
    width: a.bbox.width,
    height: a.bbox.height,
    labelId: a.label_id,
    labelName: a.label_name,
    color: a.color,
  }))
  canvas.setBoxes(boxes)
}

function handleDelete() {
  const id = canvas.selectedId.value
  if (id) {
    canvas.deleteSelected()
    emit('delete', id)
  }
}

function handleSave() {
  emit('save', canvas.boxes.value)
}
</script>

<style scoped>
.image-canvas {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.annotation-canvas {
  border: 1px solid #ddd;
  cursor: crosshair;
  background: #f0f0f0;
}
</style>
