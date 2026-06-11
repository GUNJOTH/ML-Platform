<template>
  <el-upload
    :action="uploadUrl"
    :before-upload="handleBeforeUpload"
    :on-success="handleSuccess"
    :on-error="handleError"
    :accept="accept"
    :drag="drag"
  >
    <slot>
      <div v-if="drag" class="upload-dragger">
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <p>拖拽文件到此处或点击上传</p>
      </div>
      <el-button v-else type="primary">选择文件</el-button>
    </slot>
  </el-upload>
</template>

<script setup lang="ts">
import { UploadFilled } from '@element-plus/icons-vue'
import type { UploadRawFile } from 'element-plus'

interface Props {
  uploadUrl: string
  accept?: string
  maxSizeMb?: number
  drag?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  accept: '*',
  maxSizeMb: 500,
  drag: false,
})

const emit = defineEmits<{
  success: [response: unknown]
  error: [error: unknown]
}>()

function handleBeforeUpload(file: UploadRawFile) {
  const sizeMb = file.size / 1024 / 1024
  if (sizeMb > props.maxSizeMb) {
    return false
  }
  return true
}

function handleSuccess(response: unknown) {
  emit('success', response)
}

function handleError(error: unknown) {
  emit('error', error)
}
</script>

<style scoped>
.upload-dragger {
  padding: 40px 20px;
  text-align: center;
  color: #999;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 12px;
}
</style>
