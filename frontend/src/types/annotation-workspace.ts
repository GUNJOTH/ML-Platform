import type { BBox } from '@/composables/useCanvas'

export interface WorkspaceImageItem {
  id: string
  filename: string
  file_path: string
  split?: string
  annotation_status?: string
}

export interface WorkspaceImageListItem extends WorkspaceImageItem {
  draft_status: 'unannotated' | 'annotated'
}

export interface WorkspaceLabelItem {
  id: string
  name: string
  color: string
}

export interface WorkspaceDatasetOption {
  id: string
  name: string
}

export interface AnnotationViewData {
  id: string
  label_id: string
  label_name: string
  color: string
  bbox: { x: number; y: number; width: number; height: number }
}

export type DraftStore = Map<string, BBox[]>

export interface ImageCanvasExpose {
  updateSelectedLabel: (labelId: string, labelName: string, color: string) => void
  selectMode: () => void
  drawMode: () => void
}
