<template>
  <div class="evaluation-page">
    <div class="page-header">
      <h3>模型评估</h3>
    </div>

    <el-row :gutter="20" class="config-row">
      <el-col :span="8">
        <el-card>
          <template #header>评估配置</template>
          <el-form label-width="80px">
            <el-form-item label="模型">
              <el-select v-model="selectedModel" placeholder="选择模型" style="width: 100%">
                <el-option v-for="m in models" :key="m.id" :label="m.name" :value="m.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="数据集">
              <el-select v-model="selectedDataset" placeholder="选择数据集" style="width: 100%">
                <el-option v-for="d in datasets" :key="d.id" :label="d.name" :value="d.id" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="startEval">
                开始评估
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card v-if="metrics">
          <template #header>评估结果</template>
          <el-row :gutter="16">
            <el-col :span="6" v-for="item in metricCards" :key="item.label">
              <div class="metric-card">
                <span class="metric-label">{{ item.label }}</span>
                <span class="metric-value">{{ item.value }}</span>
              </div>
            </el-col>
          </el-row>
        </el-card>
        <el-card v-else>
          <div class="empty-hint">选择模型和数据集后开始评估</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getModels } from '@/api/model'
import { getDatasets } from '@/api/dataset'
import { runEvaluation } from '@/api/inference'

interface ModelItem { id: string; name: string }
interface DatasetItem { id: string; name: string }
interface Metrics { map50: number; map50_95: number; precision: number; recall: number }

const models = ref<ModelItem[]>([])
const datasets = ref<DatasetItem[]>([])
const selectedModel = ref('')
const selectedDataset = ref('')
const loading = ref(false)
const metrics = ref<Metrics | null>(null)

const metricCards = computed(() => {
  if (!metrics.value) return []
  return [
    { label: 'mAP50', value: (metrics.value.map50 * 100).toFixed(1) + '%' },
    { label: 'mAP50-95', value: (metrics.value.map50_95 * 100).toFixed(1) + '%' },
    { label: 'Precision', value: (metrics.value.precision * 100).toFixed(1) + '%' },
    { label: 'Recall', value: (metrics.value.recall * 100).toFixed(1) + '%' },
  ]
})

onMounted(async () => {
  const [m, d] = await Promise.all([getModels(), getDatasets()])
  models.value = m as unknown as ModelItem[]
  datasets.value = d as unknown as DatasetItem[]
})

async function startEval() {
  if (!selectedModel.value || !selectedDataset.value) return
  loading.value = true
  try {
    const res = await runEvaluation({
      model_id: selectedModel.value,
      dataset_id: selectedDataset.value,
    }) as unknown as { result: Metrics }
    metrics.value = res.result
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-header {
  margin-bottom: 16px;
}
.config-row {
  margin-bottom: 20px;
}
.metric-card {
  text-align: center;
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 8px;
}
.metric-label {
  display: block;
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}
.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}
.empty-hint {
  text-align: center;
  color: #999;
  padding: 40px;
}
</style>
