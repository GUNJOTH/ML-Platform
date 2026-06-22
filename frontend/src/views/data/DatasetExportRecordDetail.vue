<template>
  <div class="dataset-export-record-detail">
    <div class="page-header">
      <div>
        <h3>导出记录详情</h3>
        <p class="page-subtitle">
          当前先提供导出记录详情页骨架，后续再接真实导出任务状态、下载和审计追踪。
        </p>
      </div>
      <div class="header-actions">
        <el-button @click="goBack">返回版本列表</el-button>
        <el-button type="primary" @click="goValidation">查看版本校验</el-button>
      </div>
    </div>

    <el-card class="hero-card">
      <div class="hero-title">{{ record?.exportName || '--' }}</div>
      <div class="hero-subtitle">
        {{ record?.datasetName || '--' }} / {{ record?.versionName || '--' }}
      </div>
      <div class="hero-tags">
        <el-tag :type="statusType">{{ statusLabel }}</el-tag>
        <el-tag type="info">{{ (record?.exportFormat || '--').toUpperCase() }}</el-tag>
      </div>
    </el-card>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="section-card">
          <template #header>导出基本信息</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="来源版本">{{ record?.versionName || '--' }}</el-descriptions-item>
            <el-descriptions-item label="导出范围">{{ record?.exportScope || '--' }}</el-descriptions-item>
            <el-descriptions-item label="输出路径">{{ record?.outputPath || '--' }}</el-descriptions-item>
            <el-descriptions-item label="操作人">{{ record?.createdBy || '--' }}</el-descriptions-item>
            <el-descriptions-item label="导出时间">{{ formatDate(record?.createdAt) }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="section-card">
          <template #header>记录说明</template>
          <div class="notes-text">{{ record?.notes || '暂无说明' }}</div>
          <div class="asset-list">
            <span class="asset-label">附带资源</span>
            <div class="asset-tags">
              <el-tag v-for="item in record?.includedAssets || []" :key="item" type="success" effect="plain">
                {{ item }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="section-card">
      <template #header>导出前校验摘要</template>
      <div class="summary-grid">
        <div v-for="item in record?.validationSummary || []" :key="item" class="summary-item">
          {{ item }}
        </div>
      </div>
    </el-card>

    <el-card class="section-card">
      <template #header>后续能力预留</template>
      <el-table :data="futureCapabilities" border stripe>
        <el-table-column prop="name" label="能力" min-width="200" />
        <el-table-column prop="description" label="说明" min-width="320" />
        <el-table-column prop="phase" label="当前阶段" width="140" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { findMockExportRecordById, findMockVersionByName, mockDatasetExportRecords } from './datasetVersionMock'

const route = useRoute()
const router = useRouter()

const recordId = String(route.params.recordId || mockDatasetExportRecords[0]?.id || '')
const record = computed(() => findMockExportRecordById(recordId) || mockDatasetExportRecords[0] || null)

const relatedVersion = computed(() =>
  record.value ? findMockVersionByName(record.value.versionName) || null : null,
)

const statusType = computed(() => {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    completed: 'success',
    processing: 'warning',
    failed: 'danger',
  }
  return map[record.value?.status || ''] || 'info'
})

const statusLabel = computed(() => {
  const map: Record<string, string> = {
    completed: '已完成',
    processing: '处理中',
    failed: '失败',
  }
  return map[record.value?.status || ''] || '--'
})

const futureCapabilities = [
  {
    name: '下载导出包',
    description: '后续从这里直连导出产物下载和有效期控制。',
    phase: '界面预留',
  },
  {
    name: '复用导出配置',
    description: '后续允许一键复用当前导出参数，生成新的导出任务。',
    phase: '界面预留',
  },
  {
    name: '导出任务审计',
    description: '后续展示触发时间线、失败原因和重试记录。',
    phase: '后续实现',
  },
]

function formatDate(value?: string): string {
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

.asset-list {
  margin-top: 16px;
}

.asset-label {
  display: block;
  margin-bottom: 10px;
  color: #64748b;
  font-size: 13px;
}

.asset-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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
