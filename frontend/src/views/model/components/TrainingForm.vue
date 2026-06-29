<template>
  <el-dialog v-model="visible" title="创建训练任务" width="640px">
    <el-form :model="form" label-width="120px">
      <el-form-item label="任务名称" required>
        <el-input v-model="form.name" placeholder="输入任务名称" />
      </el-form-item>

      <el-form-item label="所属数据集" required>
        <el-select
          v-model="form.dataset_id"
          placeholder="选择原始数据集"
          style="width: 100%"
        >
          <el-option
            v-for="dataset in datasets"
            :key="dataset.id"
            :label="dataset.name"
            :value="dataset.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="来源版本筛选">
        <el-select
          v-model="form.dataset_version_id"
          placeholder="可选：按数据集版本筛选导出记录"
          style="width: 100%"
          clearable
        >
          <el-option
            v-for="version in filteredVersions"
            :key="version.id"
            :label="version.version_name"
            :value="version.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="训练输入数据" required>
        <el-select
          v-model="form.dataset_export_id"
          placeholder="选择已成功导出的训练输入"
          style="width: 100%"
        >
          <el-option
            v-for="record in filteredExports"
            :key="record.id"
            :label="formatExportOptionLabel(record)"
            :value="record.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="预训练模型" required>
        <el-select
          v-model="form.model_id"
          placeholder="选择预训练模型"
          style="width: 100%"
        >
          <el-option
            v-for="model in pretrainedModels"
            :key="model.id"
            :label="`${model.name}${model.version ? ` (${model.version})` : ''}`"
            :value="model.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="Epochs" required>
        <el-input-number v-model="form.epochs" :min="1" :max="500" />
      </el-form-item>

      <el-collapse>
        <el-collapse-item title="高级配置">
          <el-form-item label="Batch Size">
            <el-input-number v-model="form.batch_size" :min="1" :max="128" />
          </el-form-item>
          <el-form-item label="图片尺寸">
            <el-input-number
              v-model="form.img_size"
              :min="320"
              :max="1280"
              :step="32"
            />
          </el-form-item>
          <el-form-item label="早停 Patience">
            <el-input-number v-model="form.patience" :min="0" :max="100" />
          </el-form-item>
          <el-form-item label="优化器">
            <el-select v-model="form.optimizer" style="width: 100%">
              <el-option label="AdamW" value="AdamW" />
              <el-option label="SGD" value="SGD" />
            </el-select>
          </el-form-item>
          <el-form-item label="学习率">
            <el-input-number
              v-model="form.lr0"
              :min="0.0001"
              :max="0.1"
              :step="0.001"
              :precision="4"
            />
          </el-form-item>
          <el-form-item label="Warmup Epochs">
            <el-input-number v-model="form.warmup_epochs" :min="0" :max="10" />
          </el-form-item>
          <el-form-item label="Device">
            <el-select v-model="form.device" style="width: 100%">
              <el-option label="Auto" value="auto" />
              <el-option label="CUDA" value="cuda" />
              <el-option label="CUDA:0" value="cuda:0" />
              <el-option label="CPU" value="cpu" />
            </el-select>
          </el-form-item>
          <el-form-item label="Workers">
            <el-input-number v-model="form.workers" :min="0" :max="16" />
          </el-form-item>
          <el-form-item label="余弦学习率">
            <el-switch v-model="form.cos_lr" />
          </el-form-item>
          <el-form-item label="Close Mosaic">
            <el-input-number v-model="form.close_mosaic" :min="0" :max="50" />
          </el-form-item>
          <el-form-item label="使用预训练">
            <el-switch v-model="form.pretrained" />
          </el-form-item>
        </el-collapse-item>
      </el-collapse>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">
        创建并开始训练
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getDatasets } from '@/api/dataset'
import { getDatasetExports, getDatasetVersions } from '@/api/datasetVersion'
import { getModels } from '@/api/model'
import { createTask, startTask } from '@/api/task'
import type { Dataset } from '@/types/dataset'
import type {
  DatasetExportRecordDetail,
  DatasetVersionApiRecord,
} from '@/types/dataset-version'
import type { MLModel } from '@/types/model'

interface TrainingTaskFormState {
  name: string
  dataset_id: string
  dataset_version_id: string
  dataset_export_id: string
  model_id: string
  epochs: number
  batch_size: number
  img_size: number
  patience: number
  workers: number | null
  device: 'auto' | 'cpu' | 'cuda' | 'cuda:0'
  optimizer: 'AdamW' | 'SGD'
  lr0: number
  warmup_epochs: number
  cos_lr: boolean
  close_mosaic: number
  pretrained: boolean
}

const visible = defineModel<boolean>({ required: true })
const emit = defineEmits<{ created: [taskId: string] }>()

const datasets = ref<Dataset[]>([])
const pretrainedModels = ref<MLModel[]>([])
const datasetVersions = ref<DatasetVersionApiRecord[]>([])
const datasetExports = ref<DatasetExportRecordDetail[]>([])

const form = reactive<TrainingTaskFormState>({
  name: '',
  dataset_id: '',
  dataset_version_id: '',
  dataset_export_id: '',
  model_id: '',
  epochs: 50,
  batch_size: 16,
  img_size: 640,
  patience: 10,
  workers: null,
  device: 'auto',
  optimizer: 'AdamW',
  lr0: 0.01,
  warmup_epochs: 3,
  cos_lr: false,
  close_mosaic: 10,
  pretrained: true,
})

const filteredVersions = computed(() =>
  datasetVersions.value.filter(
    (item) => !form.dataset_id || item.dataset_id === form.dataset_id,
  ),
)

const filteredExports = computed(() =>
  datasetExports.value.filter(
    (item) =>
      item.status === 'success' &&
      (!form.dataset_id || item.dataset_id === form.dataset_id) &&
      (!form.dataset_version_id ||
        item.dataset_version_id === form.dataset_version_id),
  ),
)

watch(
  () => form.dataset_id,
  () => {
    form.dataset_version_id = ''
    form.dataset_export_id = ''
  },
)

watch(
  () => form.dataset_version_id,
  () => {
    form.dataset_export_id = ''
  },
)

onMounted(async () => {
  await Promise.all([
    loadDatasets(),
    loadPretrainedModels(),
    loadDatasetVersions(),
    loadDatasetExports(),
  ])
})

async function loadDatasets() {
  try {
    datasets.value = (await getDatasets()) || []
  } catch {
    datasets.value = []
  }
}

async function loadPretrainedModels() {
  try {
    pretrainedModels.value = (await getModels({ source: 'pretrained' })) || []
  } catch {
    pretrainedModels.value = []
  }
}

async function loadDatasetVersions() {
  try {
    datasetVersions.value = await getDatasetVersions()
  } catch {
    datasetVersions.value = []
  }
}

async function loadDatasetExports() {
  try {
    datasetExports.value = await getDatasetExports()
  } catch {
    datasetExports.value = []
  }
}

function formatExportOptionLabel(record: DatasetExportRecordDetail): string {
  return `${record.export_name} (${String(record.export_format).toUpperCase()})`
}

async function handleSubmit() {
  if (!form.dataset_id) {
    ElMessage.warning('请选择所属数据集')
    return
  }
  if (!form.dataset_export_id) {
    ElMessage.warning('请选择训练输入数据')
    return
  }
  if (!form.model_id) {
    ElMessage.warning('请选择预训练模型')
    return
  }

  const config = {
    epochs: form.epochs,
    batch_size: form.batch_size,
    img_size: form.img_size,
    patience: form.patience,
    workers: form.workers,
    device: form.device === 'auto' ? undefined : form.device,
    optimizer: form.optimizer,
    lr0: form.lr0,
    warmup_epochs: form.warmup_epochs,
    cos_lr: form.cos_lr,
    close_mosaic: form.close_mosaic,
    pretrained: form.pretrained,
    framework: 'ultralytics',
  }

  try {
    const task = await createTask({
      name: form.name || `training_${form.epochs}e`,
      task_type: 'training',
      model_id: form.model_id,
      dataset_id: form.dataset_id,
      dataset_version_id: form.dataset_version_id || undefined,
      dataset_export_id: form.dataset_export_id,
      config,
    })

    await startTask(task.id)
    emit('created', task.id)
    visible.value = false
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : '创建训练任务失败'
    ElMessage.error(message)
    emit('created', '')
  }
}
</script>
