import request from './request'
import type { Task } from '@/types/task'
import type { TaskArtifactItem, TaskHistoryPoint, TaskLog } from '@/types/task'

export function getTasks(params?: { page?: number; page_size?: number; task_type?: string }) {
  return request.get<never, Task[]>('/tasks', { params })
}

export function getTask(id: string) {
  return request.get<never, Task>(`/tasks/${id}`)
}

export function createTask(data: {
  name: string
  task_type: string
  model_id?: string
  dataset_id?: string
  dataset_version_id?: string
  dataset_export_id?: string
  config?: Record<string, unknown>
}) {
  return request.post<never, Task>('/tasks', data)
}

export function cancelTask(id: string) {
  return request.post<never, Task>(`/tasks/${id}/cancel`)
}

export function startTask(id: string) {
  return request.post<never, Task>(`/tasks/${id}/start`)
}

export function syncTask(id: string) {
  return request.post<never, Task>(`/tasks/${id}/sync`)
}

export function deleteTask(id: string) {
  return request.delete(`/tasks/${id}`)
}

export function getTaskHistory(id: string) {
  return request.get<never, TaskHistoryPoint[]>(`/tasks/${id}/history`)
}

export function exportTaskModel(id: string) {
  return request.post(`/tasks/${id}/export-model`)
}

export function getTaskProgress(id: string) {
  return request.get<never, { task_id: string; progress: number }>(`/tasks/${id}/progress`)
}

export function getTaskArtifacts(id: string) {
  return request.get<never, { items: TaskArtifactItem[] }>(`/tasks/${id}/artifacts`)
}

export function getTaskLog(id: string, stream: 'stdout' | 'stderr') {
  return request.get<never, TaskLog>(`/tasks/${id}/logs/${stream}`)
}
