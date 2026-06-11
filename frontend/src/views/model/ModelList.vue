<template>
  <div class="model-list">
    <div class="page-header">
      <h3>模型管理</h3>
      <el-button type="primary">注册模型</el-button>
    </div>
    <el-table :data="models" border stripe>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="version" label="版本" width="120" />
      <el-table-column prop="framework" label="框架" width="120" />
      <el-table-column prop="model_size_mb" label="大小(MB)" width="100" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column label="操作" width="150">
        <template #default>
          <el-button size="small" type="primary" link>详情</el-button>
          <el-button size="small" type="danger" link>删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { MLModel } from '@/types/model'

const models = ref<MLModel[]>([])
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
