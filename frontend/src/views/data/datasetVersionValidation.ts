import type {
  DatasetExportRecord,
  DatasetExportRecordDetail,
  DatasetExportStatus,
  DatasetVersionApiRecord,
  DatasetVersionCreatePayload,
  DatasetVersionSummary,
  DatasetVersionValidationIssue,
  DatasetVersionValidationResult,
} from '@/types/dataset-version'

export interface DatasetVersionCreateFormState {
  datasetId: string
  versionName: string
  source: 'annotation-export' | 'imported' | 'manual-freeze'
  exportFormat: 'YOLO'
  notes: string
  includeSplits: string[]
  splitStrategy: 'reuse-existing' | 'auto-ratio'
  trainRatio: number
  valRatio: number
  testRatio: number
  randomSeed: number
  scopeSplits: string[]
  includeAssets: string[]
}

export interface ValidationIssueDisplay extends DatasetVersionValidationIssue {
  title: string
}

export interface SplitPlanSummary {
  strategyLabel: string
  subtitle: string
  items: Array<{
    split: string
    count: number
    help: string
  }>
  notes: string
}

export type ExportStatusTagType = 'success' | 'warning' | 'danger' | 'info'

export function buildDatasetVersionPayload(
  form: DatasetVersionCreateFormState,
): DatasetVersionCreatePayload {
  return {
    dataset_id: form.datasetId,
    version_name: form.versionName.trim(),
    description: form.notes,
    source_type: form.source,
    export_format: 'yolo',
    include_splits: [...form.includeSplits],
    split_strategy: form.splitStrategy,
    split_config:
      form.splitStrategy === 'auto-ratio'
        ? {
            scope_splits: [...form.scopeSplits],
            train_ratio: form.trainRatio,
            val_ratio: form.valRatio,
            test_ratio: form.testRatio,
            random_seed: form.randomSeed,
            include_assets: [...form.includeAssets],
          }
        : {
            scope_splits: [...form.includeSplits],
            include_assets: [...form.includeAssets],
          },
  }
}

export function buildDatasetVersionValidationFingerprint(
  form: DatasetVersionCreateFormState,
): string {
  return JSON.stringify({
    datasetId: form.datasetId,
    versionName: form.versionName.trim(),
    source: form.source,
    includeSplits: [...form.includeSplits].sort(),
    splitStrategy: form.splitStrategy,
    trainRatio: form.trainRatio,
    valRatio: form.valRatio,
    testRatio: form.testRatio,
    randomSeed: form.randomSeed,
    scopeSplits: [...form.scopeSplits].sort(),
    includeAssets: [...form.includeAssets].sort(),
    notes: form.notes,
  })
}

export function getSplitStrategyLabel(strategy: string): string {
  const map: Record<string, string> = {
    'reuse-existing': '复用现有划分',
    'auto-ratio': '按比例自动划分',
  }
  return map[strategy] || strategy
}

export function formatAutoRatioSummary(form: Pick<DatasetVersionCreateFormState, 'trainRatio' | 'valRatio' | 'testRatio'>): string {
  const train = Number.isFinite(form.trainRatio) ? form.trainRatio : 0
  const val = Number.isFinite(form.valRatio) ? form.valRatio : 0
  const test = Number.isFinite(form.testRatio) ? form.testRatio : 0
  return `train ${train} / val ${val} / test ${test}`
}

function readRecordMap(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return {}
  }
  return value as Record<string, unknown>
}

function readSplitCountMap(value: unknown): Record<string, number> {
  const raw = readRecordMap(value)
  return Object.fromEntries(
    Object.entries(raw).map(([key, count]) => [key, Number(count || 0)]),
  )
}

function formatScopeSplits(scopeSplits: unknown): string {
  if (!Array.isArray(scopeSplits) || !scopeSplits.length) {
    return '--'
  }
  return scopeSplits.join(' / ')
}

function buildSplitItems(counts: Record<string, number>) {
  const orderedSplits = ['train', 'val', 'test']
  return orderedSplits.map((split) => ({
    split,
    count: Number(counts[split] || 0),
    help: split === 'train'
      ? '用于模型训练'
      : split === 'val'
        ? '用于训练中验证'
        : '用于最终测试',
  }))
}

export function buildVersionSplitPlanSummary(
  item: Pick<DatasetVersionApiRecord, 'split_strategy' | 'split_config' | 'stats_snapshot'>,
): SplitPlanSummary {
  const splitConfig = readRecordMap(item.split_config)
  const statsSnapshot = readRecordMap(item.stats_snapshot)
  const resolvedCounts = readSplitCountMap(splitConfig.resolved_split_counts)
  const fallbackCounts = readSplitCountMap(statsSnapshot.split_counts)
  const counts = Object.keys(resolvedCounts).length ? resolvedCounts : fallbackCounts

  if (item.split_strategy === 'auto-ratio') {
    const scopeText = formatScopeSplits(splitConfig.scope_splits)
    const ratios = [
      `train ${Number(splitConfig.train_ratio || 0)}`,
      `val ${Number(splitConfig.val_ratio || 0)}`,
      `test ${Number(splitConfig.test_ratio || 0)}`,
    ].join(' / ')

    return {
      strategyLabel: '按比例自动划分',
      subtitle: `平台会先汇总来源范围 ${scopeText} 中的样本，再按比例冻结到最终训练划分。`,
      items: buildSplitItems(counts),
      notes: `当前冻结比例为 ${ratios}，随机种子 ${Number(splitConfig.random_seed || 42)}。`,
    }
  }

  const scopeText = formatScopeSplits(splitConfig.scope_splits)
  return {
    strategyLabel: '复用现有划分',
    subtitle: `平台直接沿用当前数据中的现有划分结构${scopeText !== '--' ? `，来源范围为 ${scopeText}` : ''}。`,
    items: buildSplitItems(counts),
    notes: '训练和导出将直接使用当前已存在的 train / val / test 结果，不再重新分配。',
  }
}

export function buildExportSplitPlanSummary(
  item: Pick<DatasetExportRecordDetail, 'split_config' | 'validation_summary'>,
): SplitPlanSummary {
  const splitConfig = readRecordMap(item.split_config)
  const validationSummary = readRecordMap(item.validation_summary)
  const validationSummaryBody = readRecordMap(validationSummary.summary)
  const resolvedCounts = readSplitCountMap(splitConfig.resolved_split_counts)
  const fallbackCounts = readSplitCountMap(validationSummaryBody.split_counts)
  const counts = Object.keys(resolvedCounts).length ? resolvedCounts : fallbackCounts
  const splits = Array.isArray(splitConfig.splits) ? splitConfig.splits.join(' / ') : '--'
  const strategy = typeof splitConfig.version_split_strategy === 'string'
    ? splitConfig.version_split_strategy
    : 'reuse-existing'

  return {
    strategyLabel: getSplitStrategyLabel(strategy),
    subtitle: `这次导出最终包含的目标划分为 ${splits}，训练任务将直接消费这套落地后的结果。`,
    items: buildSplitItems(counts),
    notes: Object.keys(resolvedCounts).length
      ? '下方数量为导出完成后实际写入到 images/labels 目录中的最终结果。'
      : '当前数量基于版本校验快照推导，用于帮助你在导出前确认最终训练输入结构。',
  }
}

export function getDatasetVersionIssueLabel(code: string): string {
  const map: Record<string, string> = {
    EMPTY_DATASET: '没有可导出的图片',
    EMPTY_LABELS: '缺少类别定义',
    EMPTY_ANNOTATIONS: '缺少有效标注',
    MISSING_IMAGE_FILES: '图片文件缺失',
    EMPTY_SPLIT: '划分为空',
    UNANNOTATED_IMAGES: '存在未标注图片',
    LOW_CLASS_SAMPLES: '类别样本偏少',
    INVALID_YOLO_ROW: 'YOLO 标注格式错误',
    INVALID_YOLO_VALUE: 'YOLO 标注值非法',
    INVALID_CLASS_ID: 'YOLO 类别索引非法',
    INVALID_YOLO_COORD: 'YOLO 坐标越界',
    INVALID_SPLIT_CONFIG: '划分配置无效',
  }
  return map[code] || code
}

export function buildValidationIssueDisplay(
  issue: DatasetVersionValidationIssue,
): ValidationIssueDisplay {
  const levelMap: Record<string, string> = {
    error: '阻断项',
    warning: '警告项',
  }
  return {
    ...issue,
    title: `${levelMap[issue.level] || issue.level} · ${getDatasetVersionIssueLabel(issue.code)}`,
  }
}

export function collectValidationIssueDisplay(
  validationResult: DatasetVersionValidationResult | null,
): ValidationIssueDisplay[] {
  if (!validationResult) {
    return []
  }
  return [...validationResult.errors, ...validationResult.warnings].map(buildValidationIssueDisplay)
}

export function collectValidationMessages(
  validationResult: DatasetVersionValidationResult | null,
  emptyText: string,
): string[] {
  const messages = collectValidationIssueDisplay(validationResult).map((issue) => issue.message)
  return messages.length ? messages : [emptyText]
}

export function getDatasetExportStatusTagType(status: DatasetExportStatus): ExportStatusTagType {
  const map: Record<DatasetExportStatus, ExportStatusTagType> = {
    success: 'success',
    exporting: 'warning',
    failed: 'danger',
    pending: 'info',
  }
  return map[status]
}

export function getDatasetExportStatusLabel(status: DatasetExportStatus): string {
  const map: Record<DatasetExportStatus, string> = {
    success: '已完成',
    exporting: '处理中',
    failed: '失败',
    pending: '待执行',
  }
  return map[status]
}

export function formatDatasetVersionSplitSummary(item: {
  split_config?: Record<string, unknown> | null
  stats_snapshot?: Record<string, unknown> | null
}): string {
  const splitConfig = item.split_config || {}
  const resolvedCounts = splitConfig.resolved_split_counts
  if (resolvedCounts && typeof resolvedCounts === 'object') {
    return Object.entries(resolvedCounts as Record<string, unknown>)
      .map(([key, value]) => `${key} ${value}`)
      .join(' / ')
  }

  const stats = item.stats_snapshot || {}
  const splitCounts = stats.split_counts
  if (splitCounts && typeof splitCounts === 'object') {
    return Object.entries(splitCounts as Record<string, unknown>)
      .map(([key, value]) => `${key} ${value}`)
      .join(' / ')
  }
  return '--'
}

export function mapDatasetVersionSummary(
  item: DatasetVersionApiRecord,
  datasetName: string,
): DatasetVersionSummary {
  return {
    id: item.id,
    datasetId: item.dataset_id,
    datasetName,
    versionName: item.version_name,
    source: item.source_type as DatasetVersionSummary['source'],
    imageCount: Number(item.stats_snapshot?.image_count || 0),
    annotationCount: Number(item.stats_snapshot?.box_count || 0),
    classCount: Number(item.stats_snapshot?.class_count || 0),
    splitSummary: formatDatasetVersionSplitSummary(item),
    exportFormat: (item.export_format || 'yolo').toUpperCase(),
    status: item.status === 'frozen' ? 'ready' : item.status === 'archived' ? 'archived' : 'draft',
    createdBy: 'system',
    createdAt: item.created_at,
    notes: item.description || '',
    validationHints: item.validation_summary?.warnings?.map((warning) => warning.message) || [],
  }
}

export function mapDatasetExportRecord(
  item: DatasetExportRecordDetail,
  versions: DatasetVersionSummary[],
): DatasetExportRecord {
  const version = versions.find((entry) => entry.id === item.dataset_version_id)
  return {
    id: item.id,
    datasetId: item.dataset_id,
    datasetName: version?.datasetName || '--',
    versionName: version?.versionName || '--',
    exportName: item.export_name,
    exportFormat: (item.export_format || 'yolo') as DatasetExportRecord['exportFormat'],
    exportScope: Array.isArray(item.split_config?.splits) ? item.split_config.splits.join(' / ') : '--',
    status:
      item.status === 'success'
        ? 'completed'
        : item.status === 'exporting' || item.status === 'pending'
          ? 'processing'
          : 'failed',
    outputPath: item.output_path || '--',
    createdBy: 'system',
    createdAt: item.created_at,
    notes: typeof item.split_config?.notes === 'string' ? item.split_config.notes : '',
    includedAssets: Array.isArray(item.split_config?.extras) ? item.split_config.extras : [],
    validationSummary: [
      ...(item.validation_summary?.errors?.map((issue) => issue.message) || []),
      ...(item.validation_summary?.warnings?.map((issue) => issue.message) || []),
    ],
  }
}
