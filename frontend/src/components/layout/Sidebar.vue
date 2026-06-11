<template>
  <div class="sidebar">
    <div class="logo">
      <h2>AI Platform</h2>
    </div>
    <el-menu
      :default-active="activeMenu"
      :default-openeds="openedMenus"
      router
      background-color="#1d1e2c"
      text-color="#bfcbd9"
      active-text-color="#409eff"
    >
      <SidebarItem
        v-for="item in menuConfig"
        :key="item.path"
        :item="item"
      />
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { menuConfig } from '@/config/menu'
import SidebarItem from './SidebarItem.vue'

const route = useRoute()

const activeMenu = computed(() => route.path)

const openedMenus = computed(() =>
  menuConfig.filter((m) => m.children?.length).map((m) => m.path)
)
</script>

<style scoped>
.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo h2 {
  color: #fff;
  font-size: 18px;
  margin: 0;
}
</style>
