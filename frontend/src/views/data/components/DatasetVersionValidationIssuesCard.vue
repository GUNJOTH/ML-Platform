<template>
  <el-card class="section-card">
    <template #header>{{ title }}</template>
    <div v-if="!validationResult" class="empty-validation">
      {{ emptyText }}
    </div>
    <template v-else>
      <div class="validation-status">
        <el-tag :type="validationResult.passed ? 'success' : 'danger'">
          {{ validationResult.passed ? successText : failureText }}
        </el-tag>
      </div>
      <div v-if="issues.length" class="validation-issues">
        <div
          v-for="issue in issues"
          :key="`${issue.level}-${issue.code}-${issue.message}`"
          class="validation-issue"
          :class="`is-${issue.level}`"
        >
          <div class="issue-title">{{ issue.title }}</div>
          <div class="issue-message">{{ issue.message }}</div>
        </div>
      </div>
      <div v-else class="empty-validation success">
        当前未发现阻断项或警告项。
      </div>
    </template>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DatasetVersionValidationResult } from '@/types/dataset-version'
import {
  collectValidationIssueDisplay,
  type ValidationIssueDisplay,
} from '../datasetVersionValidation'

const props = defineProps<{
  title: string
  emptyText: string
  successText: string
  failureText: string
  validationResult: DatasetVersionValidationResult | null
}>()

const issues = computed<ValidationIssueDisplay[]>(() =>
  collectValidationIssueDisplay(props.validationResult),
)
</script>

<style scoped>
.section-card {
  margin-bottom: 20px;
  border-radius: 16px;
}

.empty-validation {
  padding: 14px 16px;
  border-radius: 12px;
  background: #f8fafc;
  color: #64748b;
}

.empty-validation.success {
  background: #f0fdf4;
  color: #166534;
}

.validation-status {
  margin-bottom: 14px;
}

.validation-issues {
  display: grid;
  gap: 12px;
}

.validation-issue {
  padding: 14px 16px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: #fff;
}

.validation-issue.is-error {
  border-color: #fecaca;
  background: #fef2f2;
}

.validation-issue.is-warning {
  border-color: #fde68a;
  background: #fffbeb;
}

.issue-title {
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
}

.issue-message {
  margin-top: 6px;
  color: #475569;
  line-height: 1.6;
}
</style>
