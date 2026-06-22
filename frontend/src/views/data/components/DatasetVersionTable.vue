<template>
  <el-card class="section-card">
    <template #header>
      <div class="section-header">
        <span>数据集版本</span>
        <el-button type="primary" plain @click="$emit('create')">新建版本</el-button>
      </div>
    </template>

    <el-table :data="versions" border stripe>
      <el-table-column prop="versionName" label="版本名称" min-width="160" />
      <el-table-column prop="datasetName" label="数据集" min-width="150" />
      <el-table-column label="来源" width="140">
        <template #default="{ row }">{{ sourceLabel(row.source) }}</template>
      </el-table-column>
      <el-table-column label="样本规模" min-width="180">
        <template #default="{ row }">
          {{ row.imageCount }} 图 / {{ row.annotationCount }} 标注 / {{ row.classCount }} 类
        </template>
      </el-table-column>
      <el-table-column prop="splitSummary" label="数据划分" min-width="160" />
      <el-table-column prop="exportFormat" label="训练格式" width="110" />
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createdBy" label="创建人" width="110" />
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">{{ formatDate(row.createdAt) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="260" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="$emit('detail', row)">详情</el-button>
          <el-button link type="success" @click="$emit('export', row)">导出</el-button>
          <el-button link type="warning" @click="$emit('compare', row)">对比</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import type { DatasetVersionSummary } from '@/types/dataset-version'

defineProps<{
  versions: DatasetVersionSummary[]
}>()

defineEmits<{
  create: []
  detail: [row: DatasetVersionSummary]
  export: [row: DatasetVersionSummary]
  compare: [row: DatasetVersionSummary]
}>()

function sourceLabel(source: DatasetVersionSummary['source']): string {
  const map: Record<DatasetVersionSummary['source'], string> = {
    'annotation-export': '标注导出',
    imported: '外部导入',
    'manual-freeze': '手动冻结',
  }
  return map[source]
}

function statusType(status: DatasetVersionSummary['status']): 'success' | 'info' | 'warning' {
  const map: Record<DatasetVersionSummary['status'], 'success' | 'info' | 'warning'> = {
    ready: 'success',
    draft: 'warning',
    archived: 'info',
  }
  return map[status]
}

function statusLabel(status: DatasetVersionSummary['status']): string {
  const map: Record<DatasetVersionSummary['status'], string> = {
    ready: '可训练',
    draft: '草稿',
    archived: '归档',
  }
  return map[status]
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString()
}
</script>

<style scoped>
.section-card {
  border-radius: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
