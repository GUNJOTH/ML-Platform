<template>
  <div class="sidebar">
    <div class="logo">
      <h2>AI Platform</h2>
    </div>
    <el-menu
      :default-active="activeMenu"
      router
      background-color="#1d1e2c"
      text-color="#bfcbd9"
      active-text-color="#409eff"
    >
      <el-menu-item
        v-for="item in menuRoutes"
        :key="item.path"
        :index="'/' + item.path"
      >
        <el-icon><component :is="iconMap[item.meta?.icon as string]" /></el-icon>
        <span>{{ item.meta?.title }}</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed, markRaw } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Odometer,
  Files,
  Edit,
  Cpu,
  VideoPlay,
  MagicStick,
  DataAnalysis,
} from '@element-plus/icons-vue'

const iconMap: Record<string, unknown> = {
  Odometer: markRaw(Odometer),
  Files: markRaw(Files),
  Edit: markRaw(Edit),
  Cpu: markRaw(Cpu),
  VideoPlay: markRaw(VideoPlay),
  MagicStick: markRaw(MagicStick),
  DataAnalysis: markRaw(DataAnalysis),
}

const route = useRoute()
const router = useRouter()

const menuRoutes = computed(() => {
  const root = router.options.routes[0]
  return root?.children || []
})

const activeMenu = computed(() => '/' + (route.path.split('/')[1] || 'dashboard'))
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
