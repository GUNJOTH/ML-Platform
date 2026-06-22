<template>
  <div class="dataset-version-page">
    <div class="page-header">
      <div>
        <h3>数据集版本 / 导出记录</h3>
        <p class="page-subtitle">
          先把训练前的数据冻结、导出和追溯界面搭起来，后续再接真实版本与导出逻辑。
        </p>
      </div>
      <div class="header-actions">
        <el-button @click="goRules">版本规则</el-button>
        <el-button type="primary" @click="goCreateVersion">新建版本</el-button>
      </div>
    </div>

    <DatasetVersionOverviewCards :cards="overviewCards" />
    <DatasetVersionPlanPanel :items="planItems" />

    <el-card class="filter-card">
      <el-form inline>
        <el-form-item label="数据集">
          <el-select
            v-model="selectedDatasetId"
            clearable
            placeholder="筛选数据集"
            style="width: 220px"
          >
            <el-option
              v-for="dataset in datasets"
              :key="dataset.id"
              :label="dataset.name"
              :value="dataset.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="视图">
          <el-radio-group v-model="activeView">
            <el-radio-button label="versions">版本列表</el-radio-button>
            <el-radio-button label="exports">导出记录</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </el-card>

    <DatasetVersionTable
      v-if="activeView === 'versions'"
      :versions="filteredVersions"
      @create="goCreateVersion"
      @detail="handleVersionDetail"
      @export="handleVersionExport"
      @compare="handleVersionCompare"
    />

    <DatasetExportRecordTable
      v-else
      :records="filteredExportRecords"
      @create="handleCreateExport"
      @detail="handleExportDetail"
      @download="handleExportDownload"
      @reuse="handleExportReuse"
    />

    <DatasetVersionDetailDrawer
      v-model:visible="detailVisible"
      :version="selectedVersion"
      @export="handleVersionExport"
      @compare="handleVersionCompare"
    />

    <DatasetExportCreateDialog
      v-model:visible="exportDialogVisible"
      :version="selectedVersion"
      :dataset-name="selectedVersion?.datasetName || '--'"
      @submit="handleSubmitExport"
      @save-draft="handleSaveDraft"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getDatasets } from '@/api/dataset'
import type { Dataset } from '@/types/dataset'
import type {
  DatasetExportRecord,
  DatasetVersionOverviewCard,
  DatasetVersionSummary,
  ExportDraft,
} from '@/types/dataset-version'
import DatasetExportCreateDialog from './components/DatasetExportCreateDialog.vue'
import DatasetExportRecordTable from './components/DatasetExportRecordTable.vue'
import DatasetVersionDetailDrawer from './components/DatasetVersionDetailDrawer.vue'
import DatasetVersionOverviewCards from './components/DatasetVersionOverviewCards.vue'
import DatasetVersionPlanPanel from './components/DatasetVersionPlanPanel.vue'
import DatasetVersionTable from './components/DatasetVersionTable.vue'
import {
  buildDatasetVersionOverviewCards,
  datasetVersionListPlanItems,
} from './datasetVersionConfig'
import {
  findMockVersionByName,
  mockDatasetExportRecords,
  mockDatasetVersions,
} from './datasetVersionMock'

const router = useRouter()
const datasets = ref<Dataset[]>([])
const selectedDatasetId = ref('')
const activeView = ref<'versions' | 'exports'>('versions')
const detailVisible = ref(false)
const exportDialogVisible = ref(false)
const selectedVersion = ref<DatasetVersionSummary | null>(null)
const mockVersions = ref<DatasetVersionSummary[]>(mockDatasetVersions)
const mockExportRecords = ref<DatasetExportRecord[]>(mockDatasetExportRecords)

const overviewCards = computed<DatasetVersionOverviewCard[]>(() =>
  buildDatasetVersionOverviewCards(mockVersions.value, mockExportRecords.value.length),
)

const planItems = datasetVersionListPlanItems

const filteredVersions = computed(() =>
  mockVersions.value.filter((item) => !selectedDatasetId.value || item.datasetId === selectedDatasetId.value),
)

const filteredExportRecords = computed(() =>
  mockExportRecords.value.filter((item) => !selectedDatasetId.value || item.datasetId === selectedDatasetId.value),
)

onMounted(async () => {
  try {
    datasets.value = await getDatasets()
  } catch {
    datasets.value = []
  }
})

function goRules() {
  router.push('/data/versions/rules')
}

function goCreateVersion() {
  router.push('/data/versions/new')
}

function handleVersionDetail(row: DatasetVersionSummary) {
  selectedVersion.value = row
  detailVisible.value = true
}

function handleVersionExport(row: DatasetVersionSummary) {
  selectedVersion.value = row
  exportDialogVisible.value = true
}

function handleVersionCompare(row: DatasetVersionSummary) {
  router.push({
    path: '/data/versions/compare',
    query: {
      base: mockVersions.value[1]?.id || row.id,
      target: row.id,
    },
  })
}

function handleCreateExport() {
  selectedVersion.value = filteredVersions.value[0] || null
  if (!selectedVersion.value) {
    ElMessage.warning('当前没有可用于演示的版本数据')
    return
  }
  exportDialogVisible.value = true
}

function handleExportDetail(row: DatasetExportRecord) {
  router.push(`/data/versions/exports/${row.id}`)
}

function handleExportDownload(row: DatasetExportRecord) {
  ElMessage.info(`已预留下载入口：${row.exportName}`)
}

function handleExportReuse(row: DatasetExportRecord) {
  const matchedVersion = findMockVersionByName(row.versionName)
  if (matchedVersion) {
    selectedVersion.value = matchedVersion
    exportDialogVisible.value = true
    return
  }
  ElMessage.info(`已预留复用入口：${row.exportName}`)
}

function handleSaveDraft(draft: ExportDraft) {
  ElMessage.success(`导出草稿已保存：${draft.exportName}`)
}

function handleSubmitExport(draft: ExportDraft) {
  ElMessage.success(`已预演导出流程：${draft.exportName}`)
  exportDialogVisible.value = false
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

.filter-card {
  margin-bottom: 20px;
  border-radius: 16px;
}
</style>
