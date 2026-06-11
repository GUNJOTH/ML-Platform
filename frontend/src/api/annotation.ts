import request from './request'
import type { Annotation } from '@/types/annotation'

export function getAnnotations(imageId: string) {
  return request.get<never, Annotation[]>(`/images/${imageId}/annotations`)
}

export function createAnnotation(data: {
  image_id: string
  label_id: string
  annotation_type?: string
  data: Record<string, number>
}) {
  return request.post<never, Annotation>('/annotations', data)
}

export function updateAnnotation(id: string, data: Partial<Annotation>) {
  return request.put<never, Annotation>(`/annotations/${id}`, data)
}

export function deleteAnnotation(id: string) {
  return request.delete(`/annotations/${id}`)
}
