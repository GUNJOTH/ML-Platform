<template>
  <div class="dataset-version-compare">
    <div class="page-header">
      <div>
        <h3>数据集版本对比</h3>
        <p class="page-subtitle">
          先把版本差异视图搭起来，后续再接真实样本差异、类别分布变化和校验结果对比。
        </p>
      </div>
      <div class="header-actions">
        <el-button @click="goBack">返回版本列表</el-button>
        <el-button type="primary" @click="showPlaceholder('导出对比报告')">导出对比报告</el-button>
      </div>
    </div>

    <el-card class="filter-card">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="基准版本">
            <el-select v-model="baseVersionId" placeholder="选择基准版本" style="width: 100%">
              <el-option
                v-for="version in versions"
                :key="version.id"
                :label="version.versionName"
                :value="version.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="目标版本">
            <el-select v-model="targetVersionId" placeholder="选择目标版本" style="width: 100%">
              <el-option
                v-for="version in versions"
                :key="version.id"
                :label="version.versionName"
                :value="version.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="16" class="metric-row">
      <el-col :span="6" v-for="card in compareCards" :key="card.label">
        <el-card class="metric-card">
          <div class="metric-label">{{ card.label }}</div>
          <div class="metric-value">{{ card.current }}</div>
          <div class="metric-diff" :class="{ positive: card.diff.startsWith('+'), negative: card.diff.startsWith('-') }">
            {{ card.diff }} vs 基准版本
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="section-card">
          <template #header>版本信息对照</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="基准版本">
              {{ baseVersion?.versionName || '--' }}
            </el-descriptions-item>
            <el-descriptions-item label="目标版本">
              {{ targetVersion?.versionName || '--' }}
            </el-descriptions-item>
            <el-descriptions-item label="数据划分">
              {{ baseVersion?.splitSummary || '--' }} -> {{ targetVersion?.splitSummary || '--' }}
            </el-descriptions-item>
            <el-descriptions-item label="训练格式">
              {{ baseVersion?.exportFormat || '--' }} -> {{ targetVersion?.exportFormat || '--' }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              {{ baseVersion?.status || '--' }} -> {{ targetVersion?.status || '--' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="section-card">
          <template #header>重点变化摘要</template>
          <div class="summary-list">
            <div v-for="item in summaryItems" :key="item" class="summary-item">{{ item }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="section-card">
      <template #header>类别分布对比</template>
      <el-table :data="classCompareRows" border stripe>
        <el-table-column prop="className" label="类别" min-width="180" />
        <el-table-column prop="baseCount" label="基准版本实例数" width="160" />
        <el-table-column prop="targetCount" label="目标版本实例数" width="160" />
        <el-table-column prop="delta" label="变化量" width="120" />
        <el-table-column prop="targetRatio" label="目标版本占比" width="140" />
      </el-table>
    </el-card>

    <el-card class="section-card">
      <template #header>训练前校验预留对比</template>
      <div class="placeholder-grid">
        <div class="placeholder-item">空标注差异</div>
        <div class="placeholder-item">类别失衡变化</div>
        <div class="placeholder-item">划分缺失变化</div>
        <div class="placeholder-item">异常样本增量</div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { mockDatasetVersions } from './datasetVersionMock'

const route = useRoute()
const router = useRouter()
const versions = mockDatasetVersions

const defaultBaseVersionId = String(route.query.base || versions[1]?.id || versions[0]?.id || '')
const defaultTargetVersionId = String(route.query.target || versions[0]?.id || '')

const baseVersionId = ref(defaultBaseVersionId)
const targetVersionId = ref(defaultTargetVersionId)

const baseVersion = computed(() => versions.find((item) => item.id === baseVersionId.value) || null)
const targetVersion = computed(() => versions.find((item) => item.id === targetVersionId.value) || null)

const compareCards = computed(() => {
  const base = baseVersion.value
  const target = targetVersion.value
  if (!base || !target) {
    return []
  }
  return [
    buildCard('图像数', base.imageCount, target.imageCount),
    buildCard('标注数', base.annotationCount, target.annotationCount),
    buildCard('类别数', base.classCount, target.classCount),
    buildCard('平均标注密度', density(base), density(target), true),
  ]
})

const summaryItems = computed(() => {
  const base = baseVersion.value
  const target = targetVersion.value
  if (!base || !target) {
    return []
  }
  return [
    `目标版本比基准版本增加 ${target.imageCount - base.imageCount} 张图片。`,
    `目标版本比基准版本增加 ${target.annotationCount - base.annotationCount} 条标注。`,
    `当前界面已预留后续样本级 diff、类别覆盖率和训练前校验对比。`,
  ]
})

const classCompareRows = computed(() => {
  const baseRows = baseVersion.value?.classDistribution || []
  const targetRows = targetVersion.value?.classDistribution || []
  return targetRows.map((targetRow) => {
    const baseRow = baseRows.find((item) => item.className === targetRow.className)
    const baseCount = baseRow?.count || 0
    const delta = targetRow.count - baseCount
    return {
      className: targetRow.className,
      baseCount,
      targetCount: targetRow.count,
      delta: delta > 0 ? `+${delta}` : String(delta),
      targetRatio: targetRow.ratio,
    }
  })
})

function density(version: { annotationCount: number; imageCount: number }): number {
  if (!version.imageCount) {
    return 0
  }
  return Number((version.annotationCount / version.imageCount).toFixed(2))
}

function buildCard(label: string, base: number, current: number, keepDecimal = false) {
  const diff = current - base
  const currentText = keepDecimal ? current.toFixed(2) : String(current)
  const diffText = `${diff > 0 ? '+' : ''}${keepDecimal ? diff.toFixed(2) : diff}`
  return {
    label,
    current: currentText,
    diff: diffText,
  }
}

function goBack() {
  router.push('/data/versions')
}

async function showPlaceholder(action: string) {
  await ElMessageBox.alert(
    `${action}功能暂未接真实逻辑。当前阶段先把版本对比页面结构搭好。`,
    '占位说明',
    { confirmButtonText: '知道了' },
  )
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

.filter-card,
.section-card {
  margin-bottom: 20px;
  border-radius: 16px;
}

.metric-row {
  margin-bottom: 20px;
}

.metric-card {
  border-radius: 14px;
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

.metric-diff {
  margin-top: 8px;
  font-size: 12px;
  color: #64748b;
}

.metric-diff.positive {
  color: #15803d;
}

.metric-diff.negative {
  color: #b91c1c;
}

.summary-list {
  display: grid;
  gap: 10px;
}

.summary-item,
.placeholder-item {
  padding: 12px 14px;
  border-radius: 12px;
  background: #f8fafc;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.placeholder-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}
</style>
