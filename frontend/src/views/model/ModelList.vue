<template>
  <div class="model-list">
    <div class="page-header">
      <h3>模型管理</h3>
      <div class="header-actions">
        <el-radio-group v-model="filterSource" @change="loadModels">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button label="pretrained">预训练</el-radio-button>
          <el-radio-button label="trained">训练产出</el-radio-button>
          <el-radio-button label="imported">导入</el-radio-button>
        </el-radio-group>
        <el-button type="primary" @click="importVisible = true">导入模型</el-button>
      </div>
    </div>

    <el-table :data="models" border stripe>
      <el-table-column prop="name" label="名称" min-width="180" />
      <el-table-column label="来源" width="100">
        <template #default="{ row }">
          <el-tag :type="sourceTag(row.model_source)">{{ sourceLabel(row.model_source) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="version" label="版本" width="120" />
      <el-table-column prop="framework" label="框架" width="120" />
      <el-table-column label="mAP50" width="100">
        <template #default="{ row }">
          {{ formatMetric(row.metrics?.map50) }}
        </template>
      </el-table-column>
      <el-table-column prop="model_size_mb" label="大小(MB)" width="100" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column label="操作" width="240">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="handleDownload(row.id)">
            下载
          </el-button>
          <el-button size="small" type="primary" link @click="handleViewDetail(row)">
            详情
          </el-button>
          <el-button size="small" type="danger" link @click="handleDelete(row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="detailVisible" title="模型详情" width="500px">
      <el-descriptions v-if="selectedModel" :column="1" border>
        <el-descriptions-item label="名称">{{ selectedModel.name }}</el-descriptions-item>
        <el-descriptions-item label="版本">{{ selectedModel.version }}</el-descriptions-item>
        <el-descriptions-item label="框架">{{ selectedModel.framework }}</el-descriptions-item>
        <el-descriptions-item label="来源">{{ sourceLabel(selectedModel.model_source) }}</el-descriptions-item>
        <el-descriptions-item label="权重路径">{{ selectedModel.weight_path }}</el-descriptions-item>
        <el-descriptions-item label="指标">
          <pre>{{ JSON.stringify(selectedModel.metrics, null, 2) }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
    <el-dialog v-model="importVisible" title="导入模型" width="500px" @closed="resetImportForm">
      <el-form :model="importForm" label-width="90px">
        <el-form-item label="名称" required>
          <el-input v-model="importForm.name" placeholder="模型名称" />
        </el-form-item>
        <el-form-item label="版本">
          <el-input v-model="importForm.version" placeholder="如 v8n、v8s（可选）" />
        </el-form-item>
        <el-form-item label="框架">
          <el-select v-model="importForm.framework" style="width: 100%">
            <el-option label="ultralytics" value="ultralytics" />
            <el-option label="onnx" value="onnx" />
            <el-option label="torchscript" value="torchscript" />
          </el-select>
        </el-form-item>
        <el-form-item label="权重文件" required>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".pt,.pth,.onnx,.torchscript"
            :on-change="handleFileChange"
            :on-remove="() => (importForm.file = null)"
          >
            <el-button type="primary" plain>选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">支持 .pt / .pth / .onnx / .torchscript</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="importVisible = false">取消</el-button>
        <el-button type="primary" :loading="importLoading" @click="handleImport">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getModels, deleteModel, modelDownloadUrl, importModel } from '@/api/model'
import type { MLModel } from '@/types/model'
import type { UploadFile } from 'element-plus'

const models = ref<MLModel[]>([])
const filterSource = ref('')
const detailVisible = ref(false)
const selectedModel = ref<MLModel | null>(null)

onMounted(loadModels)

async function loadModels() {
  const params = filterSource.value ? { source: filterSource.value } : undefined
  models.value = await getModels(params)
}

function sourceLabel(source: string): string {
  const map: Record<string, string> = {
    pretrained: '预训练',
    trained: '训练产出',
    imported: '导入',
  }
  return map[source] || source
}

function sourceTag(source: string): 'primary' | 'success' | 'info' {
  const map: Record<string, 'primary' | 'success' | 'info'> = {
    pretrained: 'info',
    trained: 'success',
    imported: 'primary',
  }
  return map[source] || 'info'
}

function formatMetric(value: number | undefined): string {
  if (value === undefined || value === null) return '--'
  return (value * 100).toFixed(1) + '%'
}

function handleDownload(id: string) {
  window.open(modelDownloadUrl(id), '_blank')
}

function handleViewDetail(model: MLModel) {
  selectedModel.value = model
  detailVisible.value = true
}

async function handleDelete(id: string) {
  try {
    await ElMessageBox.confirm('确定删除该模型？此操作不可恢复', '确认', {
      type: 'warning',
    })
    await deleteModel(id)
    ElMessage.success('已删除')
    loadModels()
  } catch {
    // user cancelled
  }
}

const importVisible = ref(false)
const importLoading = ref(false)
const importForm = reactive<{
  name: string
  version: string
  framework: string
  file: File | null
}>({
  name: '',
  version: '',
  framework: 'ultralytics',
  file: null,
})

function handleFileChange(uploadFile: UploadFile) {
  importForm.file = (uploadFile.raw as File) ?? null
}

function resetImportForm() {
  importForm.name = ''
  importForm.version = ''
  importForm.framework = 'ultralytics'
  importForm.file = null
}

async function handleImport() {
  if (!importForm.name.trim()) {
    ElMessage.warning('请输入模型名称')
    return
  }
  if (!importForm.file) {
    ElMessage.warning('请选择权重文件')
    return
  }
  importLoading.value = true
  try {
    await importModel({
      name: importForm.name.trim(),
      version: importForm.version.trim() || undefined,
      framework: importForm.framework,
      file: importForm.file,
    })
    ElMessage.success('导入成功')
    importVisible.value = false
    loadModels()
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : '导入失败'
    ElMessage.error(message)
  } finally {
    importLoading.value = false
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
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
pre {
  margin: 0;
  font-size: 12px;
  white-space: pre-wrap;
}
</style>
