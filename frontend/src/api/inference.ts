import request from './request'

export interface InferenceDetection {
  label: string
  confidence: number
  bbox: { x: number; y: number; width: number; height: number }
}

export function runInference(data: { model_id: string; image_path: string }) {
  return request.post<never, InferenceDetection[]>('/inference/run', data)
}

export function runEvaluation(data: { model_id: string; dataset_id: string }) {
  return request.post('/evaluation/run', data)
}
