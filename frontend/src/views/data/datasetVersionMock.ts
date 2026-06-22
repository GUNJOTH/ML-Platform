import type { DatasetExportRecord, DatasetVersionSummary } from '@/types/dataset-version'

export const mockDatasetVersions: DatasetVersionSummary[] = [
  {
    id: 'ver_smoke_v3',
    datasetId: 'mock_smoke_dataset',
    datasetName: 'Smoke Demo Dataset',
    versionName: 'smoke_v3_freeze',
    source: 'annotation-export',
    imageCount: 1280,
    annotationCount: 2417,
    classCount: 3,
    splitSummary: 'train 70% / val 20% / test 10%',
    exportFormat: 'YOLO',
    status: 'ready',
    createdBy: 'admin',
    createdAt: '2026-06-22T09:20:00+08:00',
    notes: '用于训练前冻结，来源于单人标注闭环后的首次导出。',
    splitDetail: [
      { split: 'train', images: 896, annotations: 1691 },
      { split: 'val', images: 256, annotations: 484 },
      { split: 'test', images: 128, annotations: 242 },
    ],
    classDistribution: [
      { className: 'smoke', count: 1360, ratio: '56.3%' },
      { className: 'fire', count: 702, ratio: '29.0%' },
      { className: 'person', count: 355, ratio: '14.7%' },
    ],
    validationHints: [
      '后续在这里接入空标注、漏图、类别失衡、划分缺失等训练前校验。',
      '未来版本详情应展示与上一版本的样本增减和类别差异。',
      '训练任务应绑定版本 ID，而不是直接绑定可变数据集。',
    ],
  },
  {
    id: 'ver_smoke_v2',
    datasetId: 'mock_smoke_dataset',
    datasetName: 'Smoke Demo Dataset',
    versionName: 'smoke_v2_imported',
    source: 'imported',
    imageCount: 960,
    annotationCount: 1730,
    classCount: 3,
    splitSummary: 'train 80% / val 20%',
    exportFormat: 'YOLO',
    status: 'archived',
    createdBy: 'admin',
    createdAt: '2026-06-15T14:30:00+08:00',
    notes: '外部导入基线版本，作为演示起点保留。',
    splitDetail: [
      { split: 'train', images: 768, annotations: 1380 },
      { split: 'val', images: 192, annotations: 350 },
    ],
    classDistribution: [
      { className: 'smoke', count: 980, ratio: '56.6%' },
      { className: 'fire', count: 492, ratio: '28.4%' },
      { className: 'person', count: 258, ratio: '14.9%' },
    ],
    validationHints: [
      '该版本可用于对比导入基线与标注闭环后的提升幅度。',
      '后续支持一键回退到历史版本并重新导出。',
    ],
  },
  {
    id: 'ver_defect_v1',
    datasetId: 'mock_defect_dataset',
    datasetName: 'Surface Defect Trial',
    versionName: 'defect_v1_draft',
    source: 'manual-freeze',
    imageCount: 420,
    annotationCount: 688,
    classCount: 4,
    splitSummary: 'train 60% / val 20% / test 20%',
    exportFormat: 'YOLO',
    status: 'draft',
    createdBy: 'qa_user',
    createdAt: '2026-06-21T18:05:00+08:00',
    notes: '训练前人工冻结，待补充分层抽样校验。',
    splitDetail: [
      { split: 'train', images: 252, annotations: 406 },
      { split: 'val', images: 84, annotations: 136 },
      { split: 'test', images: 84, annotations: 146 },
    ],
    classDistribution: [
      { className: 'scratch', count: 233, ratio: '33.9%' },
      { className: 'dent', count: 181, ratio: '26.3%' },
      { className: 'stain', count: 151, ratio: '22.0%' },
      { className: 'crack', count: 123, ratio: '17.9%' },
    ],
    validationHints: [
      '草稿版本未来应阻止直接进入训练，需先通过训练前校验。',
      '建议后续补充按类别和场景的覆盖率检查。',
    ],
  },
]

export const mockDatasetExportRecords: DatasetExportRecord[] = [
  {
    id: 'exp_smoke_v3_yolo',
    datasetId: 'mock_smoke_dataset',
    datasetName: 'Smoke Demo Dataset',
    versionName: 'smoke_v3_freeze',
    exportName: 'smoke_v3_yolo_trainset',
    exportFormat: 'yolo',
    exportScope: '全部样本 + train/val/test 划分',
    status: 'completed',
    outputPath: 'storage/exports/smoke_v3_yolo.zip',
    createdBy: 'admin',
    createdAt: '2026-06-22T10:00:00+08:00',
    notes: '用于 YOLO 训练的标准导出包，包含图片、标签与 manifest。',
    includedAssets: ['原图', '标注文件', 'manifest'],
    validationSummary: ['版本冻结已完成', '训练格式匹配 YOLO', '导出范围完整'],
  },
  {
    id: 'exp_smoke_v3_coco',
    datasetId: 'mock_smoke_dataset',
    datasetName: 'Smoke Demo Dataset',
    versionName: 'smoke_v3_freeze',
    exportName: 'smoke_v3_coco_audit',
    exportFormat: 'coco',
    exportScope: '验证集审计导出',
    status: 'processing',
    outputPath: 'storage/exports/pending/smoke_v3_coco.zip',
    createdBy: 'admin',
    createdAt: '2026-06-22T10:18:00+08:00',
    notes: '用于审计和对外部工具兼容性验证的 COCO 导出。',
    includedAssets: ['验证集图片', 'COCO 标注', '统计摘要'],
    validationSummary: ['等待导出任务执行', '导出范围为 val split', '版本校验结果待绑定'],
  },
  {
    id: 'exp_defect_v1_yolo',
    datasetId: 'mock_defect_dataset',
    datasetName: 'Surface Defect Trial',
    versionName: 'defect_v1_draft',
    exportName: 'defect_v1_trial_export',
    exportFormat: 'yolo',
    exportScope: '仅 train/val，跳过测试集',
    status: 'failed',
    outputPath: 'storage/exports/failed/defect_v1_trial_export.zip',
    createdBy: 'qa_user',
    createdAt: '2026-06-21T20:40:00+08:00',
    notes: '演示草稿版本导出，后续应通过校验后再允许正式导出。',
    includedAssets: ['原图', '标签文件'],
    validationSummary: ['草稿版本未通过完整校验', 'test split 缺失', '需要人工确认是否允许导出'],
  },
]

export function findMockVersionByName(versionName: string): DatasetVersionSummary | undefined {
  return mockDatasetVersions.find((item) => item.versionName === versionName)
}

export function findMockVersionById(versionId: string): DatasetVersionSummary | undefined {
  return mockDatasetVersions.find((item) => item.id === versionId)
}

export function findMockExportRecordById(recordId: string): DatasetExportRecord | undefined {
  return mockDatasetExportRecords.find((item) => item.id === recordId)
}
