<template>
  <div class="batch-list">
    <div class="page-header">
      <h3>标注批次</h3>
      <el-button type="primary">新建批次</el-button>
    </div>
    <el-table :data="[]" border stripe>
      <el-table-column prop="name" label="批次名称" />
      <el-table-column prop="dataset" label="数据集" />
      <el-table-column prop="total" label="总数" width="80" />
      <el-table-column prop="completed" label="已完成" width="80" />
      <el-table-column prop="assignee" label="标注人" width="120" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
