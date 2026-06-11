<template>
  <div class="dataset-list">
    <div class="page-header">
      <h3>数据集管理</h3>
      <el-button type="primary">新建数据集</el-button>
    </div>
    <el-table :data="datasets" border stripe>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="data_type" label="类型" width="100" />
      <el-table-column prop="num_classes" label="类别数" width="100" />
      <el-table-column prop="train_count" label="训练集" width="100" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column label="操作" width="200">
        <template #default>
          <el-button size="small" type="primary" link>标注</el-button>
          <el-button size="small" type="primary" link>编辑</el-button>
          <el-button size="small" type="danger" link>删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Dataset } from '@/types/dataset'

const datasets = ref<Dataset[]>([])
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
