<template>
  <div class="role-list">
    <div class="page-header">
      <h3>角色权限</h3>
      <el-button type="primary">新建角色</el-button>
    </div>
    <el-table :data="[]" border stripe>
      <el-table-column prop="name" label="角色名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="user_count" label="用户数" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="150">
        <template #default>
          <el-button size="small" type="primary" link>权限</el-button>
          <el-button size="small" type="primary" link>编辑</el-button>
        </template>
      </el-table-column>
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
