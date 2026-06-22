<template>
  <el-card class="artifact-card">
    <template #header>{{ title }}</template>
    <div class="artifact-grid">
      <div
        v-for="artifact in imageArtifacts"
        :key="artifact.key"
        class="artifact-item"
        @click="openPreview(artifact.url)"
      >
        <img :src="artifact.url" :alt="artifact.filename" class="artifact-image" />
        <div class="artifact-name">{{ artifact.filename }}</div>
      </div>
    </div>

    <template v-if="fileArtifacts.length">
      <el-divider content-position="left">其他文件</el-divider>
      <div class="artifact-links">
        <el-link
          v-for="artifact in fileArtifacts"
          :key="artifact.key"
          :href="artifact.url"
          target="_blank"
          type="primary"
        >
          {{ artifact.filename }}
        </el-link>
      </div>
    </template>

    <el-dialog v-model="previewVisible" title="产物预览" width="80%">
      <img v-if="previewUrl" :src="previewUrl" alt="artifact preview" class="preview-image" />
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { TaskArtifactItem } from '@/types/task'

const props = defineProps<{
  title: string
  artifacts: TaskArtifactItem[]
}>()

const previewVisible = ref(false)
const previewUrl = ref('')

const imageArtifacts = computed(() =>
  props.artifacts.filter((artifact) => /\.(png|jpg|jpeg|webp)$/i.test(artifact.filename)),
)

const fileArtifacts = computed(() =>
  props.artifacts.filter((artifact) => !/\.(png|jpg|jpeg|webp)$/i.test(artifact.filename)),
)

function openPreview(url: string) {
  previewUrl.value = url
  previewVisible.value = true
}
</script>

<style scoped>
.artifact-card {
  margin-top: 20px;
}

.artifact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.artifact-item {
  border: 1px solid #ebeef5;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.artifact-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
}

.artifact-image {
  width: 100%;
  height: 140px;
  object-fit: cover;
  display: block;
  background: #f5f7fa;
}

.artifact-name {
  padding: 10px 12px;
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.artifact-links {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.preview-image {
  width: 100%;
  max-height: 75vh;
  object-fit: contain;
  display: block;
}
</style>
