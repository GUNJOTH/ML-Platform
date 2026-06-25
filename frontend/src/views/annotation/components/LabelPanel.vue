<template>
  <div class="label-panel">
    <div class="panel-header">
      <h4>类别标签</h4>
      <el-button size="small" type="primary" plain @click="dialogVisible = true">
        新增类别
      </el-button>
    </div>

    <div
      v-for="label in labels"
      :key="label.id"
      class="label-item"
      :class="{ active: label.id === selectedLabelId }"
      @click="emit('select', label)"
    >
      <div class="label-main">
        <span class="color-dot" :style="{ background: label.color }" />
        <span class="label-name">{{ label.name }}</span>
      </div>
      <el-button size="small" link type="danger" @click.stop="emit('delete', label)">
        删除
      </el-button>
    </div>

    <div v-if="labels.length === 0" class="empty-block">
      <p class="empty">当前数据集还没有类别</p>
      <p class="empty-tip">请先新增类别，再开始框选标注。</p>
    </div>

    <el-dialog v-model="dialogVisible" title="新增类别" width="420px">
      <el-form label-width="80px">
        <el-form-item label="类别名">
          <el-input v-model="form.name" maxlength="40" show-word-limit />
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="form.color" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submit">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { WorkspaceLabelItem } from '@/types/annotation-workspace'

const props = defineProps<{
  labels: WorkspaceLabelItem[]
  selectedLabelId: string
  canCreate: boolean
}>()

const emit = defineEmits<{
  select: [label: WorkspaceLabelItem]
  create: [payload: { name: string; color: string }]
  delete: [label: WorkspaceLabelItem]
}>()

const dialogVisible = ref(false)
const submitting = ref(false)
const form = reactive({
  name: '',
  color: '#FF0000',
})

async function submit() {
  if (!props.canCreate) {
    ElMessage.warning('请先选择数据集')
    return
  }
  if (!form.name.trim()) {
    ElMessage.warning('请输入类别名')
    return
  }

  submitting.value = true
  try {
    emit('create', {
      name: form.name.trim(),
      color: form.color,
    })
    form.name = ''
    form.color = '#FF0000'
    dialogVisible.value = false
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

h4 {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.label-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.label-item:hover {
  background: #f0f2f5;
}

.label-item.active {
  background: #ecf5ff;
  border: 1px solid #409eff;
}

.label-main {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  flex-shrink: 0;
}

.label-name {
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-block {
  padding: 16px 8px;
  text-align: center;
}

.empty {
  color: #666;
  font-size: 13px;
  margin: 0 0 6px;
}

.empty-tip {
  color: #999;
  font-size: 12px;
  margin: 0;
}
</style>
