---
name: frontend-rules
description: 前端架构约定，确保可扩展性和一致性
alwaysApply: true
globs: "frontend/**/*.{ts,vue}"
---

# 前端规则

## API 调用（强制）

- 所有 HTTP 调用通过 `@/api/` 下的封装函数，禁止在组件里直接 `request.get/post`
- `@/api/` 按资源划分：`@/api/dataset.ts` / `@/api/model.ts` / `@/api/task.ts` 等
- 每个 api 函数必须有明确的请求参数类型和返回值类型
- 公共类型定义在 `@/types/` 下，跨 api / 组件复用

```ts
// @/api/dataset.ts
import request from './request'
import type { Dataset, DatasetCreate } from '@/types/dataset'

export function listDatasets(page = 1, pageSize = 20): Promise<Dataset[]> {
  return request.get('/datasets', { params: { page, page_size: pageSize } })
}
```

## 类型定义

- 业务实体类型放 `@/types/{module}.ts`
- 禁止在组件 `<script setup>` 中重复定义同一实体的 interface
- API 响应错误结构统一定义在 `@/types/api.ts`

## 状态管理

- 跨页面共享的状态用 Pinia store，定义在 `@/stores/{module}.ts`
- 单页面内部状态用 `ref` / `reactive`，不用 store
- 用户信息、当前数据集、标注草稿等跨页状态必须用 store

## 组件组织

- `views/` 下页面级组件，文件名 PascalCase（`DatasetList.vue`）
- `views/{module}/components/` 下放该模块专用子组件
- `components/` 下放跨模块通用组件
- 组件 `<template>` + `<script>` 部分超过 250 行需拆分（`<style>` 不计）

## 路由

- 路由定义集中在 `@/router/index.ts`
- 路由 `meta` 字段用于权限、面包屑、菜单标题
- 动态参数用 kebab-case：`/annotation/workspace/:datasetId`

## 错误处理

- API 调用失败统一用 `ElMessage.error`，禁止 `console.error` + 静默
- `catch (err: unknown)` 后必须类型守卫，禁止 `as any`
- 表单校验错误就近提示，业务错误用 `ElMessage`，致命错误用 `ElMessageBox.alert`

## 禁止事项

- 禁止直接 import `request.ts` 到 `views/`，必须通过 `@/api/` 中转
- 禁止在多处定义同名 interface
- 禁止 `as any` / `: any`
- 禁止组件直接修改 props
