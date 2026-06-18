import request from './request'
import type { MLModel } from '@/types/model'

export function getModels(params?: {
  page?: number
  page_size?: number
  source?: string
  dataset_id?: string
}) {
  return request.get<never, MLModel[]>('/models', { params })
}

export function getModel(id: string) {
  return request.get<never, MLModel>(`/models/${id}`)
}

export function createModel(data: {
  name: string
  version?: string
  framework?: string
  description?: string
  dataset_id?: string
}) {
  return request.post<never, MLModel>('/models', data)
}

export function updateModel(id: string, data: Partial<MLModel>) {
  return request.put<never, MLModel>(`/models/${id}`, data)
}

export function deleteModel(id: string) {
  return request.delete(`/models/${id}`)
}

export function importModel(payload: {
  name: string
  version?: string
  framework?: string
  file: File
}) {
  const fd = new FormData()
  fd.append('name', payload.name)
  if (payload.version) fd.append('version', payload.version)
  fd.append('framework', payload.framework ?? 'ultralytics')
  fd.append('file', payload.file)
  return request.post<never, MLModel>('/models/import', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function modelDownloadUrl(id: string): string {
  return `/api/v1/models/${id}/download`
}
