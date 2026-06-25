import { ref, onUnmounted } from 'vue'
import { getTaskProgress } from '@/api/task'

export function useTaskProgress(taskId: string) {
  const progress = ref(0)
  const epoch = ref(0)
  const totalEpochs = ref(0)
  const status = ref<'connecting' | 'running' | 'completed' | 'failed'>('connecting')
  const result = ref<Record<string, unknown> | null>(null)

  let ws: WebSocket | null = null
  let pollTimer: ReturnType<typeof setInterval> | null = null

  function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const host = window.location.host
    ws = new WebSocket(`${protocol}://${host}/api/v1/ws/tasks/${taskId}`)

    ws.onmessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data)
      if (data.type === 'progress') {
        progress.value = data.progress || 0
        epoch.value = data.epoch || 0
        totalEpochs.value = data.total || 0
        status.value = 'running'
      } else if (data.type === 'complete') {
        status.value = data.status === 'failed' ? 'failed' : 'completed'
        result.value = data
        progress.value = 100
      }
    }

    ws.onerror = () => {
      fallbackToPolling()
    }

    ws.onclose = () => {
      if (status.value === 'connecting' || status.value === 'running') {
        fallbackToPolling()
      }
    }
  }

  function fallbackToPolling() {
    if (pollTimer) return
    pollTimer = setInterval(async () => {
      try {
        const data = await getTaskProgress(taskId)
        progress.value = data.progress || 0
      } catch {
        // silent retry
      }
    }, 3000)
  }

  function disconnect() {
    ws?.close()
    ws = null
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  connect()
  onUnmounted(disconnect)

  return { progress, epoch, totalEpochs, status, result, disconnect }
}
