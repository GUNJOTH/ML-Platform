<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>数据集</template>
          <div class="stat-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>模型</template>
          <div class="stat-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>训练任务</template>
          <div class="stat-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>标注进度</template>
          <div class="stat-value">--</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.stat-value {
  font-size: 28px;
  font-weight: 700;
  text-align: center;
  padding: 10px 0;
}
</style>
