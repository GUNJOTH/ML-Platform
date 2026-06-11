<template>
  <el-container class="app-layout">
    <el-aside width="220px" class="sidebar-container">
      <Sidebar />
    </el-aside>
    <el-container>
      <el-header class="header-container">
        <Header />
      </el-header>
      <el-main class="main-container">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'
</script>

<style scoped>
.app-layout {
  height: 100vh;
}

.sidebar-container {
  background-color: #1d1e2c;
  overflow-y: auto;
}

.header-container {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.main-container {
  background-color: #f5f7fa;
  padding: 20px;
}
</style>
