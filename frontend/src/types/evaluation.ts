export interface EvaluationRequest {
  model_id: string
  dataset_id: string
}

export interface EvaluationSpeed {
  preprocess: number
  inference: number
  loss: number
  postprocess: number
  total: number
}

export interface EvaluationDatasetSummary {
  images: number
  instances: number
  classes: number
}

export interface EvaluationConfig {
  split?: string
}

export interface PerClassMetric {
  class_id: number
  class_name: string
  image_count: number
  precision: number
  recall: number
  f1: number
  map50: number
  map50_95: number
}

export interface EvaluationReport {
  map50: number
  map75?: number
  map50_95: number
  precision: number
  recall: number
  f1?: number
  fitness?: number
  speed_ms?: EvaluationSpeed
  dataset_summary?: EvaluationDatasetSummary
  evaluation_config?: EvaluationConfig
  per_class?: PerClassMetric[]
}

function toNumber(value: unknown): number {
  return Number(value ?? 0)
}

function computeF1(precision: number, recall: number): number {
  if (precision + recall === 0) {
    return 0
  }
  return (2 * precision * recall) / (precision + recall)
}

function normalizeSpeed(value: unknown): EvaluationSpeed | undefined {
  if (!value || typeof value !== 'object') {
    return undefined
  }
  const speed = value as Record<string, unknown>
  return {
    preprocess: toNumber(speed.preprocess),
    inference: toNumber(speed.inference),
    loss: toNumber(speed.loss),
    postprocess: toNumber(speed.postprocess),
    total: toNumber(speed.total),
  }
}

function normalizeDatasetSummary(value: unknown): EvaluationDatasetSummary | undefined {
  if (!value || typeof value !== 'object') {
    return undefined
  }
  const summary = value as Record<string, unknown>
  return {
    images: toNumber(summary.images),
    instances: toNumber(summary.instances),
    classes: toNumber(summary.classes),
  }
}

function normalizeConfig(value: unknown): EvaluationConfig | undefined {
  if (!value || typeof value !== 'object') {
    return undefined
  }
  const config = value as Record<string, unknown>
  return {
    split: typeof config.split === 'string' ? config.split : 'val',
  }
}

function normalizePerClass(value: unknown): PerClassMetric[] {
  if (!Array.isArray(value)) {
    return []
  }
  return value.map((item) => {
    const row = item as Record<string, unknown>
    return {
      class_id: toNumber(row.class_id),
      class_name: String(row.class_name ?? row.class_id ?? ''),
      image_count: toNumber(row.image_count),
      precision: toNumber(row.precision),
      recall: toNumber(row.recall),
      f1: toNumber(row.f1),
      map50: toNumber(row.map50),
      map50_95: toNumber(row.map50_95),
    }
  })
}

export function normalizeEvaluationReport(result: Record<string, unknown>): EvaluationReport {
  const precision = toNumber(result.precision)
  const recall = toNumber(result.recall)
  return {
    map50: toNumber(result.map50),
    map75: toNumber(result.map75 ?? result.map50_95),
    map50_95: toNumber(result.map50_95),
    precision,
    recall,
    f1: toNumber(result.f1 ?? computeF1(precision, recall)),
    fitness: toNumber(result.fitness),
    speed_ms: normalizeSpeed(result.speed_ms),
    dataset_summary: normalizeDatasetSummary(result.dataset_summary),
    evaluation_config: normalizeConfig(result.evaluation_config),
    per_class: normalizePerClass(result.per_class),
  }
}

export function formatPercent(value: number | undefined): string {
  if (value === undefined || Number.isNaN(value)) {
    return '--'
  }
  return `${(value * 100).toFixed(1)}%`
}

export function formatMs(value: number | undefined): string {
  if (value === undefined || Number.isNaN(value)) {
    return '--'
  }
  return value.toFixed(1)
}
