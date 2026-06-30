<template>
  <div>
    <div class="detail-section-title">训练日志</div>
    <div class="log-actions">
      <el-button size="small" @click="loadLog('stdout')">查看 stdout</el-button>
      <el-button size="small" @click="loadLog('stderr')">查看 stderr</el-button>
      <el-button size="small" :disabled="!activeLogStream" @click="refreshActiveLog">
        刷新日志
      </el-button>
    </div>
    <el-input
      v-if="activeLogStream"
      :model-value="activeLogContent"
      type="textarea"
      :rows="rows"
      readonly
      class="log-viewer"
    />
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { onUnmounted, ref, watch } from 'vue'
import { getTaskLog } from '@/api/task'

const props = defineProps<{
  taskId: string
  isRunning: boolean
  rows: number
}>()

const activeLogStream = ref<'stdout' | 'stderr' | ''>('')
const activeLogContent = ref('')

let logTimer: ReturnType<typeof setInterval> | null = null

watch(
  () => [props.taskId, props.isRunning] as const,
  ([taskId, isRunning]) => {
    stopLogRefresh()
    activeLogStream.value = ''
    activeLogContent.value = ''

    if (!taskId) {
      return
    }

    if (isRunning) {
      loadLog('stdout')
      startLogRefresh()
    }
  },
  { immediate: true },
)

async function loadLog(stream: 'stdout' | 'stderr') {
  try {
    const log = await getTaskLog(props.taskId, stream)
    activeLogStream.value = stream
    activeLogContent.value = log.content || ''
  } catch {
    ElMessage.error('日志加载失败')
  }
}

function refreshActiveLog() {
  if (!activeLogStream.value) {
    return
  }
  loadLog(activeLogStream.value)
}

function startLogRefresh() {
  if (logTimer) {
    return
  }

  logTimer = setInterval(() => {
    if (!props.isRunning || !activeLogStream.value) {
      return
    }
    loadLog(activeLogStream.value)
  }, 3000)
}

function stopLogRefresh() {
  if (!logTimer) {
    return
  }
  clearInterval(logTimer)
  logTimer = null
}

onUnmounted(() => {
  stopLogRefresh()
})
</script>

<style scoped>
.detail-section-title {
  margin: 16px 0 10px;
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.log-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.log-viewer {
  margin-top: 12px;
}
</style>
