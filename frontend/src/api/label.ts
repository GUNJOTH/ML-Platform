import request from './request'
import type { Label } from '@/types/label'

export function getDatasetLabels(datasetId: string) {
  return request.get<never, Label[]>(`/datasets/${datasetId}/labels`)
}

export function createLabel(data: { dataset_id: string; name: string; color?: string }) {
  return request.post<never, Label>('/labels', data)
}

export function deleteLabel(id: string) {
  return request.delete(`/labels/${id}`)
}
