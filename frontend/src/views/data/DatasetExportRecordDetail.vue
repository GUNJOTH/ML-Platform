<template>
  <div class="dataset-export-record-detail">
    <div class="page-header">
      <div>
        <h3>导出记录详情</h3>
        <p class="page-subtitle">查看单次导出的状态、产物路径、配置摘要和校验结果。</p>
      </div>
      <div class="header-actions">
        <el-button @click="goBack">返回版本列表</el-button>
        <el-button type="primary" @click="goValidation">查看版本校验</el-button>
      </div>
    </div>

    <el-card class="hero-card">
      <div class="hero-title">{{ record?.export_name || '--' }}</div>
      <div class="hero-subtitle">{{ relatedVersion?.version_name || '--' }} / {{ datasetName }}</div>
      <div class="hero-tags">
        <el-tag :type="statusType">{{ statusLabel }}</el-tag>
        <el-tag type="info">{{ exportFormat }}</el-tag>
      </div>
    </el-card>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="section-card">
          <template #header>导出基本信息</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="来源版本">{{ relatedVersion?.version_name || '--' }}</el-descriptions-item>
            <el-descriptions-item label="输出路径">{{ record?.output_path || '--' }}</el-descriptions-item>
            <el-descriptions-item label="dataset.yaml">{{ record?.data_yaml_path || '--' }}</el-descriptions-item>
            <el-descriptions-item label="manifest">{{ record?.manifest_path || '--' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(record?.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="完成时间">{{ formatDate(record?.finished_at) }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="section-card">
          <template #header>导出配置</template>
          <div class="notes-text">split: {{ splitText }}</div>
          <div class="notes-text">extras: {{ extrasText }}</div>
          <div class="notes-text">notes: {{ notesText }}</div>
          <div v-if="record?.error_message" class="error-box">
            {{ record.error_message }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="section-card">
      <template #header>校验摘要</template>
      <div class="summary-grid">
        <div v-for="item in validationMessages" :key="item" class="summary-item">
          {{ item }}
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDatasets } from '@/api/dataset'
import { getDatasetExport, getDatasetVersion } from '@/api/datasetVersion'
import type {
  DatasetExportRecordDetail,
  DatasetVersionApiRecord,
} from '@/types/dataset-version'
import {
  collectValidationMessages,
  getDatasetExportStatusLabel,
  getDatasetExportStatusTagType,
} from './datasetVersionValidation'

const EMPTY_VALIDATION_TEXT = '当前导出没有记录额外的校验问题'

const route = useRoute()
const router = useRouter()
const record = ref<DatasetExportRecordDetail | null>(null)
const relatedVersion = ref<DatasetVersionApiRecord | null>(null)
const datasetName = ref('--')

const statusType = computed(() =>
  record.value ? getDatasetExportStatusTagType(record.value.status) : 'info',
)

const statusLabel = computed(() =>
  record.value ? getDatasetExportStatusLabel(record.value.status) : '--',
)

const exportFormat = computed(() => (record.value?.export_format || '--').toUpperCase())

const splitText = computed(() => {
  const splits = record.value?.split_config?.splits
  return Array.isArray(splits) ? splits.join(' / ') : '--'
})

const extrasText = computed(() => {
  const extras = record.value?.split_config?.extras
  return Array.isArray(extras) ? extras.join(' / ') : '--'
})

const notesText = computed(() => {
  const notes = record.value?.split_config?.notes
  return typeof notes === 'string' && notes ? notes : '--'
})

const validationMessages = computed(() =>
  collectValidationMessages(record.value?.validation_summary || null, EMPTY_VALIDATION_TEXT),
)

onMounted(async () => {
  const recordId = String(route.params.recordId || '')
  if (!recordId) {
    return
  }

  record.value = await getDatasetExport(recordId)
  if (record.value?.dataset_version_id) {
    relatedVersion.value = await getDatasetVersion(record.value.dataset_version_id)
  }

  try {
    const datasets = await getDatasets()
    datasetName.value = datasets.find((item) => item.id === record.value?.dataset_id)?.name || '--'
  } catch {
    datasetName.value = '--'
  }
})

function formatDate(value?: string | null): string {
  if (!value) {
    return '--'
  }
  return new Date(value).toLocaleString()
}

function goBack() {
  router.push('/data/versions')
}

function goValidation() {
  if (!relatedVersion.value) {
    return
  }
  router.push(`/data/versions/validation/${relatedVersion.value.id}`)
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.page-subtitle {
  margin: 8px 0 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.7;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.hero-card,
.section-card {
  border-radius: 16px;
  margin-bottom: 20px;
}

.hero-title {
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
}

.hero-subtitle {
  margin-top: 8px;
  color: #64748b;
}

.hero-tags {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}

.notes-text {
  color: #475569;
  line-height: 1.8;
}

.error-box {
  margin-top: 16px;
  padding: 12px 14px;
  border-radius: 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.summary-item {
  padding: 12px 14px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #475569;
}
</style>
