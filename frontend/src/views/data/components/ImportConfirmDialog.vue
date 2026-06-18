<template>
  <el-dialog :model-value="visible" title="确认导入" width="500px" @close="emit('update:visible', false)">
    <div v-if="detectResult">
      <p><strong>检测到类别 ({{ detectResult.classes.length }})：</strong></p>
      <el-tag v-for="c in detectResult.classes" :key="c" class="class-tag">{{ c }}</el-tag>
      <el-divider />
      <p><strong>数据分布：</strong></p>
      <ul>
        <li v-for="(info, split) in detectResult.splits" :key="split">
          {{ split }}: {{ info.count }} 张图片
        </li>
      </ul>
    </div>
    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" @click="emit('confirm')">确认导入</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
interface DetectResult {
  classes: string[]
  splits: Record<string, { count: number }>
}

defineProps<{
  visible: boolean
  detectResult: DetectResult | null
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  confirm: []
}>()
</script>

<style scoped>
.class-tag { margin: 2px 4px; }
</style>
