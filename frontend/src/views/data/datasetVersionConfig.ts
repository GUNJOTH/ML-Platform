import type {
  DatasetVersionOverviewCard,
  DatasetVersionPlanItem,
  DatasetVersionSummary,
} from '@/types/dataset-version'

export const datasetVersionListPlanItems: DatasetVersionPlanItem[] = [
  {
    title: '训练前先冻结版本',
    description: '让训练任务引用版本 ID，而不是直接引用可变数据集，保证结果可追溯。',
  },
  {
    title: '每次导出都落历史',
    description: '沉淀导出格式、导出范围、输出目录与发起人，服务于回查和复用。',
  },
  {
    title: '后续补差异对比',
    description: '重点对比样本数、类别分布、空标注和划分变化，而不只是版本号递增。',
  },
  {
    title: '为训练前校验预留入口',
    description: '版本详情页未来可直接接入缺图、空标注、类别失衡、划分缺失等检查。',
  },
]

export const datasetVersionCreatePlanItems: DatasetVersionPlanItem[] = [
  {
    title: '版本先行',
    description: '训练、评估、导出后续都应绑定版本，而不是直接绑定可变数据集。',
  },
  {
    title: '冻结快照',
    description: '后续真正落地时，这里负责生成版本清单、划分快照和校验结果。',
  },
  {
    title: '支持回溯',
    description: '版本对象需要记录创建人、来源、策略和导出兼容信息。',
  },
]

export const datasetVersionCreateValidationHints: string[] = [
  '预留空标注、漏图、非法类别、划分缺失等训练前检查结果区。',
  '预留与上一个版本对比的增量信息，例如样本数和类别变化。',
  '预留冻结后自动生成导出记录和训练候选版本能力。',
]

export function buildDatasetVersionOverviewCards(
  versions: DatasetVersionSummary[],
  exportRecordCount: number,
): DatasetVersionOverviewCard[] {
  return [
    {
      label: '版本总数',
      value: versions.length,
      help: '后续这里会接真实版本仓视图，用于训练前冻结追溯。',
    },
    {
      label: '可训练版本',
      value: versions.filter((item) => item.status === 'ready').length,
      help: '训练入口未来应只允许选择通过校验的可训练版本。',
    },
    {
      label: '导出记录',
      value: exportRecordCount,
      help: '用于沉淀导出路径、格式、操作者与时间线。',
    },
    {
      label: '待补逻辑',
      value: '4',
      help: '版本冻结、差异对比、导出任务、回滚与复用规则。',
    },
  ]
}
