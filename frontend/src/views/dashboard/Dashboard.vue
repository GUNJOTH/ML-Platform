<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-card-content">
            <div class="stat-info">
              <span class="stat-label">{{ card.label }}</span>
              <span class="stat-value">{{ card.value }}</span>
            </div>
            <el-icon class="stat-icon" :size="36"><component :is="card.icon" /></el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>工作流程</template>
          <div class="workflow">
            <div class="workflow-step" v-for="step in workflow" :key="step.title">
              <div class="step-circle">{{ step.num }}</div>
              <div class="step-text">
                <strong>{{ step.title }}</strong>
                <p>{{ step.desc }}</p>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>最近任务</template>
          <div class="recent-tasks">
            <p class="empty-hint">暂无任务记录</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { reactive, markRaw } from 'vue'
import { Files, Edit, Cpu, VideoPlay } from '@element-plus/icons-vue'

const statCards = reactive([
  { label: '数据集', value: '--', icon: markRaw(Files) },
  { label: '已标注图片', value: '--', icon: markRaw(Edit) },
  { label: '模型', value: '--', icon: markRaw(Cpu) },
  { label: '训练任务', value: '--', icon: markRaw(VideoPlay) },
])

const workflow = [
  { num: '1', title: '上传数据', desc: '创建数据集并上传图片' },
  { num: '2', title: '数据标注', desc: '使用标注工具标记目标' },
  { num: '3', title: '模型训练', desc: '选择框架启动训练任务' },
  { num: '4', title: '评估推理', desc: '验证模型效果并部署' },
]
</script>

<style scoped>
.stat-row {
  margin-bottom: 20px;
}

.stat-card-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.stat-icon {
  color: #409eff;
}

.workflow {
  display: flex;
  justify-content: space-between;
  padding: 20px 0;
}

.workflow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  flex: 1;
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  margin-bottom: 8px;
}

.step-text strong {
  display: block;
  margin-bottom: 4px;
}

.step-text p {
  font-size: 12px;
  color: #909399;
  margin: 0;
}

.recent-tasks {
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-hint {
  color: #999;
  font-size: 14px;
}
</style>
