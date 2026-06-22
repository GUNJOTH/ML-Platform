export interface DatasetVersionSummary {
  id: string
  datasetId: string
  datasetName: string
  versionName: string
  source: 'annotation-export' | 'imported' | 'manual-freeze'
  imageCount: number
  annotationCount: number
  classCount: number
  splitSummary: string
  exportFormat: string
  status: 'ready' | 'draft' | 'archived'
  createdBy: string
  createdAt: string
  notes: string
  splitDetail?: Array<{ split: string; images: number; annotations: number }>
  classDistribution?: Array<{ className: string; count: number; ratio: string }>
  validationHints?: string[]
}

export interface DatasetExportRecord {
  id: string
  datasetId: string
  datasetName: string
  versionName: string
  exportName: string
  exportFormat: 'yolo' | 'coco' | 'voc'
  exportScope: string
  status: 'completed' | 'processing' | 'failed'
  outputPath: string
  createdBy: string
  createdAt: string
  notes?: string
  includedAssets?: string[]
  validationSummary?: string[]
}

export interface DatasetVersionPlanItem {
  title: string
  description: string
}

export interface DatasetVersionOverviewCard {
  label: string
  value: string | number
  help: string
}

export interface ExportDraft {
  exportName: string
  exportFormat: 'yolo' | 'coco' | 'voc'
  splits: string[]
  extras: string[]
  outputPath: string
  notes: string
}
