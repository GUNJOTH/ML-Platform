<template>
  <el-drawer
    :model-value="visible"
    title="版本详情"
    size="720px"
    @update:model-value="emit('update:visible', $event)"
  >
    <template v-if="version">
      <div class="hero-card">
        <div>
          <div class="hero-title">{{ version.versionName }}</div>
          <div class="hero-subtitle">{{ version.datasetName }}</div>
        </div>
        <el-tag :type="statusType(version.status)">{{ statusLabel(version.status) }}</el-tag>
      </div>

      <el-descriptions :column="2" border class="section-block">
        <el-descriptions-item label="版本来源">{{ sourceLabel(version.source) }}</el-descriptions-item>
        <el-descriptions-item label="训练格式">{{ version.exportFormat }}</el-descriptions-item>
        <el-descriptions-item label="图像数量">{{ version.imageCount }}</el-descriptions-item>
        <el-descriptions-item label="标注数量">{{ version.annotationCount }}</el-descriptions-item>
        <el-descriptions-item label="类别数量">{{ version.classCount }}</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ version.createdBy }}</el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">
          {{ formatDate(version.createdAt) }}
        </el-descriptions-item>
      </el-descriptions>

      <el-card class="section-block">
        <template #header>版本说明</template>
        <div class="notes-text">{{ version.notes }}</div>
      </el-card>

      <el-card class="section-block">
        <template #header>数据划分</template>
        <div class="split-summary-line">{{ version.splitSummary }}</div>
        <el-table :data="version.splitDetail || []" border stripe>
          <el-table-column prop="split" label="划分" width="120" />
          <el-table-column prop="images" label="图像数" width="140" />
          <el-table-column prop="annotations" label="标注数" width="140" />
        </el-table>
      </el-card>

      <el-card class="section-block">
        <template #header>类别分布</template>
        <el-table :data="version.classDistribution || []" border stripe>
          <el-table-column prop="className" label="类别" min-width="180" />
          <el-table-column prop="count" label="实例数" width="140" />
          <el-table-column prop="ratio" label="占比" width="140" />
        </el-table>
      </el-card>

      <el-card class="section-block">
        <template #header>训练前校验预留</template>
        <div class="hint-list">
          <div v-for="hint in version.validationHints || []" :key="hint" class="hint-item">
            {{ hint }}
          </div>
        </div>
      </el-card>

      <div class="footer-actions">
        <el-button @click="emit('compare', version)">发起版本对比</el-button>
        <el-button type="primary" @click="emit('export', version)">基于该版本导出</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import type { DatasetVersionSummary } from '@/types/dataset-version'

defineProps<{
  visible: boolean
  version: DatasetVersionSummary | null
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  export: [version: DatasetVersionSummary]
  compare: [version: DatasetVersionSummary]
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
.hero-card {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  padding: 18px;
  border-radius: 16px;
  background: linear-gradient(135deg, #eff6ff, #f8fafc);
  border: 1px solid #dbeafe;
  margin-bottom: 20px;
}

.hero-title {
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
}

.hero-subtitle {
  margin-top: 8px;
  font-size: 13px;
  color: #64748b;
}

.section-block {
  margin-bottom: 16px;
}

.notes-text {
  color: #475569;
  line-height: 1.8;
}

.split-summary-line {
  margin-bottom: 12px;
  color: #0f172a;
  font-weight: 600;
}

.hint-list {
  display: grid;
  gap: 10px;
}

.hint-item {
  padding: 12px 14px;
  border-radius: 12px;
  background: #f8fafc;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
</style>
