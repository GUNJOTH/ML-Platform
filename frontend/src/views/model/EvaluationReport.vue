<template>
  <div class="evaluation-page">
    <div class="page-header">
      <h3>模型评估</h3>
      <el-button type="primary">新建评估</el-button>
    </div>
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>mAP50</template>
          <div class="metric-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>mAP50-95</template>
          <div class="metric-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>精确率</template>
          <div class="metric-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>召回率</template>
          <div class="metric-value">--</div>
        </el-card>
      </el-col>
    </el-row>
    <el-card>
      <template #header>评估历史</template>
      <el-table :data="evaluations" border stripe>
        <el-table-column prop="model_name" label="模型" />
        <el-table-column prop="dataset_name" label="数据集" />
        <el-table-column prop="map50" label="mAP50" width="100" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const evaluations = ref<unknown[]>([])
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.stats-row {
  margin-bottom: 20px;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  text-align: center;
  padding: 10px 0;
}
</style>
