<template>
  <div class="inference-page">
    <div class="page-header">
      <h3>模型推理</h3>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>配置</template>
          <el-form label-width="80px">
            <el-form-item label="模型">
              <el-select v-model="selectedModel" placeholder="选择模型" style="width: 100%">
                <el-option
                  v-for="m in models"
                  :key="m.id"
                  :label="m.name"
                  :value="m.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="图片">
              <el-upload
                :auto-upload="false"
                :on-change="handleFileChange"
                :show-file-list="false"
                accept="image/*"
              >
                <el-button>选择图片</el-button>
              </el-upload>
              <span v-if="fileName" class="file-name">{{ fileName }}</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="runInference">
                开始推理
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card>
          <template #header>结果 ({{ detections.length }} 个检测)</template>
          <div class="result-area">
            <canvas ref="canvasRef" class="result-canvas" />
            <p v-if="!imageLoaded" class="empty-hint">上传图片并推理后查看结果</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { getModels } from '@/api/model'
import { uploadImage } from '@/api/upload'
import { runInference as runInferenceApi } from '@/api/inference'

interface ModelItem { id: string; name: string }
interface Detection {
  bbox: number[]
  confidence: number
  class_id: number
  class_name: string
}

const models = ref<ModelItem[]>([])
const selectedModel = ref('')
const fileName = ref('')
const loading = ref(false)
const detections = ref<Detection[]>([])
const canvasRef = ref<HTMLCanvasElement | null>(null)
const imageLoaded = ref(false)

let uploadedFile: File | null = null

onMounted(async () => {
  const res = await getModels()
  models.value = res as unknown as ModelItem[]
})

function handleFileChange(file: { raw: File; name: string }) {
  uploadedFile = file.raw
  fileName.value = file.name
}

async function runInference() {
  if (!selectedModel.value || !uploadedFile) return

  loading.value = true
  try {
    const uploadRes = await uploadImage(uploadedFile) as unknown as { file_path: string }
    const res = await runInferenceApi({
      model_id: selectedModel.value,
      image_path: uploadRes.file_path,
    }) as unknown as Detection[]

    detections.value = res
    await nextTick()
    drawDetections()
  } finally {
    loading.value = false
  }
}

function drawDetections() {
  if (!canvasRef.value || !uploadedFile) return
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const img = new Image()
  img.onload = () => {
    canvas.width = img.width
    canvas.height = img.height
    ctx.drawImage(img, 0, 0)
    imageLoaded.value = true

    for (const det of detections.value) {
      const [x1, y1, x2, y2] = det.bbox
      ctx.strokeStyle = '#00ff00'
      ctx.lineWidth = 2
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1)

      ctx.fillStyle = '#00ff00'
      ctx.font = '14px sans-serif'
      ctx.fillText(`${det.class_name} ${(det.confidence * 100).toFixed(0)}%`, x1, y1 - 4)
    }
  }
  img.src = URL.createObjectURL(uploadedFile)
}
</script>

<style scoped>
.page-header {
  margin-bottom: 16px;
}
.result-area {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.result-canvas {
  max-width: 100%;
  max-height: 500px;
}
.empty-hint {
  color: #999;
}
.file-name {
  margin-left: 8px;
  color: #666;
  font-size: 12px;
}
</style>
