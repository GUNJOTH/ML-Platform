<template>
  <div class="review-list">
    <div class="page-header">
      <h3>质检审核</h3>
    </div>
    <el-table :data="[]" border stripe>
      <el-table-column prop="batch_name" label="批次" />
      <el-table-column prop="image_name" label="图片" />
      <el-table-column prop="annotator" label="标注人" width="120" />
      <el-table-column prop="quality_score" label="质量评分" width="100" />
      <el-table-column prop="status" label="审核状态" width="100" />
      <el-table-column label="操作" width="150">
        <template #default>
          <el-button size="small" type="success" link>通过</el-button>
          <el-button size="small" type="danger" link>驳回</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
