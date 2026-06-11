<template>
  <div class="log-list">
    <div class="page-header">
      <h3>操作日志</h3>
    </div>
    <el-table :data="[]" border stripe>
      <el-table-column prop="user" label="操作人" width="120" />
      <el-table-column prop="action" label="操作类型" width="120" />
      <el-table-column prop="target" label="操作对象" />
      <el-table-column prop="detail" label="详情" />
      <el-table-column prop="ip" label="IP" width="130" />
      <el-table-column prop="created_at" label="时间" width="180" />
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
