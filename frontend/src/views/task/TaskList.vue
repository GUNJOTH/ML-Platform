<template>
  <div class="task-list">
    <div class="page-header">
      <h3>训练任务</h3>
      <el-button type="primary">新建任务</el-button>
    </div>
    <el-table :data="tasks" border stripe>
      <el-table-column prop="name" label="任务名称" />
      <el-table-column prop="task_type" label="类型" width="100" />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusTag(row.status)">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="progress" label="进度" width="120">
        <template #default="{ row }">
          <el-progress :percentage="row.progress" :stroke-width="6" />
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 'running'"
            size="small"
            type="danger"
            link
          >取消</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Task } from '@/types/task'

const tasks = ref<Task[]>([])

function statusTag(status: string) {
  const map: Record<string, string> = {
    pending: 'info',
    running: '',
    completed: 'success',
    failed: 'danger',
    cancelled: 'warning',
  }
  return map[status] || 'info'
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
