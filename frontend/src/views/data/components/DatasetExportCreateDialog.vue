<template>
  <el-dialog
    :model-value="visible"
    title="发起导出"
    width="680px"
    @update:model-value="emit('update:visible', $event)"
  >
    <el-form label-width="110px">
      <el-form-item label="目标数据集">
        <el-input :model-value="datasetName" disabled />
      </el-form-item>
      <el-form-item label="来源版本">
        <el-input :model-value="version?.versionName || '--'" disabled />
      </el-form-item>
      <el-form-item label="导出名称">
        <el-input v-model="form.exportName" placeholder="例如 smoke_v3_yolo_trainset" />
      </el-form-item>
      <el-form-item label="导出格式">
        <el-radio-group v-model="form.exportFormat">
          <el-radio-button label="yolo">YOLO</el-radio-button>
          <el-radio-button label="coco">COCO</el-radio-button>
          <el-radio-button label="voc">VOC</el-radio-button>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="导出范围">
        <el-checkbox-group v-model="form.splits">
          <el-checkbox label="train">train</el-checkbox>
          <el-checkbox label="val">val</el-checkbox>
          <el-checkbox label="test">test</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item label="附加内容">
        <el-checkbox-group v-model="form.extras">
          <el-checkbox label="include_images">包含原图</el-checkbox>
          <el-checkbox label="include_labels">包含标注</el-checkbox>
          <el-checkbox label="include_manifest">包含清单文件</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item label="输出位置">
        <el-input v-model="form.outputPath" placeholder="storage/exports/..." />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.notes" type="textarea" :rows="3" />
      </el-form-item>
    </el-form>

    <el-card class="preview-card">
      <template #header>导出预览</template>
      <div class="preview-line">版本：{{ version?.versionName || '--' }}</div>
      <div class="preview-line">格式：{{ form.exportFormat.toUpperCase() }}</div>
      <div class="preview-line">范围：{{ splitPreview }}</div>
      <div class="preview-line">附加内容：{{ extraPreview }}</div>
      <div class="preview-line">输出位置：{{ form.outputPath || '--' }}</div>
    </el-card>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button @click="emit('save-draft', snapshot)">保存草稿</el-button>
      <el-button type="primary" @click="emit('submit', snapshot)">确认导出</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import type { ExportDraft } from '@/types/dataset-version'
import type { DatasetVersionSummary } from '@/types/dataset-version'

const props = defineProps<{
  visible: boolean
  version: DatasetVersionSummary | null
  datasetName: string
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  submit: [draft: ExportDraft]
  'save-draft': [draft: ExportDraft]
}>()

const form = reactive<ExportDraft>({
  exportName: '',
  exportFormat: 'yolo',
  splits: ['train', 'val', 'test'],
  extras: ['include_images', 'include_labels', 'include_manifest'],
  outputPath: '',
  notes: '',
})

watch(
  () => props.version,
  (version) => {
    if (!version) {
      return
    }
    form.exportName = `${version.versionName}_${form.exportFormat}`
    form.outputPath = `storage/exports/${version.versionName}_${form.exportFormat}.zip`
    form.notes = `基于 ${version.versionName} 发起的训练前导出。`
  },
  { immediate: true },
)

watch(
  () => form.exportFormat,
  (format) => {
    if (!props.version) {
      return
    }
    form.exportName = `${props.version.versionName}_${format}`
    form.outputPath = `storage/exports/${props.version.versionName}_${format}.zip`
  },
)

const splitPreview = computed(() => (form.splits.length ? form.splits.join(' / ') : '未选择'))
const extraPreview = computed(() => {
  if (!form.extras.length) {
    return '无'
  }
  const labels: Record<string, string> = {
    include_images: '原图',
    include_labels: '标注',
    include_manifest: '清单文件',
  }
  return form.extras.map((item) => labels[item] || item).join(' / ')
})

const snapshot = computed<ExportDraft>(() => ({
  exportName: form.exportName,
  exportFormat: form.exportFormat,
  splits: [...form.splits],
  extras: [...form.extras],
  outputPath: form.outputPath,
  notes: form.notes,
}))
</script>

<style scoped>
.preview-card {
  margin-top: 8px;
  border-radius: 14px;
  background: #f8fafc;
}

.preview-line {
  line-height: 1.9;
  color: #475569;
}
</style>
