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
