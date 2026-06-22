<template>
  <div class="dataset-version-rules">
    <div class="page-header">
      <div>
        <h3>版本规则</h3>
        <p class="page-subtitle">
          先沉淀版本命名、冻结时机、导出约束和训练准入规则，后续再接真实规则引擎。
        </p>
      </div>
      <el-button @click="goBack">返回版本列表</el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="section-card">
          <template #header>命名与冻结规则</template>
          <div class="rule-list">
            <div v-for="rule in namingRules" :key="rule.title" class="rule-item">
              <div class="rule-title">{{ rule.title }}</div>
              <div class="rule-desc">{{ rule.description }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="section-card">
          <template #header>训练准入规则</template>
          <div class="rule-list">
            <div v-for="rule in trainingRules" :key="rule.title" class="rule-item">
              <div class="rule-title">{{ rule.title }}</div>
              <div class="rule-desc">{{ rule.description }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="section-card">
      <template #header>导出与回滚规则</template>
      <el-table :data="exportRules" border stripe>
        <el-table-column prop="scene" label="场景" min-width="180" />
        <el-table-column prop="rule" label="规则说明" min-width="320" />
        <el-table-column prop="phase" label="当前阶段" width="140" />
      </el-table>
    </el-card>

    <el-card class="section-card">
      <template #header>后续规则引擎预留</template>
      <div class="placeholder-grid">
        <div class="placeholder-item">规则可配置化</div>
        <div class="placeholder-item">规则等级：提示 / 警告 / 阻断</div>
        <div class="placeholder-item">规则命中日志</div>
        <div class="placeholder-item">规则版本化</div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const namingRules = [
  {
    title: '版本名称应体现来源与用途',
    description: '建议采用 dataset_alias + 版本号 + 冻结动作，例如 smoke_v4_freeze。',
  },
  {
    title: '冻结应发生在训练前',
    description: '训练任务后续应只绑定版本 ID，不直接绑定可变数据集。',
  },
  {
    title: '每次关键导出都应生成版本',
    description: '标注闭环后、训练前、对外共享前都应形成可回溯版本。',
  },
]

const trainingRules = [
  {
    title: '草稿版本默认不可训练',
    description: '未完成训练前校验的版本，只能查看和补充信息，不能直接用于训练。',
  },
  {
    title: '版本校验不通过则阻断训练',
    description: '后续应对空标注、划分缺失、类别异常等问题给出阻断结果。',
  },
  {
    title: '训练配置需记录引用版本',
    description: '用于后续回放、复训、评估和模型导出时的完整追溯。',
  },
]

const exportRules = [
  {
    scene: '正式训练导出',
    rule: '必须绑定 ready 状态版本，且包含原图、标签与 manifest。',
    phase: '界面已预留',
  },
  {
    scene: '外部共享导出',
    rule: '需支持脱敏、筛选 split、记录导出路径和发起人。',
    phase: '界面已预留',
  },
  {
    scene: '版本回滚',
    rule: '允许选择历史版本重新导出，但应保留新的导出记录。',
    phase: '后续实现',
  },
]

function goBack() {
  router.push('/data/versions')
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.page-subtitle {
  margin: 8px 0 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.7;
}

.section-card {
  margin-bottom: 20px;
  border-radius: 16px;
}

.rule-list {
  display: grid;
  gap: 12px;
}

.rule-item,
.placeholder-item {
  padding: 14px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.rule-title {
  font-weight: 600;
  color: #0f172a;
}

.rule-desc {
  margin-top: 8px;
  color: #475569;
  line-height: 1.7;
}

.placeholder-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}
</style>
