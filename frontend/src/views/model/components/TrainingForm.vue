<template>
  <el-dialog v-model="visible" title="创建训练任务" width="600px">
    <el-form :model="form" label-width="120px">
      <el-form-item label="任务名称" required>
        <el-input v-model="form.name" placeholder="输入任务名称" />
      </el-form-item>
      <el-form-item label="数据集" required>
        <el-select v-model="form.dataset_id" placeholder="选择数据集" style="width: 100%">
          <el-option
            v-for="ds in datasets"
            :key="ds.id"
            :label="ds.name"
            :value="ds.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="预训练模型" required>
        <el-select v-model="form.model_id" placeholder="选择预训练模型" style="width: 100%">
          <el-option
            v-for="m in pretrainedModels"
            :key="m.id"
            :label="`${m.name}${m.version ? ' (' + m.version + ')' : ''}`"
            :value="m.id"
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
            <el-input-number v-model="form.img_size" :min="320" :max="1280" :step="32" />
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
            <el-input-number v-model="form.lr0" :min="0.0001" :max="0.1" :step="0.001" :precision="4" />
          </el-form-item>
          <el-form-item label="Warmup Epochs">
            <el-input-number v-model="form.warmup_epochs" :min="0" :max="10" />
          </el-form-item>
          <el-form-item label="余弦学习率">
            <el-switch v-model="form.cos_lr" />
          </el-form-item>
          <el-form-item label="Close Mosaic">
            <el-input-number v-model="form.close_mosaic" :min="0" :max="50" />
          </el-form-item>
          <el-form-item label="预训练权重">
            <el-switch v-model="form.pretrained" />
          </el-form-item>
        </el-collapse-item>
      </el-collapse>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">创建并开始训练</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { createTask, startTask, listDatasets } from '@/api/task'
import { getModels } from '@/api/model'

interface PretrainedModel {
  id: string
  name: string
  version: string | null
}

const visible = defineModel<boolean>({ required: true })
const emit = defineEmits<{ created: [taskId: string] }>()

const datasets = ref<Array<{ id: string; name: string }>>([])
const pretrainedModels = ref<PretrainedModel[]>([])

const form = reactive({
  name: '',
  dataset_id: '',
  model_id: '',
  epochs: 50,
  batch_size: 16,
  img_size: 640,
  patience: 10,
  optimizer: 'AdamW',
  lr0: 0.01,
  warmup_epochs: 3,
  cos_lr: false,
  close_mosaic: 10,
  pretrained: true,
})

onMounted(async () => {
  try {
    datasets.value = await listDatasets() || []
  } catch {
    datasets.value = []
  }
  try {
    const res = await getModels({ source: 'pretrained' })
    pretrainedModels.value = res || []
  } catch {
    pretrainedModels.value = []
  }
})

async function handleSubmit() {
  if (!form.dataset_id) {
    ElMessage.warning('请选择数据集')
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
