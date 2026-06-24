import request from './request'
import type {
  DatasetVersionSummary,
  DatasetExportRecordDetail,
  DatasetVersionApiRecord,
  DatasetVersionCreatePayload,
  DatasetVersionValidationResult,
} from '@/types/dataset-version'

export function getDatasetVersions(params?: {
  page?: number
  page_size?: number
  dataset_id?: string
}) {
  return request.get<never, DatasetVersionApiRecord[]>('/dataset-versions', { params })
}

export function getDatasetVersion(id: string) {
  return request.get<never, DatasetVersionApiRecord>(`/dataset-versions/${id}`)
}

export function deleteDatasetVersion(id: string) {
  return request.delete<never, void>(`/dataset-versions/${id}`)
}

export function createDatasetVersion(data: DatasetVersionCreatePayload) {
  return request.post<never, DatasetVersionSummary>('/dataset-versions', data)
}

export function validateDatasetVersionDraft(data: DatasetVersionCreatePayload) {
  return request.post<never, DatasetVersionValidationResult>('/dataset-versions/validate-draft', data)
}

export function validateDatasetVersion(id: string) {
  return request.post<never, DatasetVersionValidationResult>(`/dataset-versions/${id}/validate`)
}

export function getDatasetExports(params?: {
  page?: number
  page_size?: number
  dataset_id?: string
  dataset_version_id?: string
}) {
  return request.get<never, DatasetExportRecordDetail[]>('/dataset-exports', { params })
}

export function getDatasetExport(id: string) {
  return request.get<never, DatasetExportRecordDetail>(`/dataset-exports/${id}`)
}

export function deleteDatasetExport(id: string) {
  return request.delete<never, void>(`/dataset-exports/${id}`)
}

export function createDatasetExport(
  versionId: string,
  data: {
    dataset_version_id: string
    export_name: string
    export_format: string
    splits: string[]
    extras: string[]
    notes?: string
  },
) {
  return request.post<never, DatasetExportRecordDetail>(`/dataset-versions/${versionId}/exports`, data)
}
