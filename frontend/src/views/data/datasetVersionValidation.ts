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
  splitStrategy: string
  splitSummary: string
  includeAssets: string[]
}

export interface ValidationIssueDisplay extends DatasetVersionValidationIssue {
  title: string
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
    split_config: {
      summary: form.splitSummary,
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
    splitSummary: form.splitSummary,
    includeAssets: [...form.includeAssets].sort(),
    notes: form.notes,
  })
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
  const stats = item.stats_snapshot || {}
  const splitCounts = stats.split_counts
  if (splitCounts && typeof splitCounts === 'object') {
    return Object.entries(splitCounts as Record<string, unknown>)
      .map(([key, value]) => `${key} ${value}`)
      .join(' / ')
  }
  if (typeof item.split_config?.summary === 'string') {
    return item.split_config.summary
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
