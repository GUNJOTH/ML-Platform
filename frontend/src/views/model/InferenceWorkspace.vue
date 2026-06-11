<template>
  <div class="inference-page">
    <div class="page-header">
      <h3>模型推理</h3>
    </div>
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>推理配置</template>
          <el-form label-width="80px">
            <el-form-item label="模型">
              <el-select v-model="form.model_id" placeholder="选择模型">
              </el-select>
            </el-form-item>
            <el-form-item label="置信度">
              <el-slider v-model="form.confidence" :min="0.1" :max="1" :step="0.05" />
            </el-form-item>
            <el-form-item label="IoU">
              <el-slider v-model="form.iou_threshold" :min="0.1" :max="1" :step="0.05" />
            </el-form-item>
            <el-form-item>
              <el-upload action="" :auto-upload="false">
                <el-button type="primary">上传图片</el-button>
              </el-upload>
            </el-form-item>
            <el-form-item>
              <el-button type="success" :disabled="!form.model_id">开始推理</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card>
          <template #header>推理结果</template>
          <div class="result-placeholder">
            <p>上传图片并选择模型后，点击推理查看结果</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const form = reactive({
  model_id: '',
  confidence: 0.25,
  iou_threshold: 0.45,
})
</script>

<style scoped>
.page-header {
  margin-bottom: 16px;
}

.result-placeholder {
  text-align: center;
  padding: 60px 0;
  color: #999;
}
</style>
