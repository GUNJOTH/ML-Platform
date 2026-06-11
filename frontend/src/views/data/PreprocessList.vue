<template>
  <div class="preprocess-list">
    <div class="page-header">
      <h3>预处理任务</h3>
      <el-button type="primary">新建任务</el-button>
    </div>
    <el-table :data="[]" border stripe>
      <el-table-column prop="name" label="任务名称" />
      <el-table-column prop="type" label="处理类型" width="120" />
      <el-table-column prop="dataset" label="目标数据集" />
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
