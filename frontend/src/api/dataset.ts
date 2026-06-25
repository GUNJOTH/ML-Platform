import request from './request'
import type { Dataset, DatasetImage } from '@/types/dataset'

export function getDatasets(params?: { page?: number; page_size?: number }) {
  return request.get<never, Dataset[]>('/datasets', { params })
}

export function getDataset(id: string) {
  return request.get<never, Dataset>(`/datasets/${id}`)
}

export function createDataset(data: { name: string; description?: string; data_type?: string }) {
  return request.post<never, Dataset>('/datasets', data)
}

export function updateDataset(id: string, data: Partial<Dataset>) {
  return request.put<never, Dataset>(`/datasets/${id}`, data)
}

export function deleteDataset(id: string) {
  return request.delete(`/datasets/${id}`)
}

export function getDatasetImages(
  id: string,
  params?: { page?: number; page_size?: number }
) {
  return request.get<never, DatasetImage[]>(`/datasets/${id}/images`, { params })
}

export function deleteDatasetImage(imageId: string) {
  return request.delete(`/datasets/images/${imageId}`)
}

export function imageFileUrl(imageId: string): string {
  return `/api/v1/datasets/images/${imageId}/file`
}

export function exportAnnotated(
  id: string,
  payload: { annotations: Record<string, unknown[]>; mode: 'new' | 'overwrite' }
) {
  return request.post<never, Dataset>(`/datasets/${id}/export-annotated`, payload)
}
