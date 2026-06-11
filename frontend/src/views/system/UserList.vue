<template>
  <div class="user-list">
    <div class="page-header">
      <h3>用户管理</h3>
      <el-button type="primary">新建用户</el-button>
    </div>
    <el-table :data="[]" border stripe>
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="role" label="角色" width="120" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column prop="last_login" label="最后登录" width="180" />
      <el-table-column label="操作" width="150">
        <template #default>
          <el-button size="small" type="primary" link>编辑</el-button>
          <el-button size="small" type="danger" link>禁用</el-button>
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
