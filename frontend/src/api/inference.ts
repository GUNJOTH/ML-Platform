import request from './request'

export function runInference(data: {
  model_id: string
  confidence?: number
  iou_threshold?: number
}) {
  return request.post('/inference', data)
}

export function runEvaluation(data: {
  model_id: string
  dataset_id: string
  iou_threshold?: number
}) {
  return request.post('/evaluation', data)
}
