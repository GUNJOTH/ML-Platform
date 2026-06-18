<template>
  <div class="annotation-workspace">
    <div v-if="!datasetId" class="dataset-selector">
      <el-card>
        <template #header>选择数据集进行标注</template>
        <el-select v-model="selectedDatasetId" placeholder="请选择数据集" style="width: 300px">
          <el-option v-for="ds in datasetOptions" :key="ds.id" :label="ds.name" :value="ds.id" />
        </el-select>
        <el-button type="primary" style="margin-left: 12px" @click="enterWorkspace">
          进入标注
        </el-button>
      </el-card>
    </div>

    <template v-else>
      <div class="workspace-left">
        <el-select v-model="datasetId" size="small" @change="onDatasetChange">
          <el-option v-for="ds in datasetOptions" :key="ds.id" :label="ds.name" :value="ds.id" />
        </el-select>
        <div class="progress-info">{{ annotatedCount }}/{{ images.length }} 已标注</div>
        <ImageList :images="images" :selected-id="selectedImageId" @select="handleSelectImage" />
      </div>

      <div class="workspace-center">
        <ImageCanvas
          :image-src="currentImageSrc"
          :annotations="currentAnnotations"
          :current-label="currentLabel"
          @save="handleTempSave"
          @delete="() => {}"
        />
        <div class="center-footer">
          <el-button type="success" size="large" @click="showExport = true">导出数据集</el-button>
        </div>
      </div>

      <div class="workspace-right">
        <LabelPanel
          :labels="labels"
          :selected-label-id="currentLabel?.id || ''"
          @select="handleSelectLabel"
        />
      </div>
    </template>

    <ExportDialog
      v-model:visible="showExport"
      :dataset-id="datasetId"
      :draft-store="draftStore"
      :annotated-count="annotatedCount"
      :total-box-count="totalBoxCount"
      @exported="onExported"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getDatasets, getDatasetImages, imageFileUrl } from '@/api/dataset'
import { getDatasetLabels } from '@/api/label'
import ImageList from './components/ImageList.vue'
import ImageCanvas from './components/ImageCanvas.vue'
import LabelPanel from './components/LabelPanel.vue'
import ExportDialog from './components/ExportDialog.vue'
import type { BBox } from '@/composables/useCanvas'

interface ImageItem { id: string; filename: string; file_path: string }
interface LabelItem { id: string; name: string; color: string }
interface DatasetOption { id: string; name: string }
interface AnnotationData {
  label_id: string
  label_name: string
  color: string
  bbox: { x: number; y: number; width: number; height: number }
}

const route = useRoute()
const router = useRouter()
const datasetId = ref(route.params.datasetId as string || '')
const selectedDatasetId = ref('')
const showExport = ref(false)

const datasetOptions = ref<DatasetOption[]>([])
const images = ref<ImageItem[]>([])
const labels = ref<LabelItem[]>([])
const selectedImageId = ref('')
const currentImageSrc = ref<string | null>(null)
const currentAnnotations = ref<AnnotationData[]>([])
const currentLabel = ref<LabelItem | null>(null)
const draftStore = ref<Map<string, BBox[]>>(new Map())

const annotatedCount = computed(() =>
  [...draftStore.value.values()].filter((b) => b.length > 0).length
)
const totalBoxCount = computed(() => {
  let n = 0
  for (const boxes of draftStore.value.values()) n += boxes.length
  return n
})

onMounted(async () => {
  try {
    datasetOptions.value = (await getDatasets()) as unknown as DatasetOption[]
  } catch { datasetOptions.value = [] }
  if (datasetId.value) await loadData()
})

function enterWorkspace() {
  if (!selectedDatasetId.value) return
  datasetId.value = selectedDatasetId.value
  router.push(`/annotation/workspace/${datasetId.value}`)
  loadData()
}

function onDatasetChange() {
  draftStore.value.clear()
  router.push(`/annotation/workspace/${datasetId.value}`)
  loadData()
}

async function loadData() {
  try {
    const [imgs, lbls] = await Promise.all([
      getDatasetImages(datasetId.value),
      getDatasetLabels(datasetId.value),
    ])
    images.value = (imgs || []) as unknown as ImageItem[]
    labels.value = (lbls || []) as unknown as LabelItem[]
    if (labels.value.length > 0) currentLabel.value = labels.value[0]
  } catch { images.value = []; labels.value = [] }
}

function handleSelectImage(image: ImageItem) {
  selectedImageId.value = image.id
  currentImageSrc.value = imageFileUrl(image.id)
  const saved = draftStore.value.get(image.id)
  currentAnnotations.value = saved ? saved.map(boxToAnnotation) : []
}

function handleSelectLabel(label: LabelItem) { currentLabel.value = label }

function handleTempSave(boxes: BBox[]) {
  if (!selectedImageId.value) return
  draftStore.value.set(selectedImageId.value, [...boxes])
  ElMessage.success('已暂存')
}

function onExported() { showExport.value = false }

function boxToAnnotation(box: BBox): AnnotationData {
  return {
    label_id: box.labelId,
    label_name: box.labelName,
    color: box.color,
    bbox: { x: box.x, y: box.y, width: box.width, height: box.height },
  }
}
</script>

<style scoped>
.annotation-workspace { display: flex; height: calc(100vh - 120px); gap: 8px; }
.dataset-selector { width: 100%; display: flex; align-items: center; justify-content: center; padding-top: 100px; }
.workspace-left { width: 200px; background: #fff; border-radius: 4px; overflow-y: auto; padding: 8px; display: flex; flex-direction: column; gap: 8px; }
.progress-info { font-size: 12px; color: #666; padding: 4px 0; border-bottom: 1px solid #eee; }
.workspace-center { flex: 1; background: #2c2c2c; border-radius: 4px; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 12px; gap: 12px; }
.center-footer { flex-shrink: 0; }
.workspace-right { width: 240px; background: #fff; border-radius: 4px; padding: 12px; overflow-y: auto; }
</style>
