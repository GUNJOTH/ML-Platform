import request from './request'
import type { Label } from '@/types/label'

export function getDatasetLabels(datasetId: string) {
  return request.get<never, Label[]>(`/datasets/${datasetId}/labels`)
}

export function createDatasetLabel(
  datasetId: string,
  data: { name: string; color?: string; sort_order?: number }
) {
  return request.post<never, Label>(`/datasets/${datasetId}/labels`, data)
}

export function deleteLabel(id: string) {
  return request.delete(`/labels/${id}`)
}
