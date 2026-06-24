export type DatasetExportStatus = 'success' | 'exporting' | 'failed' | 'pending'

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

export interface DatasetVersionCreatePayload {
  dataset_id: string
  version_name: string
  description?: string
  source_type: 'annotation-export' | 'imported' | 'manual-freeze'
  export_format: 'yolo'
  include_splits: string[]
  split_strategy: string
  split_config?: Record<string, unknown>
}

export interface DatasetVersionValidationIssue {
  code: string
  message: string
  level: string
}

export interface DatasetExportRecordDetail {
  id: string
  dataset_id: string
  dataset_version_id: string
  export_name: string
  export_format: string
  status: DatasetExportStatus
  split_config: Record<string, unknown> | null
  output_path: string | null
  data_yaml_path: string | null
  manifest_path: string | null
  validation_summary: {
    passed: boolean
    errors: DatasetVersionValidationIssue[]
    warnings: DatasetVersionValidationIssue[]
    summary: Record<string, unknown>
  } | null
  error_message: string | null
  finished_at: string | null
  created_at: string
  updated_at: string
}

export interface DatasetVersionValidationResult {
  passed: boolean
  errors: DatasetVersionValidationIssue[]
  warnings: DatasetVersionValidationIssue[]
  summary: Record<string, unknown>
}

export interface DatasetVersionApiRecord {
  id: string
  dataset_id: string
  version_name: string
  version_code: string
  description: string | null
  status: string
  source_type: string
  export_format: string
  include_splits: string[] | null
  split_strategy: string | null
  split_config: Record<string, unknown> | null
  label_schema_snapshot: Array<Record<string, unknown>> | null
  stats_snapshot: Record<string, unknown> | null
  validation_summary: {
    passed: boolean
    errors: DatasetVersionValidationIssue[]
    warnings: DatasetVersionValidationIssue[]
    summary: Record<string, unknown>
  } | null
  frozen_at: string | null
  created_at: string
  updated_at: string
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
