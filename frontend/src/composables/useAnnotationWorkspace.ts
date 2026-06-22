import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getDatasets, getDatasetImages, imageFileUrl } from '@/api/dataset'
import { getDatasetLabels } from '@/api/label'
import type { BBox } from '@/composables/useCanvas'
import { useAnnotationDraftStore } from '@/stores/annotationDraft'
import type {
  AnnotationViewData,
  DraftStore,
  WorkspaceDatasetOption,
  WorkspaceImageItem,
  WorkspaceImageListItem,
  WorkspaceLabelItem,
} from '@/types/annotation-workspace'

function boxesToAnnotations(boxes: BBox[]): AnnotationViewData[] {
  return boxes.map((box) => ({
    id: box.id,
    label_id: box.labelId,
    label_name: box.labelName,
    color: box.color,
    bbox: { x: box.x, y: box.y, width: box.width, height: box.height },
  }))
}

export function useAnnotationWorkspace(datasetId: { value: string }) {
  const draftStoreApi = useAnnotationDraftStore()

  const datasetOptions = ref<WorkspaceDatasetOption[]>([])
  const images = ref<WorkspaceImageItem[]>([])
  const labels = ref<WorkspaceLabelItem[]>([])
  const selectedImageId = ref('')
  const currentImageSrc = ref<string | null>(null)
  const currentAnnotations = ref<AnnotationViewData[]>([])
  const currentLabel = ref<WorkspaceLabelItem | null>(null)

  const draftStore = computed<DraftStore>(() => {
    const entries = Object.entries(draftStoreApi.datasetDrafts(datasetId.value))
    return new Map(entries)
  })

  const annotatedCount = computed(() =>
    [...draftStore.value.values()].filter((boxes) => boxes.length > 0).length,
  )

  const totalBoxCount = computed(() => {
    let total = 0
    for (const boxes of draftStore.value.values()) {
      total += boxes.length
    }
    return total
  })

  const imagesWithStatus = computed<WorkspaceImageListItem[]>(() =>
    images.value.map((image) => ({
      ...image,
      draft_status:
        draftStoreApi.getImageDraft(datasetId.value, image.id).length > 0
          ? 'annotated'
          : 'unannotated',
    })),
  )

  const selectedImageIndex = computed(() =>
    imagesWithStatus.value.findIndex((image) => image.id === selectedImageId.value),
  )

  const hasPreviousImage = computed(() => selectedImageIndex.value > 0)
  const hasNextImage = computed(
    () =>
      selectedImageIndex.value >= 0
      && selectedImageIndex.value < imagesWithStatus.value.length - 1,
  )

  async function loadDatasetOptions() {
    try {
      datasetOptions.value = await getDatasets()
    } catch {
      datasetOptions.value = []
    }
  }

  async function loadData() {
    try {
      const [imageList, labelList] = await Promise.all([
        getDatasetImages(datasetId.value),
        getDatasetLabels(datasetId.value),
      ])
      images.value = imageList
      labels.value = labelList
      if (labels.value.length > 0) {
        currentLabel.value = labels.value[0]
      }
      restoreSelection()
    } catch {
      images.value = []
      labels.value = []
    }
  }

  function restoreSelection() {
    if (!images.value.length) {
      selectedImageId.value = ''
      currentImageSrc.value = null
      currentAnnotations.value = []
      return
    }

    const active =
      images.value.find((image) => image.id === selectedImageId.value)
      ?? findFirstAnnotatedImage()
      ?? images.value[0]
    handleSelectImage(active)
  }

  function findFirstAnnotatedImage(): WorkspaceImageItem | undefined {
    return images.value.find(
      (image) => draftStoreApi.getImageDraft(datasetId.value, image.id).length > 0,
    )
  }

  function handleSelectImage(image: WorkspaceImageItem) {
    selectedImageId.value = image.id
    currentImageSrc.value = imageFileUrl(image.id)
    currentAnnotations.value = boxesToAnnotations(
      draftStoreApi.getImageDraft(datasetId.value, image.id),
    )
  }

  function handleSelectLabel(label: WorkspaceLabelItem) {
    currentLabel.value = label
  }

  function handleTempSave(boxes: BBox[]) {
    if (!selectedImageId.value) {
      return
    }
    draftStoreApi.setImageDraft(datasetId.value, selectedImageId.value, [...boxes])
    currentAnnotations.value = boxesToAnnotations(boxes)
    ElMessage.success('已保存当前图片草稿')
  }

  function handleDeleteAnnotation(annotationId: string) {
    currentAnnotations.value = currentAnnotations.value.filter(
      (item) => item.id !== annotationId,
    )
  }

  function goPreviousImage() {
    if (!hasPreviousImage.value) {
      return
    }
    const prev = imagesWithStatus.value[selectedImageIndex.value - 1]
    if (prev) {
      handleSelectImage(prev)
    }
  }

  function goNextImage() {
    if (!hasNextImage.value) {
      return
    }
    const next = imagesWithStatus.value[selectedImageIndex.value + 1]
    if (next) {
      handleSelectImage(next)
    }
  }

  function goNextUnannotatedImage() {
    const nextImage = imagesWithStatus.value.find(
      (image) => image.draft_status === 'unannotated',
    )
    if (nextImage) {
      handleSelectImage(nextImage)
      return
    }
    ElMessage.info('当前数据集草稿都已经标过了')
  }

  function clearDatasetDraft() {
    draftStoreApi.clearDatasetDraft(datasetId.value)
  }

  return {
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
  }
}
