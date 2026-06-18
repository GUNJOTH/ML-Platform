<template>
  <div class="dataset-list">
    <div class="page-header">
      <h3>数据集管理</h3>
      <div>
        <el-button type="primary" @click="showCreate = true">新建数据集</el-button>
      </div>
    </div>

    <el-table :data="datasets" border stripe>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="data_type" label="类型" width="100" />
      <el-table-column prop="num_classes" label="类别数" width="80" />
      <el-table-column prop="train_count" label="训练集" width="80" />
      <el-table-column prop="val_count" label="验证集" width="80" />
      <el-table-column prop="test_count" label="测试集" width="80" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="260">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="handleUploadZip(row.id)">
            上传数据
          </el-button>
          <el-button size="small" type="success" link @click="goAnnotate(row.id)">
            标注
          </el-button>
          <el-button size="small" type="danger" link @click="handleDelete(row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreate" title="新建数据集" width="400px">
      <el-form label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="createForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showUpload" title="上传数据集 ZIP" width="400px">
      <el-upload
        drag
        :auto-upload="false"
        :on-change="onZipSelected"
        accept=".zip"
        :show-file-list="true"
        :limit="1"
      >
        <el-icon :size="48"><UploadFilled /></el-icon>
        <div>拖拽或点击上传 ZIP 文件</div>
      </el-upload>
      <template #footer>
        <el-button @click="showUpload = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="doUpload">上传</el-button>
      </template>
    </el-dialog>

    <ImportConfirmDialog
      v-model:visible="showConfirm"
      :detect-result="detectResult"
      @confirm="doConfirm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDatasets, createDataset, deleteDataset } from '@/api/dataset'
import { uploadDatasetZip, detectDatasetStructure, confirmDatasetImport } from '@/api/upload'
import ImportConfirmDialog from './components/ImportConfirmDialog.vue'

interface Dataset {
  id: string
  name: string
  data_type: string
  num_classes: number
  train_count: number
  val_count: number
  test_count: number
  status: string
}

const datasets = ref<Dataset[]>([])
const showCreate = ref(false)
const showUpload = ref(false)
const showConfirm = ref(false)
const uploading = ref(false)
const activeDatasetId = ref('')
const detectResult = ref<{ classes: string[]; splits: Record<string, { count: number }> } | null>(null)
const router = useRouter()

const createForm = reactive({ name: '', description: '' })
let zipFile: File | null = null

onMounted(loadDatasets)

async function loadDatasets() {
  datasets.value = (await getDatasets()) as unknown as Dataset[]
}

async function handleCreate() {
  if (!createForm.name) {
    ElMessage.warning('请输入数据集名称')
    return
  }
  try {
    const res = await createDataset(createForm) as unknown as { id: string }
    showCreate.value = false
    createForm.name = ''
    createForm.description = ''
    await loadDatasets()
    handleUploadZip(res.id)
  } catch (err: unknown) {
    const detail = isAxiosErrorDetail(err) ? err.response?.data?.detail : undefined
    ElMessage.error(detail || '创建失败')
  }
}

function isAxiosErrorDetail(err: unknown): err is { response?: { data?: { detail?: string } } } {
  return typeof err === 'object' && err !== null && 'response' in err
}

function handleUploadZip(datasetId: string) {
  activeDatasetId.value = datasetId
  showUpload.value = true
}

function onZipSelected(file: { raw: File }) {
  zipFile = file.raw
}

async function doUpload() {
  if (!zipFile || !activeDatasetId.value) return
  uploading.value = true
  try {
    await uploadDatasetZip(activeDatasetId.value, zipFile)
    const result = await detectDatasetStructure(activeDatasetId.value)
    detectResult.value = result as unknown as { classes: string[]; splits: Record<string, { count: number }> }
    showUpload.value = false
    showConfirm.value = true
  } finally {
    uploading.value = false
  }
}

async function doConfirm() {
  if (!detectResult.value) return
  await confirmDatasetImport(activeDatasetId.value, {
    classes: detectResult.value.classes,
    splits: detectResult.value.splits,
  })
  showConfirm.value = false
  loadDatasets()
}

function goAnnotate(datasetId: string) {
  router.push(`/annotation/workspace/${datasetId}`)
}

async function handleDelete(id: string) {
  try {
    await ElMessageBox.confirm('确定删除该数据集？', '确认', { type: 'warning' })
    await deleteDataset(id)
    ElMessage.success('已删除')
    loadDatasets()
  } catch {
    // cancelled
  }
}

const STATUS_CONFIG: Record<string, { type: 'info' | 'success' | 'warning'; label: string }> = {
  ready: { type: 'info', label: '待标注' },
  annotated: { type: 'success', label: '已标注' },
  importing: { type: 'warning', label: '导入中' },
}

function statusType(status: string) { return STATUS_CONFIG[status]?.type || 'info' }
function statusLabel(status: string) { return STATUS_CONFIG[status]?.label || status }
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
