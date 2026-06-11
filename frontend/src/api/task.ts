import request from './request'
import type { Task } from '@/types/task'

export function getTasks(params?: { page?: number; page_size?: number }) {
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
  config?: Record<string, unknown>
}) {
  return request.post<never, Task>('/tasks', data)
}

export function cancelTask(id: string) {
  return request.post<never, Task>(`/tasks/${id}/cancel`)
}
