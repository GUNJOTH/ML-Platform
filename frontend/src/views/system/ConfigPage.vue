<template>
  <div class="config-page">
    <div class="page-header">
      <h3>系统配置</h3>
    </div>
    <el-card>
      <el-form label-width="120px">
        <el-form-item label="平台名称">
          <el-input model-value="AI Platform" disabled />
        </el-form-item>
        <el-form-item label="存储路径">
          <el-input model-value="./storage" disabled />
        </el-form-item>
        <el-form-item label="最大上传">
          <el-input model-value="500 MB" disabled />
        </el-form-item>
        <el-form-item label="训练框架">
          <el-input model-value="ultralytics (YOLOv8)" disabled />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.page-header {
  margin-bottom: 16px;
}
</style>
