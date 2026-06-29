import { getDatasets } from '@/api/dataset'
import { getDatasetExport, getDatasetVersion } from '@/api/datasetVersion'
import { getModel } from '@/api/model'
import type { Dataset } from '@/types/dataset'
import type {
  DatasetExportRecordDetail,
  DatasetVersionApiRecord,
} from '@/types/dataset-version'
import type { MLModel } from '@/types/model'
import type { Task, TrainingDetailContext } from '@/types/task'

function readNumberMap(value: unknown): Record<string, number> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return {}
  }

  const entries = Object.entries(value as Record<string, unknown>).map(
    ([key, rawValue]) => [key, Number(rawValue || 0)],
  )
  return Object.fromEntries(entries)
}

function readClassNames(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value
      .map((item) => {
        if (typeof item === 'string') {
          return item
        }
        if (!item || typeof item !== 'object') {
          return ''
        }
        const name = (item as Record<string, unknown>).name
        return typeof name === 'string' ? name : ''
      })
      .filter(Boolean)
  }

  return []
}

function formatSplitSummary(splitCounts: Record<string, number>): string {
  const orderedSplits = ['train', 'val', 'test']
  const entries = orderedSplits
    .filter((split) => split in splitCounts)
    .map((split) => `${split} ${splitCounts[split]}`)

  if (!entries.length) {
    return '--'
  }
  return entries.join(' / ')
}

function readTaskConfig(task: Task): Record<string, unknown> {
  if (!task.config || typeof task.config !== 'object' || Array.isArray(task.config)) {
    return {}
  }
  return task.config
}

function readTaskString(config: Record<string, unknown>, key: string): string {
  const value = config[key]
  return typeof value === 'string' && value ? value : '--'
}

function readTaskNumber(config: Record<string, unknown>, key: string): number {
  return Number(config[key] || 0)
}

export async function buildTrainingDetailContext(
  task: Task,
): Promise<TrainingDetailContext | null> {
  const config = readTaskConfig(task)

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
  const fallbackSplitCounts = readNumberMap(statsSnapshot.split_counts)
  const splitCounts = readNumberMap(config.split_counts)
  const resolvedSplitCounts = Object.keys(splitCounts).length
    ? splitCounts
    : fallbackSplitCounts

  const fallbackClassNames = readClassNames(version?.label_schema_snapshot)
  const classNames = readClassNames(config.class_names)
  const resolvedClassNames = classNames.length ? classNames : fallbackClassNames

  const fallbackDatasetName = dataset?.name || '--'
  const fallbackModelName = model?.name || '--'
  const fallbackModelVersion = model?.version || '--'

  return {
    datasetName: readTaskString(config, 'dataset_name') !== '--'
      ? readTaskString(config, 'dataset_name')
      : fallbackDatasetName,
    modelName: readTaskString(config, 'model_name') !== '--'
      ? readTaskString(config, 'model_name')
      : fallbackModelName,
    modelVersion: readTaskString(config, 'model_version') !== '--'
      ? readTaskString(config, 'model_version')
      : fallbackModelVersion,
    versionName: readTaskString(config, 'dataset_version_name') !== '--'
      ? readTaskString(config, 'dataset_version_name')
      : (version?.version_name || '--'),
    exportName: readTaskString(config, 'dataset_export_name') !== '--'
      ? readTaskString(config, 'dataset_export_name')
      : (exportRecord?.export_name || '--'),
    exportFormat: (
      readTaskString(config, 'export_format') !== '--'
        ? readTaskString(config, 'export_format')
        : (exportRecord?.export_format || '--')
    ).toUpperCase(),
    dataYamlPath: readTaskString(config, 'data_yaml_path') !== '--'
      ? readTaskString(config, 'data_yaml_path')
      : (exportRecord?.data_yaml_path || '--'),
    exportCreatedAt: readTaskString(config, 'export_created_at') !== '--'
      ? readTaskString(config, 'export_created_at')
      : (exportRecord?.created_at || '--'),
    exportNotes: readTaskString(config, 'export_notes') !== '--'
      ? readTaskString(config, 'export_notes')
      : (
          typeof exportRecord?.split_config?.notes === 'string' &&
          exportRecord.split_config.notes
            ? exportRecord.split_config.notes
            : '--'
        ),
    splitSummary: readTaskString(config, 'split_summary') !== '--'
      ? readTaskString(config, 'split_summary')
      : formatSplitSummary(resolvedSplitCounts),
    classCount:
      readTaskNumber(config, 'class_count') ||
      Number(statsSnapshot.class_count || resolvedClassNames.length || 0),
    classNames: resolvedClassNames,
    imageCount:
      readTaskNumber(config, 'image_count') || Number(statsSnapshot.image_count || 0),
    boxCount:
      readTaskNumber(config, 'box_count') || Number(statsSnapshot.box_count || 0),
    splitCounts: resolvedSplitCounts,
  }
}
