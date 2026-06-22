<template>
  <div class="dataset-version-validation">
    <div class="page-header">
      <div>
        <h3>版本校验结果</h3>
        <p class="page-subtitle">
          当前先展示训练前校验结果页面骨架，后续再接真实规则执行和阻断逻辑。
        </p>
      </div>
      <div class="header-actions">
        <el-button @click="goBack">返回版本列表</el-button>
        <el-button type="primary" @click="goCompare">查看版本对比</el-button>
      </div>
    </div>

    <el-card class="hero-card">
      <div class="hero-title">{{ version?.versionName || '--' }}</div>
      <div class="hero-subtitle">{{ version?.datasetName || '--' }}</div>
      <div class="hero-tags">
        <el-tag type="warning">当前为占位校验报告</el-tag>
        <el-tag type="info">后续接真实规则执行</el-tag>
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

    <el-card class="section-card">
      <template #header>校验项结果</template>
      <el-table :data="validationRows" border stripe>
        <el-table-column prop="rule" label="校验项" min-width="200" />
        <el-table-column label="结果" width="120">
          <template #default="{ row }">
            <el-tag :type="row.level === 'pass' ? 'success' : row.level === 'warn' ? 'warning' : 'danger'">
              {{ row.level === 'pass' ? '通过' : row.level === 'warn' ? '警告' : '阻断' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="summary" label="说明" min-width="320" />
        <el-table-column prop="action" label="后续动作" min-width="220" />
      </el-table>
    </el-card>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="section-card">
          <template #header>发现的问题</template>
          <div class="issue-list">
            <div v-for="item in issueList" :key="item" class="issue-item">{{ item }}</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="section-card">
          <template #header>后续扩展点</template>
          <div class="issue-list">
            <div v-for="item in extensionList" :key="item" class="issue-item">{{ item }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { findMockVersionById, mockDatasetVersions } from './datasetVersionMock'

const route = useRoute()
const router = useRouter()

const versionId = String(route.params.versionId || mockDatasetVersions[0]?.id || '')
const version = computed(() => findMockVersionById(versionId) || mockDatasetVersions[0] || null)

const summaryCards = computed(() => [
  { label: '阻断项', value: 1, help: '后续训练前应强制处理。' },
  { label: '警告项', value: 2, help: '不一定阻断，但应人工确认。' },
  { label: '通过项', value: 3, help: '可直接复用的版本特征。' },
  { label: '结论', value: '待处理', help: '当前版本默认不直接放行训练。' },
])

const validationRows = [
  {
    rule: '数据划分完整性',
    level: 'pass',
    summary: 'train / val / test 划分信息已存在。',
    action: '后续接入 split 级别样本数和占比校验。',
  },
  {
    rule: '空标注与空图片检查',
    level: 'warn',
    summary: '当前界面预留该项，后续应检查空标注图片和无效样本。',
    action: '支持跳转到标注问题修复页。',
  },
  {
    rule: '类别分布均衡性',
    level: 'warn',
    summary: '后续应检测类别过少或极度失衡场景。',
    action: '支持类别重采样建议或人工确认。',
  },
  {
    rule: '版本状态是否可训练',
    level: 'block',
    summary: '草稿或未校验完成版本默认阻断训练。',
    action: '通过后才允许进入训练配置页。',
  },
]

const issueList = [
  '当前页面还未接真实规则执行结果，只提供校验报告结构。',
  '后续应展示具体命中的文件、类别、split 和问题样本数量。',
  '校验结果最终应回写到版本状态和训练准入控制点。',
]

const extensionList = [
  '接入训练前校验规则引擎。',
  '支持按规则等级过滤结果。',
  '支持一键导出校验报告。',
  '支持从校验项跳转到数据集、标注或版本对比页。',
]

function goBack() {
  router.push('/data/versions')
}

function goCompare() {
  if (!version.value) {
    return
  }
  router.push({
    path: '/data/versions/compare',
    query: {
      base: mockDatasetVersions[1]?.id || version.value.id,
      target: version.value.id,
    },
  })
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

.issue-list {
  display: grid;
  gap: 10px;
}

.issue-item {
  padding: 12px 14px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #475569;
  line-height: 1.7;
}
</style>
