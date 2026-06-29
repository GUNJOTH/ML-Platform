<template>
  <div class="dataset-version-create">
    <div class="page-header">
      <div>
        <h3>新建数据集版本</h3>
        <p class="page-subtitle">
          先校验当前冻结范围是否可用于训练，再正式创建版本，并把训练集 / 验证集 / 测试集策略一并冻结下来。
        </p>
      </div>
      <div class="header-actions">
        <el-button @click="goBack">返回版本列表</el-button>
        <el-button :loading="validating" @click="handleValidateDraft">先校验</el-button>
        <el-button type="primary" :disabled="!validationPassed" :loading="creating" @click="handleCreateVersion">
          校验通过后创建版本
        </el-button>
      </div>
    </div>

    <DatasetVersionPlanPanel :items="planItems" />

    <el-row :gutter="20">
      <el-col :span="15">
        <el-card class="section-card">
          <template #header>版本基础信息</template>
          <el-form label-width="120px">
            <el-form-item label="来源数据集">
              <el-select v-model="form.datasetId" placeholder="选择来源数据集" style="width: 100%">
                <el-option
                  v-for="dataset in datasets"
                  :key="dataset.id"
                  :label="dataset.name"
                  :value="dataset.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="版本名称">
              <el-input v-model="form.versionName" placeholder="例如 smoke_v4_freeze" />
            </el-form-item>
            <el-form-item label="冻结来源">
              <el-radio-group v-model="form.source">
                <el-radio-button label="annotation-export">标注导出</el-radio-button>
                <el-radio-button label="imported">外部导入</el-radio-button>
                <el-radio-button label="manual-freeze">手动冻结</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="训练格式">
              <el-radio-group v-model="form.exportFormat">
                <el-radio-button label="YOLO">YOLO</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="版本说明">
              <el-input v-model="form.notes" type="textarea" :rows="4" />
            </el-form-item>
          </el-form>
        </el-card>

        <el-card class="section-card">
          <template #header>训练划分策略</template>
          <el-form label-width="120px">
            <el-form-item label="导出目标划分">
              <el-checkbox-group v-model="form.includeSplits">
                <el-checkbox label="train">train</el-checkbox>
                <el-checkbox label="val">val</el-checkbox>
                <el-checkbox label="test">test</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="划分策略">
              <el-radio-group v-model="form.splitStrategy">
                <el-radio label="reuse-existing">复用现有划分</el-radio>
                <el-radio label="auto-ratio">按比例自动划分</el-radio>
              </el-radio-group>
            </el-form-item>

            <template v-if="form.splitStrategy === 'auto-ratio'">
              <el-form-item label="划分样本来源">
                <el-checkbox-group v-model="form.scopeSplits">
                  <el-checkbox label="train">train</el-checkbox>
                  <el-checkbox label="val">val</el-checkbox>
                  <el-checkbox label="test">test</el-checkbox>
                </el-checkbox-group>
                <div class="form-hint">
                  自动划分会先从你选择的来源范围里汇总图片，再按比例冻结到 train / val / test。
                </div>
              </el-form-item>
              <el-form-item label="train 比例">
                <el-input-number v-model="form.trainRatio" :min="0.01" :max="0.98" :step="0.01" :precision="2" />
              </el-form-item>
              <el-form-item label="val 比例">
                <el-input-number v-model="form.valRatio" :min="0.01" :max="0.98" :step="0.01" :precision="2" />
              </el-form-item>
              <el-form-item label="test 比例">
                <el-input-number v-model="form.testRatio" :min="0.01" :max="0.98" :step="0.01" :precision="2" />
              </el-form-item>
              <el-form-item label="随机种子">
                <el-input-number v-model="form.randomSeed" :min="1" :max="999999" :step="1" />
              </el-form-item>
            </template>

            <el-form-item label="附带资源">
              <el-checkbox-group v-model="form.includeAssets">
                <el-checkbox label="images">原图</el-checkbox>
                <el-checkbox label="labels">标注</el-checkbox>
                <el-checkbox label="manifest">清单</el-checkbox>
                <el-checkbox label="stats">统计摘要</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-form>
        </el-card>

        <DatasetVersionValidationIssuesCard
          title="创建前校验结果"
          empty-text="请先点击“先校验”，确认当前版本范围和划分策略是否可用。"
          success-text="校验通过，可创建版本"
          failure-text="校验未通过，暂不能创建版本"
          :validation-result="validationResult"
        />
      </el-col>

      <el-col :span="9">
        <DatasetVersionPreviewCard
          :dataset-name="datasetName"
          :version-name="form.versionName"
          :source-label="sourceLabel"
          :export-format="form.exportFormat"
          :include-split-text="includeSplitText"
          :split-strategy-label="splitStrategyLabel"
          :split-plan-text="splitPlanText"
        />

        <SplitPlanSummaryCard
          title="划分落地确认"
          :strategy-label="draftSplitPlan.strategyLabel"
          :subtitle="draftSplitPlan.subtitle"
          :items="draftSplitPlan.items"
          :notes="draftSplitPlan.notes"
        />

        <el-card class="section-card">
          <template #header>训练前检查提示</template>
          <div class="hint-list">
            <div v-for="hint in validationHints" :key="hint" class="hint-item">
              {{ hint }}
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDatasets } from '@/api/dataset'
import { createDatasetVersion, validateDatasetVersionDraft } from '@/api/datasetVersion'
import type { Dataset } from '@/types/dataset'
import type { DatasetVersionValidationResult } from '@/types/dataset-version'
import DatasetVersionPlanPanel from './components/DatasetVersionPlanPanel.vue'
import DatasetVersionPreviewCard from './components/DatasetVersionPreviewCard.vue'
import SplitPlanSummaryCard from './components/SplitPlanSummaryCard.vue'
import DatasetVersionValidationIssuesCard from './components/DatasetVersionValidationIssuesCard.vue'
import {
  buildDatasetVersionPayload,
  buildVersionSplitPlanSummary,
  buildDatasetVersionValidationFingerprint,
  formatAutoRatioSummary,
  getSplitStrategyLabel,
  type DatasetVersionCreateFormState,
} from './datasetVersionValidation'
import {
  datasetVersionCreatePlanItems,
  datasetVersionCreateValidationHints,
} from './datasetVersionConfig'

const router = useRouter()
const datasets = ref<Dataset[]>([])
const validating = ref(false)
const creating = ref(false)
const validationResult = ref<DatasetVersionValidationResult | null>(null)
const validationFingerprint = ref('')

const form = reactive<DatasetVersionCreateFormState>({
  datasetId: '',
  versionName: '',
  source: 'annotation-export',
  exportFormat: 'YOLO',
  notes: '',
  includeSplits: ['train', 'val', 'test'],
  splitStrategy: 'reuse-existing',
  trainRatio: 0.8,
  valRatio: 0.1,
  testRatio: 0.1,
  randomSeed: 42,
  scopeSplits: ['train', 'val', 'test'],
  includeAssets: ['images', 'labels', 'manifest'],
})

const planItems = datasetVersionCreatePlanItems
const validationHints = datasetVersionCreateValidationHints

const datasetName = computed(
  () => datasets.value.find((item) => item.id === form.datasetId)?.name || '--',
)

const sourceLabel = computed(() => {
  const map: Record<string, string> = {
    'annotation-export': '标注导出',
    imported: '外部导入',
    'manual-freeze': '手动冻结',
  }
  return map[form.source] || form.source
})

const includeSplitText = computed(() => {
  if (form.splitStrategy === 'auto-ratio') {
    return `${form.includeSplits.join(' / ') || '--'} | ${formatAutoRatioSummary(form)}`
  }
  return form.includeSplits.length ? form.includeSplits.join(' / ') : '--'
})

const splitStrategyLabel = computed(() => getSplitStrategyLabel(form.splitStrategy))

const draftSplitPlan = computed(() =>
  buildVersionSplitPlanSummary({
    split_strategy: form.splitStrategy,
    split_config:
      form.splitStrategy === 'auto-ratio'
        ? {
            scope_splits: form.scopeSplits,
            train_ratio: form.trainRatio,
            val_ratio: form.valRatio,
            test_ratio: form.testRatio,
            random_seed: form.randomSeed,
          }
        : {
            scope_splits: form.includeSplits,
          },
    stats_snapshot: {
      split_counts: validationResult.value?.summary?.split_counts || {},
    },
  }),
)

const splitPlanText = computed(() =>
  draftSplitPlan.value.items
    .map((item) => `${item.split} ${item.count}`)
    .join(' / '),
)

const validationPassed = computed(() => {
  return (
    Boolean(validationResult.value?.passed) &&
    validationFingerprint.value === buildDatasetVersionValidationFingerprint(form)
  )
})

watch(
  () => buildDatasetVersionValidationFingerprint(form),
  (value) => {
    if (validationFingerprint.value && validationFingerprint.value !== value) {
      validationResult.value = null
      validationFingerprint.value = ''
    }
  },
)

watch(
  () => form.splitStrategy,
  (strategy) => {
    if (strategy === 'reuse-existing') {
      form.scopeSplits = ['train', 'val', 'test']
    }
  },
)

onMounted(async () => {
  try {
    datasets.value = await getDatasets()
    if (datasets.value.length) {
      form.datasetId = datasets.value[0].id
    }
  } catch {
    datasets.value = []
  }
})

function goBack() {
  router.push('/data/versions')
}

function validateFormBeforeRemoteCheck(): string | null {
  if (!form.datasetId || !form.versionName.trim()) {
    return '请选择数据集并填写版本名称'
  }
  if (!form.includeSplits.length) {
    return '请至少选择一个导出目标划分'
  }
  if (form.splitStrategy === 'auto-ratio') {
    if (!form.scopeSplits.length) {
      return '自动划分时，至少需要选择一个划分样本来源'
    }
    if (form.trainRatio <= 0 || form.valRatio <= 0 || form.testRatio <= 0) {
      return '自动划分比例必须都大于 0'
    }
  }
  return null
}

async function handleValidateDraft() {
  const localError = validateFormBeforeRemoteCheck()
  if (localError) {
    ElMessage.warning(localError)
    return
  }

  validating.value = true
  try {
    validationResult.value = await validateDatasetVersionDraft(buildDatasetVersionPayload(form))
    validationFingerprint.value = buildDatasetVersionValidationFingerprint(form)
    if (validationResult.value.passed) {
      ElMessage.success('校验通过，可以创建版本')
    } else {
      ElMessage.warning('校验未通过，请先处理阻断项')
    }
  } catch (error: unknown) {
    validationResult.value = null
    validationFingerprint.value = ''
    const message = error instanceof Error ? error.message : '版本校验失败'
    ElMessage.error(message)
  } finally {
    validating.value = false
  }
}

async function handleCreateVersion() {
  const localError = validateFormBeforeRemoteCheck()
  if (localError) {
    ElMessage.warning(localError)
    return
  }
  if (!validationPassed.value) {
    ElMessage.warning('请先完成当前表单的版本校验，并确认校验通过')
    return
  }

  creating.value = true
  try {
    const version = await createDatasetVersion(buildDatasetVersionPayload(form))
    ElMessage.success('数据集版本已创建')
    router.push(`/data/versions/validation/${version.id}`)
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : '创建数据集版本失败'
    await ElMessageBox.alert(message, '创建失败', { confirmButtonText: '知道了' })
  } finally {
    creating.value = false
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

.section-card {
  margin-bottom: 20px;
  border-radius: 16px;
}

.form-hint {
  margin-top: 8px;
  color: #64748b;
  font-size: 12px;
  line-height: 1.6;
}

.hint-list {
  display: grid;
  gap: 10px;
}

.hint-item {
  padding: 12px 14px;
  border-radius: 12px;
  background: linear-gradient(135deg, #eff6ff, #f8fafc);
  border: 1px solid #dbeafe;
  color: #475569;
}
</style>
