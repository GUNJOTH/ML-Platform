<template>
  <el-card class="section-card">
    <template #header>
      <div class="section-header">
        <span>导出记录</span>
        <el-button type="primary" plain @click="$emit('create')">发起导出</el-button>
      </div>
    </template>

    <el-table :data="records" border stripe>
      <el-table-column prop="exportName" label="导出名称" min-width="170" />
      <el-table-column prop="datasetName" label="数据集" min-width="150" />
      <el-table-column prop="versionName" label="来源版本" min-width="150" />
      <el-table-column prop="exportFormat" label="格式" width="100" />
      <el-table-column prop="exportScope" label="导出范围" min-width="180" />
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="outputPath" label="目标路径" min-width="220" show-overflow-tooltip />
      <el-table-column prop="createdBy" label="操作人" width="110" />
      <el-table-column label="导出时间" width="180">
        <template #default="{ row }">{{ formatDate(row.createdAt) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="$emit('detail', row)">详情</el-button>
          <el-button link type="success" @click="$emit('download', row)">下载</el-button>
          <el-button link type="warning" @click="$emit('reuse', row)">复用配置</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import type { DatasetExportRecord } from '@/types/dataset-version'

defineProps<{
  records: DatasetExportRecord[]
}>()

defineEmits<{
  create: []
  detail: [row: DatasetExportRecord]
  download: [row: DatasetExportRecord]
  reuse: [row: DatasetExportRecord]
}>()

function statusType(status: DatasetExportRecord['status']): 'success' | 'info' | 'warning' | 'danger' {
  const map: Record<DatasetExportRecord['status'], 'success' | 'info' | 'warning' | 'danger'> = {
    completed: 'success',
    processing: 'warning',
    failed: 'danger',
  }
  return map[status]
}

function statusLabel(status: DatasetExportRecord['status']): string {
  const map: Record<DatasetExportRecord['status'], string> = {
    completed: '已完成',
    processing: '处理中',
    failed: '失败',
  }
  return map[status]
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString()
}
</script>

<style scoped>
.section-card {
  margin-top: 20px;
  border-radius: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
