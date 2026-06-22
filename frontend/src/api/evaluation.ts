import request from './request'
import type { EvaluationRequest } from '@/types/evaluation'
import type { Task } from '@/types/task'

export function runEvaluation(data: EvaluationRequest) {
  return request.post<never, Task>('/evaluation/run', data)
}
