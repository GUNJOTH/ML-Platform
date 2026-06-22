<template>
  <div class="dataset-version-create">
    <div class="page-header">
      <div>
        <h3>新建数据集版本</h3>
        <p class="page-subtitle">
          先冻结训练前要用的数据快照，后续再接真实版本生成、校验和落库逻辑。
        </p>
      </div>
      <div class="header-actions">
        <el-button @click="goBack">返回版本列表</el-button>
        <el-button type="primary" @click="showPlaceholder('创建版本')">创建版本</el-button>
      </div>
    </div>

    <DatasetVersionPlanPanel :items="planItems" />

    <el-row :gutter="20">
      <el-col :span="15">
        <el-card class="section-card">
          <template #header>版本基础信息</template>
          <el-form label-width="110px">
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
                <el-radio-button label="COCO">COCO</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="版本说明">
              <el-input v-model="form.notes" type="textarea" :rows="4" />
            </el-form-item>
          </el-form>
        </el-card>

        <el-card class="section-card">
          <template #header>冻结范围与划分策略</template>
          <el-form label-width="110px">
            <el-form-item label="数据范围">
              <el-checkbox-group v-model="form.includeSplits">
                <el-checkbox label="train">train</el-checkbox>
                <el-checkbox label="val">val</el-checkbox>
                <el-checkbox label="test">test</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item label="划分策略">
              <el-radio-group v-model="form.splitStrategy">
                <el-radio label="reuse-existing">复用现有划分</el-radio>
                <el-radio label="manual-ratio">按比例冻结</el-radio>
                <el-radio label="manual-pick">人工指定</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="划分说明">
              <el-input
                v-model="form.splitSummary"
                placeholder="例如 train 70% / val 20% / test 10%"
              />
            </el-form-item>
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
      </el-col>

      <el-col :span="9">
        <el-card class="section-card">
          <template #header>版本预览</template>
          <div class="preview-grid">
            <div class="preview-item">
              <span class="preview-label">数据集</span>
              <span class="preview-value">{{ datasetName }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">版本名</span>
              <span class="preview-value">{{ form.versionName || '--' }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">来源</span>
              <span class="preview-value">{{ sourceLabel }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">训练格式</span>
              <span class="preview-value">{{ form.exportFormat }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">冻结范围</span>
              <span class="preview-value">{{ includeSplitText }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">划分策略</span>
              <span class="preview-value">{{ splitStrategyLabel }}</span>
            </div>
          </div>
        </el-card>

        <el-card class="section-card">
          <template #header>训练前校验预留</template>
          <div class="hint-list">
            <div v-for="hint in validationHints" :key="hint" class="hint-item">
              {{ hint }}
            </div>
          </div>
        </el-card>

        <el-card class="section-card">
          <template #header>界面阶段说明</template>
          <div class="phase-note">
            当前只搭建新建版本界面，不执行真实冻结逻辑。后续可以在这里接入：
            数据快照生成、版本校验、差异追踪和落库记录。
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { getDatasets } from '@/api/dataset'
import type { Dataset } from '@/types/dataset'
import DatasetVersionPlanPanel from './components/DatasetVersionPlanPanel.vue'
import {
  datasetVersionCreatePlanItems,
  datasetVersionCreateValidationHints,
} from './datasetVersionConfig'

const router = useRouter()
const datasets = ref<Dataset[]>([])

const form = reactive({
  datasetId: '',
  versionName: '',
  source: 'annotation-export',
  exportFormat: 'YOLO',
  notes: '',
  includeSplits: ['train', 'val', 'test'],
  splitStrategy: 'reuse-existing',
  splitSummary: 'train 70% / val 20% / test 10%',
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

const includeSplitText = computed(() =>
  form.includeSplits.length ? form.includeSplits.join(' / ') : '--',
)

const splitStrategyLabel = computed(() => {
  const map: Record<string, string> = {
    'reuse-existing': '复用现有划分',
    'manual-ratio': '按比例冻结',
    'manual-pick': '人工指定',
  }
  return map[form.splitStrategy] || form.splitStrategy
})

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

async function showPlaceholder(action: string) {
  await ElMessageBox.alert(
    `${action}功能暂未接后端逻辑。当前阶段先完成版本创建页面的信息结构和交互骨架。`,
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

.section-card {
  margin-bottom: 20px;
  border-radius: 16px;
}

.preview-grid {
  display: grid;
  gap: 12px;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 14px;
  border-radius: 12px;
  background: #f8fafc;
}

.preview-label {
  color: #64748b;
  font-size: 13px;
}

.preview-value {
  color: #0f172a;
  font-weight: 600;
  text-align: right;
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

.phase-note {
  color: #475569;
  line-height: 1.8;
}
</style>
