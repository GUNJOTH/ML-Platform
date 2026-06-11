<template>
  <template v-if="item.children?.length">
    <el-sub-menu :index="item.path">
      <template #title>
        <el-icon><component :is="iconMap[item.icon ?? '']" /></el-icon>
        <span>{{ item.title }}</span>
      </template>
      <SidebarItem
        v-for="child in item.children"
        :key="child.path"
        :item="child"
      />
    </el-sub-menu>
  </template>
  <template v-else>
    <el-menu-item :index="item.path">
      <el-icon v-if="item.icon"><component :is="iconMap[item.icon]" /></el-icon>
      <span>{{ item.title }}</span>
    </el-menu-item>
  </template>
</template>

<script setup lang="ts">
import { markRaw } from 'vue'
import {
  Odometer,
  Files,
  Edit,
  Cpu,
  Setting,
  VideoPlay,
  MagicStick,
  DataAnalysis,
} from '@element-plus/icons-vue'
import type { MenuItem } from '@/config/menu'

defineProps<{ item: MenuItem }>()

const iconMap: Record<string, unknown> = {
  Odometer: markRaw(Odometer),
  Files: markRaw(Files),
  Edit: markRaw(Edit),
  Cpu: markRaw(Cpu),
  Setting: markRaw(Setting),
  VideoPlay: markRaw(VideoPlay),
  MagicStick: markRaw(MagicStick),
  DataAnalysis: markRaw(DataAnalysis),
}
</script>
