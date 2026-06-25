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

        <div v-if="datasetDetail" class="dataset-summary">
          <div class="summary-row">
            <span>类别来源</span>
            <span>{{ labelSourceText }}</span>
          </div>
          <div class="summary-row">
            <span>数据划分</span>
            <span>{{ splitSummaryText }}</span>
          </div>
        </div>

        <div class="image-actions">
          <el-button size="small" @click="goPreviousImage" :disabled="!hasPreviousImage">
            上一张
          </el-button>
          <el-button size="small" @click="goNextImage" :disabled="!hasNextImage">
            下一张
          </el-button>
          <el-button size="small" type="primary" plain @click="goNextUnannotatedImage">
            跳到未标注
          </el-button>
        </div>

        <ImageList
          :images="imagesWithStatus"
          :selected-id="selectedImageId"
          @select="handleImageSelect"
          @delete="handleImageDelete"
        />
      </div>

      <div class="workspace-center">
        <ImageCanvas
          ref="imageCanvasRef"
          :image-src="currentImageSrc"
          :annotations="currentAnnotations"
          :current-label="currentLabel"
          :can-draw="labels.length > 0 && !!currentLabel"
          @save="handleTempSave"
          @delete="handleDeleteAnnotation"
        />
        <div class="center-footer">
          <el-button type="success" size="large" :disabled="labels.length === 0" @click="handleOpenExport">
            导出数据集
          </el-button>
        </div>
      </div>

      <div class="workspace-right">
        <LabelPanel
          :labels="labels"
          :selected-label-id="currentLabel?.id || ''"
          :can-create="!!datasetId"
          @select="handleLabelSelect"
          @create="handleCreateLabel"
          @delete="handleDeleteLabel"
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
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { createDatasetLabel, deleteLabel } from '@/api/label'
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
  datasetDetail,
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
  removeImage,
} = useAnnotationWorkspace(datasetId)

const labelSourceText = computed(() => {
  if (!datasetDetail.value) {
    return '--'
  }
  if (labels.value.length > 0) {
    return datasetDetail.value.num_classes > 0 ? '沿用当前数据集类别' : '当前工作台新建类别'
  }
  return '当前数据集暂无类别，需先创建'
})

const splitSummaryText = computed(() => {
  if (!datasetDetail.value) {
    return '--'
  }

  const { train_count, val_count, test_count } = datasetDetail.value
  const entries = [
    train_count > 0 ? `train ${train_count}` : '',
    val_count > 0 ? `val ${val_count}` : '',
    test_count > 0 ? `test ${test_count}` : '',
  ].filter(Boolean)

  return entries.length ? entries.join(' / ') : '原数据集未明确划分'
})

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
  imageCanvasRef.value?.drawMode()
}

function handleLabelSelect(label: WorkspaceLabelItem) {
  handleSelectLabel(label)
  imageCanvasRef.value?.updateSelectedLabel(label.id, label.name, label.color)
}

async function handleCreateLabel(payload: { name: string; color: string }) {
  if (!datasetId.value) {
    return
  }
  await createDatasetLabel(datasetId.value, {
    name: payload.name,
    color: payload.color,
    sort_order: labels.value.length,
  })
  await loadData()
  if (labels.value.length > 0) {
    const latest = labels.value[labels.value.length - 1]
    handleLabelSelect(latest)
  }
  ElMessage.success('类别已创建')
}

async function handleDeleteLabel(label: WorkspaceLabelItem) {
  try {
    await ElMessageBox.confirm(
      `确定删除类别 ${label.name} 吗？该类别下已有标注也会失效。`,
      '确认删除',
      { type: 'warning' },
    )
    await deleteLabel(label.id)
    await loadData()

    if (labels.value.length > 0) {
      const nextLabel = labels.value.find((item) => item.id !== label.id) || labels.value[0]
      if (nextLabel) {
        handleLabelSelect(nextLabel)
      }
    }

    ElMessage.success('类别已删除')
  } catch {
    // 用户取消
  }
}

async function handleImageDelete(image: WorkspaceImageItem) {
  try {
    await ElMessageBox.confirm(
      `确定删除图片 ${image.filename} 吗？这会同时删除该图片的标注。`,
      '确认删除',
      { type: 'warning' },
    )
    await removeImage(image.id)
    ElMessage.success('图片已删除')
  } catch {
    // 用户取消
  }
}

function handleOpenExport() {
  if (labels.value.length === 0) {
    ElMessage.warning('请先创建类别并完成标注，再导出数据集')
    return
  }
  showExport.value = true
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
  width: 280px;
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

.dataset-summary {
  padding: 8px;
  border-radius: 6px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
  color: #475569;
}

.summary-row + .summary-row {
  margin-top: 6px;
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
  width: 280px;
  background: #fff;
  border-radius: 4px;
  padding: 12px;
  overflow-y: auto;
}
</style>
