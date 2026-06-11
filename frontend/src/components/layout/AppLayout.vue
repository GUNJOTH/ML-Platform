<template>
  <el-container class="app-layout">
    <el-aside width="220px" class="sidebar-container">
      <Sidebar />
    </el-aside>
    <el-container>
      <el-header class="header-container">
        <Header />
      </el-header>
      <TagsView />
      <el-main class="main-container">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'
import TagsView from './TagsView.vue'
import { useTagsStore } from '@/stores/tags'

const route = useRoute()
const tagsStore = useTagsStore()

watch(
  () => route.path,
  () => tagsStore.addTag(route),
  { immediate: true }
)
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
  height: 50px;
}

.main-container {
  background-color: #f5f7fa;
  padding: 20px;
}
</style>
