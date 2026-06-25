export interface Task {
  id: string
  name: string
  task_type: string
  status: string
  model_id: string | null
  dataset_id: string | null
  dataset_version_id: string | null
  dataset_export_id: string | null
  config: Record<string, unknown> | null
  progress: number
  result: Record<string, unknown> | null
  error_message: string | null
  started_at: string | null
  finished_at: string | null
  created_at: string
  updated_at: string
}

export interface TaskArtifactItem {
  key: string
  filename: string
  url: string
}

export interface TaskHistoryPoint {
  epoch: number
  train_loss?: number
  map50?: number
  map50_95?: number
}

export interface TrainingDetailContext {
  datasetName: string
  modelName: string
  modelVersion: string
  versionName: string
  exportName: string
  exportFormat: string
  dataYamlPath: string
  exportCreatedAt: string
  exportNotes: string
  splitSummary: string
  classCount: number
  classNames: string[]
  imageCount: number
  boxCount: number
  splitCounts: Record<string, number>
}
