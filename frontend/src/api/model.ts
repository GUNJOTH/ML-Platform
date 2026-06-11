import request from './request'
import type { MLModel } from '@/types/model'

export function getModels(params?: { page?: number; page_size?: number }) {
  return request.get<never, MLModel[]>('/models', { params })
}

export function getModel(id: string) {
  return request.get<never, MLModel>(`/models/${id}`)
}

export function createModel(data: { name: string; version?: string; framework?: string }) {
  return request.post<never, MLModel>('/models', data)
}

export function deleteModel(id: string) {
  return request.delete(`/models/${id}`)
}
