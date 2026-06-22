<template>
  <div class="preprocess-list">
    <div class="page-header">
      <h3>预处理任务</h3>
      <el-button type="primary" @click="showForm = true">新建任务</el-button>
    </div>

    <el-table :data="tasks" border stripe>
      <el-table-column prop="name" label="任务名称" />
      <el-table-column label="数据集" width="150">
        <template #default="{ row }">
          {{ datasetName(row.dataset_id) }}
        </template>
      </el-table-column>
      <el-table-column label="类型" width="120">
        <template #default="{ row }">
          {{ row.config?.preprocess_type || '--' }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTag(row.status)">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
    </el-table>

    <el-dialog v-model="showForm" title="新建预处理任务" width="500px">
      <el-form label-width="100px">
        <el-form-item label="任务名称">
          <el-input v-model="form.name" placeholder="输入任务名称" />
        </el-form-item>
        <el-form-item label="数据集">
          <el-select v-model="form.dataset_id" placeholder="选择数据集" style="width: 100%">
            <el-option v-for="ds in datasets" :key="ds.id" :label="ds.name" :value="ds.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="处理类型">
          <el-select v-model="form.preprocess_type" style="width: 100%">
            <el-option label="图片缩放 (Resize)" value="resize" />
            <el-option label="数据增强 (Augmentation)" value="augmentation" />
            <el-option label="格式转换" value="format_convert" />
            <el-option label="数据集拆分" value="split" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showForm = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDatasets } from '@/api/dataset'
import { getTasks, createTask } from '@/api/task'
import type { Dataset } from '@/types/dataset'
import type { Task } from '@/types/task'

const datasets = ref<Dataset[]>([])
const tasks = ref<Task[]>([])
const showForm = ref(false)

const form = reactive({
  name: '',
  dataset_id: '',
  preprocess_type: 'resize',
})

onMounted(loadData)

async function loadData() {
  try {
    const [ds, ts] = await Promise.all([getDatasets(), getTasks({ task_type: 'preprocess' })])
    datasets.value = ds || []
    tasks.value = ts || []
  } catch {
    datasets.value = []
    tasks.value = []
  }
}

function datasetName(id: string | null): string {
  if (!id) return '--'
  return datasets.value.find((d) => d.id === id)?.name || '--'
}

function statusTag(status: string): string {
  const map: Record<string, string> = {
    pending: 'info',
    running: '',
    completed: 'success',
    failed: 'danger',
  }
  return map[status] || 'info'
}

async function handleCreate() {
  if (!form.name || !form.dataset_id) {
    ElMessage.warning('请填写完整')
    return
  }
  try {
    await createTask({
      name: form.name,
      task_type: 'preprocess',
      dataset_id: form.dataset_id,
      config: { preprocess_type: form.preprocess_type },
    })
    showForm.value = false
    form.name = ''
    form.dataset_id = ''
    ElMessage.success('任务已创建')
    loadData()
  } catch {
    ElMessage.error('创建失败')
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
