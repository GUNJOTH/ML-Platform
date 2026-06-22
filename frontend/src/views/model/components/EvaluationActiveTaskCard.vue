<template>
  <el-card v-if="task" class="status-card">
    <div class="status-header">
      <div>
        <div class="status-title">{{ task.name }}</div>
        <div class="status-meta">
          <span>状态：{{ task.status }}</span>
          <span v-if="task.created_at">创建于：{{ formatDate(task.created_at) }}</span>
        </div>
      </div>
      <el-tag :type="statusTag(task.status)">
        {{ task.status === 'running' ? '评估进行中' : task.status }}
      </el-tag>
    </div>
    <div v-if="task.status === 'running'" class="status-hint">
      当前评估在后台继续运行。切换页面后返回，这里会自动恢复结果展示。
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { Task } from '@/types/task'

defineProps<{
  task: Task | null
}>()

function formatDate(value: string | null): string {
  if (!value) {
    return '--'
  }
  return new Date(value).toLocaleString()
}

function statusTag(status: string): string {
  const map: Record<string, string> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info',
  }
  return map[status] || 'info'
}
</script>

<style scoped>
.status-card {
  margin-bottom: 20px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.status-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.status-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 8px;
  color: #606266;
  font-size: 13px;
}

.status-hint {
  margin-top: 12px;
  color: #8c6d1f;
  font-size: 13px;
}
</style>
