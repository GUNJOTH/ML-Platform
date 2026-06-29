<template>
  <div class="dataset-version-validation">
    <div class="page-header">
      <div>
        <h3>版本校验结果</h3>
        <p class="page-subtitle">展示该版本最新一次校验摘要，作为训练前是否可用的判断依据。</p>
      </div>
      <div class="header-actions">
        <el-button @click="goBack">返回版本列表</el-button>
        <el-button type="primary" @click="runValidation">重新校验</el-button>
      </div>
    </div>

    <el-card class="hero-card">
      <div class="hero-title">{{ version?.version_name || '--' }}</div>
      <div class="hero-subtitle">{{ datasetName }}</div>
      <div class="hero-tags">
        <el-tag :type="validationResult?.passed ? 'success' : 'danger'">
          {{ validationResult?.passed ? '可用于导出和训练' : '存在阻断问题，暂不可用' }}
        </el-tag>
        <el-tag type="info">{{ (version?.export_format || 'yolo').toUpperCase() }}</el-tag>
      </div>
    </el-card>

    <el-row :gutter="16" class="metric-row">
      <el-col :span="6" v-for="card in summaryCards" :key="card.label">
        <el-card class="metric-card">
          <div class="metric-label">{{ card.label }}</div>
          <div class="metric-value">{{ card.value }}</div>
          <div class="metric-help">{{ card.help }}</div>
        </el-card>
      </el-col>
    </el-row>

    <SplitPlanSummaryCard
      title="划分落地确认"
      :strategy-label="splitPlan.strategyLabel"
      :subtitle="splitPlan.subtitle"
      :items="splitPlan.items"
      :notes="splitPlan.notes"
      class="section-card"
    />

    <el-card class="section-card">
      <template #header>问题列表</template>
      <el-table :data="validationRows" border stripe>
        <el-table-column prop="rule" label="校验项" min-width="220" />
        <el-table-column label="级别" width="120">
          <template #default="{ row }">
            <el-tag :type="row.level === 'warning' ? 'warning' : row.level === 'error' ? 'danger' : 'success'">
              {{ row.level === 'warning' ? '警告' : row.level === 'error' ? '阻断' : '通过' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="summary" label="说明" min-width="360" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getDatasets } from '@/api/dataset'
import { getDatasetVersion, validateDatasetVersion } from '@/api/datasetVersion'
import type {
  DatasetVersionApiRecord,
  DatasetVersionValidationResult,
} from '@/types/dataset-version'
import SplitPlanSummaryCard from './components/SplitPlanSummaryCard.vue'
import {
  buildVersionSplitPlanSummary,
  getDatasetVersionIssueLabel,
} from './datasetVersionValidation'

const route = useRoute()
const router = useRouter()
const version = ref<DatasetVersionApiRecord | null>(null)
const validationResult = ref<DatasetVersionValidationResult | null>(null)
const datasetName = ref('--')

const summaryCards = computed(() => {
  const errors = validationResult.value?.errors.length || 0
  const warnings = validationResult.value?.warnings.length || 0
  const summary = validationResult.value?.summary || {}
  return [
    { label: '阻断项', value: errors, help: '必须先处理后才能继续导出或训练' },
    { label: '警告项', value: warnings, help: '不一定阻断，但建议先确认' },
    { label: '图片数', value: String(summary.image_count || 0), help: '当前版本纳入校验的图片总数' },
    { label: '标注框', value: String(summary.box_count || 0), help: '当前版本内的有效标注框数量' },
  ]
})

const splitPlan = computed(() =>
  buildVersionSplitPlanSummary({
    split_strategy: version.value?.split_strategy || 'reuse-existing',
    split_config: version.value?.split_config || {},
    stats_snapshot: {
      ...(version.value?.stats_snapshot || {}),
      split_counts: validationResult.value?.summary?.split_counts || version.value?.stats_snapshot?.split_counts || {},
    },
  }),
)

const validationRows = computed(() => {
  const rows = [
    ...(validationResult.value?.errors.map((item) => ({
      rule: getDatasetVersionIssueLabel(item.code),
      level: item.level,
      summary: item.message,
    })) || []),
    ...(validationResult.value?.warnings.map((item) => ({
      rule: getDatasetVersionIssueLabel(item.code),
      level: item.level,
      summary: item.message,
    })) || []),
  ]
  if (!rows.length) {
    rows.push({
      rule: '校验通过',
      level: 'pass',
      summary: '当前版本未发现阻断问题或警告项。',
    })
  }
  return rows
})

onMounted(async () => {
  await loadVersion()
})

async function loadVersion() {
  const versionId = String(route.params.versionId || '')
  if (!versionId) {
    return
  }
  version.value = await getDatasetVersion(versionId)
  validationResult.value = version.value.validation_summary || null
  try {
    const datasets = await getDatasets()
    datasetName.value =
      datasets.find((item) => item.id === version.value?.dataset_id)?.name || '--'
  } catch {
    datasetName.value = '--'
  }
}

async function runValidation() {
  const versionId = String(route.params.versionId || '')
  if (!versionId) {
    return
  }
  try {
    validationResult.value = await validateDatasetVersion(versionId)
    await loadVersion()
    ElMessage.success('版本校验已更新')
  } catch (error) {
    const message = error instanceof Error ? error.message : '版本校验失败'
    ElMessage.error(message)
  }
}

function goBack() {
  router.push('/data/versions')
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
.section-card,
.metric-card {
  border-radius: 16px;
}

.hero-card {
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

.metric-row {
  margin-bottom: 20px;
}

.metric-label {
  font-size: 13px;
  color: #64748b;
}

.metric-value {
  margin-top: 10px;
  font-size: 28px;
  font-weight: 700;
  color: #0f172a;
}

.metric-help {
  margin-top: 8px;
  font-size: 12px;
  color: #64748b;
}
</style>
