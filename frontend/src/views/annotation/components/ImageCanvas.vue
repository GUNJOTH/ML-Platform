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
      <el-button size="small" type="success" @click="handleSave">暂存当前图片</el-button>
    </div>

    <div class="canvas-wrap">
      <canvas
        ref="canvasEl"
        :width="800"
        :height="600"
        class="annotation-canvas"
        tabindex="0"
        @mousedown="handleMouseDown"
        @mousemove="canvas.onMouseMove"
        @mouseup="canvas.onMouseUp"
        @keydown.delete="handleDelete"
      />
      <div v-if="!canDraw" class="canvas-mask">
        请先在右侧新增并选择类别，再开始标注。
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useCanvas, type BBox } from '@/composables/useCanvas'
import type { AnnotationViewData } from '@/types/annotation-workspace'

const props = defineProps<{
  imageSrc: string | null
  annotations: AnnotationViewData[]
  currentLabel: { id: string; name: string; color: string } | null
  canDraw: boolean
}>()

const emit = defineEmits<{
  save: [boxes: BBox[]]
  delete: [annotationId: string]
}>()

const canvasEl = ref<HTMLCanvasElement | null>(null)
const canvas = useCanvas(canvasEl)

defineExpose({
  updateSelectedLabel: canvas.updateSelectedLabel,
  selectMode: () => {
    canvas.mode.value = 'select'
  },
  drawMode: () => {
    canvas.mode.value = props.canDraw ? 'draw' : 'select'
  },
})

watch(() => props.imageSrc, async (src) => {
  if (src) {
    await canvas.loadImage(src)
    canvas.mode.value = props.canDraw ? 'draw' : 'select'
    loadAnnotations()
  }
})

watch(() => props.currentLabel, (label) => {
  if (label) {
    canvas.setLabel(label.id, label.name, label.color)
  }
})

watch(
  () => props.canDraw,
  (enabled) => {
    if (!enabled && canvas.mode.value === 'draw') {
      canvas.mode.value = 'select'
    }
  },
)

watch(() => props.annotations, loadAnnotations)

function loadAnnotations() {
  const boxes: BBox[] = props.annotations.map((annotation) => ({
    id: annotation.id,
    x: annotation.bbox.x,
    y: annotation.bbox.y,
    width: annotation.bbox.width,
    height: annotation.bbox.height,
    labelId: annotation.label_id,
    labelName: annotation.label_name,
    color: annotation.color,
  }))
  canvas.setBoxes(boxes)
}

function handleMouseDown(event: MouseEvent) {
  if (canvas.mode.value === 'draw' && !props.canDraw) {
    ElMessage.warning('请先新增并选择类别')
    return
  }
  canvas.onMouseDown(event)
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

.canvas-wrap {
  position: relative;
}

.annotation-canvas {
  border: 1px solid #ddd;
  cursor: crosshair;
  background: #f0f0f0;
}

.canvas-mask {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.52);
  color: #fff;
  font-size: 14px;
  text-align: center;
  padding: 24px;
  pointer-events: none;
}
</style>
