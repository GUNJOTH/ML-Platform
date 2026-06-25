import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { BBox } from '@/composables/useCanvas'

type DraftDatasetMap = Record<string, Record<string, BBox[]>>

const STORAGE_KEY = 'annotation-draft-store'

function isBBox(value: unknown): value is BBox {
  if (!value || typeof value !== 'object') {
    return false
  }
  const row = value as Record<string, unknown>
  return typeof row.id === 'string'
    && typeof row.x === 'number'
    && typeof row.y === 'number'
    && typeof row.width === 'number'
    && typeof row.height === 'number'
    && typeof row.labelId === 'string'
    && typeof row.labelName === 'string'
    && typeof row.color === 'string'
}

function normalizeDraftStore(raw: unknown): DraftDatasetMap {
  if (!raw || typeof raw !== 'object') {
    return {}
  }
  const source = raw as Record<string, unknown>
  const next: DraftDatasetMap = {}
  for (const [datasetId, datasetValue] of Object.entries(source)) {
    if (!datasetValue || typeof datasetValue !== 'object') {
      continue
    }
    const images = datasetValue as Record<string, unknown>
    next[datasetId] = {}
    for (const [imageId, boxesValue] of Object.entries(images)) {
      if (!Array.isArray(boxesValue)) {
        continue
      }
      next[datasetId][imageId] = boxesValue.filter(isBBox)
    }
  }
  return next
}

function loadFromStorage(): DraftDatasetMap {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) {
    return {}
  }
  try {
    return normalizeDraftStore(JSON.parse(raw))
  } catch {
    return {}
  }
}

export const useAnnotationDraftStore = defineStore('annotationDraft', () => {
  const drafts = ref<DraftDatasetMap>(loadFromStorage())

  const datasetDrafts = computed(() => (datasetId: string) => drafts.value[datasetId] || {})

  function persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts.value))
  }

  function setImageDraft(datasetId: string, imageId: string, boxes: BBox[]) {
    drafts.value = {
      ...drafts.value,
      [datasetId]: {
        ...(drafts.value[datasetId] || {}),
        [imageId]: boxes.map((box) => ({ ...box })),
      },
    }
    persist()
  }

  function getImageDraft(datasetId: string, imageId: string): BBox[] {
    return drafts.value[datasetId]?.[imageId] || []
  }

  function hasImageDraft(datasetId: string, imageId: string): boolean {
    return Object.prototype.hasOwnProperty.call(drafts.value[datasetId] || {}, imageId)
  }

  function clearDatasetDraft(datasetId: string) {
    const next = { ...drafts.value }
    delete next[datasetId]
    drafts.value = next
    persist()
  }

  function clearImageDraft(datasetId: string, imageId: string) {
    if (!drafts.value[datasetId]) {
      return
    }
    const datasetDraft = { ...drafts.value[datasetId] }
    delete datasetDraft[imageId]

    if (!Object.keys(datasetDraft).length) {
      const next = { ...drafts.value }
      delete next[datasetId]
      drafts.value = next
    } else {
      drafts.value = {
        ...drafts.value,
        [datasetId]: datasetDraft,
      }
    }
    persist()
  }

  function listDraftImageIds(datasetId: string): string[] {
    return Object.entries(drafts.value[datasetId] || {})
      .filter(([, boxes]) => boxes.length > 0)
      .map(([imageId]) => imageId)
  }

  return {
    datasetDrafts,
    setImageDraft,
    getImageDraft,
    hasImageDraft,
    clearDatasetDraft,
    clearImageDraft,
    listDraftImageIds,
  }
})
