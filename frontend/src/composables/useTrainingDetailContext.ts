import { getDatasets } from '@/api/dataset'
import { getDatasetExport, getDatasetVersion } from '@/api/datasetVersion'
import { getModel } from '@/api/model'
import type { Dataset } from '@/types/dataset'
import type { DatasetExportRecordDetail, DatasetVersionApiRecord } from '@/types/dataset-version'
import type { MLModel } from '@/types/model'
import type { Task, TrainingDetailContext } from '@/types/task'

function readNumberMap(value: unknown): Record<string, number> {
  if (!value || typeof value !== 'object') {
    return {}
  }

  const entries = Object.entries(value as Record<string, unknown>).map(([key, rawValue]) => [
    key,
    Number(rawValue || 0),
  ])
  return Object.fromEntries(entries)
}

function readClassNames(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return []
  }

  return value
    .map((item) => {
      if (!item || typeof item !== 'object') {
        return ''
      }
      const name = (item as Record<string, unknown>).name
      return typeof name === 'string' ? name : ''
    })
    .filter(Boolean)
}

function formatSplitSummary(splitCounts: Record<string, number>): string {
  const entries = Object.entries(splitCounts)
  if (!entries.length) {
    return '--'
  }
  return entries.map(([split, count]) => `${split} ${count}`).join(' / ')
}

export async function buildTrainingDetailContext(
  task: Task,
): Promise<TrainingDetailContext | null> {
  const [model, datasets, version, exportRecord] = await Promise.all([
    task.model_id ? getModel(task.model_id).catch(() => null) : Promise.resolve<MLModel | null>(null),
    getDatasets().catch(() => [] as Dataset[]),
    task.dataset_version_id
      ? getDatasetVersion(task.dataset_version_id).catch(() => null)
      : Promise.resolve<DatasetVersionApiRecord | null>(null),
    task.dataset_export_id
      ? getDatasetExport(task.dataset_export_id).catch(() => null)
      : Promise.resolve<DatasetExportRecordDetail | null>(null),
  ])

  const dataset = datasets.find((item) => item.id === task.dataset_id) || null
  const statsSnapshot = version?.stats_snapshot || {}
  const splitCounts = readNumberMap(statsSnapshot.split_counts)
  const classNames = readClassNames(version?.label_schema_snapshot)

  return {
    datasetName: dataset?.name || '--',
    modelName: model?.name || '--',
    modelVersion: model?.version || '--',
    versionName: version?.version_name || '--',
    exportName: exportRecord?.export_name || '--',
    exportFormat: (exportRecord?.export_format || '--').toUpperCase(),
    dataYamlPath: exportRecord?.data_yaml_path || '--',
    exportCreatedAt: exportRecord?.created_at || '--',
    exportNotes:
      typeof exportRecord?.split_config?.notes === 'string' && exportRecord.split_config.notes
        ? exportRecord.split_config.notes
        : '--',
    splitSummary: formatSplitSummary(splitCounts),
    classCount: Number(statsSnapshot.class_count || classNames.length || 0),
    classNames,
    imageCount: Number(statsSnapshot.image_count || 0),
    boxCount: Number(statsSnapshot.box_count || 0),
    splitCounts,
  }
}
