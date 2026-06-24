<template>
  <div class="dataset-version-page">
    <div class="page-header">
      <div>
        <h3>数据集版本 / 导出记录</h3>
        <p class="page-subtitle">
          把训练前的数据冻结、导出和追溯流程接到真实后端，为后续训练和评估绑定稳定输入。
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
      @delete="handleDeleteVersion"
    />

    <DatasetExportRecordTable
      v-else
      :records="filteredExportRecords"
      @create="handleCreateExport"
      @detail="handleExportDetail"
      @download="handleExportDownload"
      @reuse="handleExportReuse"
      @delete="handleDeleteExport"
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDatasets } from '@/api/dataset'
import {
  createDatasetExport,
  deleteDatasetExport,
  deleteDatasetVersion,
  getDatasetExports,
  getDatasetVersions,
} from '@/api/datasetVersion'
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
  mapDatasetExportRecord,
  mapDatasetVersionSummary,
} from './datasetVersionValidation'

const router = useRouter()
const datasets = ref<Dataset[]>([])
const selectedDatasetId = ref('')
const activeView = ref<'versions' | 'exports'>('versions')
const detailVisible = ref(false)
const exportDialogVisible = ref(false)
const selectedVersion = ref<DatasetVersionSummary | null>(null)
const versionRows = ref<DatasetVersionSummary[]>([])
const exportRows = ref<DatasetExportRecord[]>([])

const overviewCards = computed<DatasetVersionOverviewCard[]>(() =>
  buildDatasetVersionOverviewCards(versionRows.value, exportRows.value.length),
)

const planItems = datasetVersionListPlanItems

const filteredVersions = computed(() =>
  versionRows.value.filter((item) => !selectedDatasetId.value || item.datasetId === selectedDatasetId.value),
)

const filteredExportRecords = computed(() =>
  exportRows.value.filter((item) => !selectedDatasetId.value || item.datasetId === selectedDatasetId.value),
)

onMounted(async () => {
  try {
    datasets.value = await getDatasets()
  } catch {
    datasets.value = []
  }
  await loadVersionData()
})

async function loadVersionData() {
  try {
    const [versions, exports] = await Promise.all([getDatasetVersions(), getDatasetExports()])
    versionRows.value = versions.map((item) =>
      mapDatasetVersionSummary(
        item,
        datasets.value.find((dataset) => dataset.id === item.dataset_id)?.name || '--',
      ),
    )
    exportRows.value = exports.map((item) => mapDatasetExportRecord(item, versionRows.value))
  } catch {
    versionRows.value = []
    exportRows.value = []
  }
}

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
      base: versionRows.value[1]?.id || row.id,
      target: row.id,
    },
  })
}

async function handleDeleteVersion(row: DatasetVersionSummary) {
  try {
    await ElMessageBox.confirm(
      `删除版本“${row.versionName}”后，关联导出记录也会一起删除，是否继续？`,
      '删除版本',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消',
      },
    )
    await deleteDatasetVersion(row.id)
    if (selectedVersion.value?.id === row.id) {
      selectedVersion.value = null
      detailVisible.value = false
      exportDialogVisible.value = false
    }
    ElMessage.success(`已删除版本：${row.versionName}`)
    await loadVersionData()
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    const message = error instanceof Error ? error.message : '删除版本失败'
    ElMessage.error(message)
  }
}

function handleCreateExport() {
  selectedVersion.value = filteredVersions.value[0] || null
  if (!selectedVersion.value) {
    ElMessage.warning('当前没有可用于导出的版本')
    return
  }
  exportDialogVisible.value = true
}

function handleExportDetail(row: DatasetExportRecord) {
  router.push(`/data/versions/exports/${row.id}`)
}

function handleExportDownload(row: DatasetExportRecord) {
  ElMessage.info(`导出目录：${row.outputPath}`)
}

function handleExportReuse(row: DatasetExportRecord) {
  const matchedVersion = versionRows.value.find((item) => item.versionName === row.versionName)
  if (matchedVersion) {
    selectedVersion.value = matchedVersion
    exportDialogVisible.value = true
    return
  }
  ElMessage.info(`未找到对应版本：${row.versionName}`)
}

async function handleDeleteExport(row: DatasetExportRecord) {
  try {
    await ElMessageBox.confirm(`确认删除导出记录“${row.exportName}”吗？`, '删除导出记录', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    await deleteDatasetExport(row.id)
    ElMessage.success(`已删除导出记录：${row.exportName}`)
    await loadVersionData()
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    const message = error instanceof Error ? error.message : '删除导出记录失败'
    ElMessage.error(message)
  }
}

function handleSaveDraft(draft: ExportDraft) {
  ElMessage.success(`导出草稿已保存：${draft.exportName}`)
}

async function handleSubmitExport(draft: ExportDraft) {
  if (!selectedVersion.value) {
    ElMessage.warning('当前没有可导出的数据集版本')
    return
  }
  try {
    await createDatasetExport(selectedVersion.value.id, {
      dataset_version_id: selectedVersion.value.id,
      export_name: draft.exportName,
      export_format: draft.exportFormat,
      splits: draft.splits,
      extras: draft.extras,
      notes: draft.notes,
    })
    ElMessage.success(`已创建导出记录：${draft.exportName}`)
    exportDialogVisible.value = false
    await loadVersionData()
  } catch (error) {
    const message = error instanceof Error ? error.message : '创建导出记录失败'
    ElMessage.error(message)
  }
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
