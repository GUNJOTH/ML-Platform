<template>
  <div class="annotation-workspace">
    <div v-if="!datasetId" class="dataset-selector">
      <el-card>
        <template #header>选择数据集进入标注</template>
        <el-select v-model="selectedDatasetId" placeholder="请选择数据集" style="width: 300px">
          <el-option
            v-for="dataset in datasetOptions"
            :key="dataset.id"
            :label="dataset.name"
            :value="dataset.id"
          />
        </el-select>
        <el-button type="primary" style="margin-left: 12px" @click="enterWorkspace">
          进入标注
        </el-button>
      </el-card>
    </div>

    <template v-else>
      <div class="workspace-left">
        <el-select v-model="datasetId" size="small" @change="onDatasetChange">
          <el-option
            v-for="dataset in datasetOptions"
            :key="dataset.id"
            :label="dataset.name"
            :value="dataset.id"
          />
        </el-select>
        <div class="progress-info">
          已标注 {{ annotatedCount }}/{{ images.length }}，标注框 {{ totalBoxCount }}
        </div>
        <div class="image-actions">
          <el-button size="small" @click="goPreviousImage" :disabled="!hasPreviousImage">
            上一张
          </el-button>
          <el-button size="small" @click="goNextImage" :disabled="!hasNextImage">
            下一张
          </el-button>
          <el-button size="small" type="primary" plain @click="goNextUnannotatedImage">
            跳到未标图
          </el-button>
        </div>
        <ImageList
          :images="imagesWithStatus"
          :selected-id="selectedImageId"
          @select="handleImageSelect"
        />
      </div>

      <div class="workspace-center">
        <ImageCanvas
          ref="imageCanvasRef"
          :image-src="currentImageSrc"
          :annotations="currentAnnotations"
          :current-label="currentLabel"
          @save="handleTempSave"
          @delete="handleDeleteAnnotation"
        />
        <div class="center-footer">
          <el-button type="success" size="large" @click="showExport = true">导出数据集</el-button>
        </div>
      </div>

      <div class="workspace-right">
        <LabelPanel
          :labels="labels"
          :selected-label-id="currentLabel?.id || ''"
          @select="handleLabelSelect"
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
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAnnotationWorkspace } from '@/composables/useAnnotationWorkspace'
import type {
  ImageCanvasExpose,
  WorkspaceImageItem,
  WorkspaceLabelItem,
} from '@/types/annotation-workspace'
import ExportDialog from './components/ExportDialog.vue'
import ImageCanvas from './components/ImageCanvas.vue'
import ImageList from './components/ImageList.vue'
import LabelPanel from './components/LabelPanel.vue'

const route = useRoute()
const router = useRouter()

const datasetId = ref(typeof route.params.datasetId === 'string' ? route.params.datasetId : '')
const selectedDatasetId = ref('')
const showExport = ref(false)
const imageCanvasRef = ref<ImageCanvasExpose | null>(null)

const {
  datasetOptions,
  images,
  labels,
  selectedImageId,
  currentImageSrc,
  currentAnnotations,
  currentLabel,
  draftStore,
  annotatedCount,
  totalBoxCount,
  imagesWithStatus,
  hasPreviousImage,
  hasNextImage,
  loadDatasetOptions,
  loadData,
  restoreSelection,
  handleSelectImage,
  handleSelectLabel,
  handleTempSave,
  handleDeleteAnnotation,
  goPreviousImage,
  goNextImage,
  goNextUnannotatedImage,
  clearDatasetDraft,
} = useAnnotationWorkspace(datasetId)

onMounted(async () => {
  await loadDatasetOptions()
  if (datasetId.value) {
    await loadData()
  }
})

watch(
  () => route.params.datasetId,
  async (value) => {
    datasetId.value = typeof value === 'string' ? value : ''
    if (datasetId.value) {
      await loadData()
    }
  },
)

function enterWorkspace() {
  if (!selectedDatasetId.value) {
    return
  }
  datasetId.value = selectedDatasetId.value
  router.push(`/annotation/workspace/${datasetId.value}`)
}

async function onDatasetChange() {
  selectedImageId.value = ''
  currentImageSrc.value = null
  currentAnnotations.value = []
  router.push(`/annotation/workspace/${datasetId.value}`)
  await loadData()
}

function handleImageSelect(image: WorkspaceImageItem) {
  handleSelectImage(image)
  imageCanvasRef.value?.selectMode()
}

function handleLabelSelect(label: WorkspaceLabelItem) {
  handleSelectLabel(label)
  imageCanvasRef.value?.updateSelectedLabel(label.id, label.name, label.color)
}

function onExported() {
  showExport.value = false
  clearDatasetDraft()
  restoreSelection()
}
</script>

<style scoped>
.annotation-workspace {
  display: flex;
  height: calc(100vh - 120px);
  gap: 8px;
}

.dataset-selector {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 100px;
}

.workspace-left {
  width: 240px;
  background: #fff;
  border-radius: 4px;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-info {
  font-size: 12px;
  color: #666;
  padding: 4px 0;
  border-bottom: 1px solid #eee;
}

.image-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.image-actions :deep(.el-button:last-child) {
  grid-column: 1 / -1;
}

.workspace-center {
  flex: 1;
  background: #2c2c2c;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px;
  gap: 12px;
}

.center-footer {
  flex-shrink: 0;
}

.workspace-right {
  width: 240px;
  background: #fff;
  border-radius: 4px;
  padding: 12px;
  overflow-y: auto;
}
</style>
