---
name: code-style
description: 代码风格与格式规范，写入代码前必读
alwaysApply: true
globs: "**/*.py,**/*.ts,**/*.vue"
---

# 代码风格规范

## Python

- 函数体建议不超过 50 行；超出需在 commit message 说明原因（如外部库回调链不便拆分）
- 类建议不超过 200 行；超出需在 commit message 说明原因
- 所有函数参数和返回值必须有类型注解
- 禁止使用 `print`，使用 `logging` 模块
- 命名：snake_case（变量/函数/模块），PascalCase（类）
- 业务异常用 `app.exceptions.*`，必须在 module 顶部 import，禁止函数内重复 import
- 一个模块导出一组紧密相关的类或函数（如 dataset.py 同时导出 Dataset/Image/Label 是允许的）

## TypeScript / Vue

- 禁止使用 `any` 类型，必须明确类型
- 禁止 `as any` 作为类型守卫的替代品；处理 `unknown` 用类型守卫或可选链
- Vue 组件 `<template>` + `<script>` 部分建议不超过 250 行（`<style>` 不计入）；超出需拆分子组件
- Props 必须定义类型接口
- 命名：camelCase（变量/函数），PascalCase（类/组件/接口/类型）
- 使用 Composition API + `<script setup lang="ts">` 语法糖
- `catch (err: unknown)` 后必须用类型守卫缩窄类型，禁止直接断言

## 通用

- 注释只写 WHY（为什么这样做），不写 WHAT（代码做了什么）
- 不写无意义的注释，如 `// 获取用户` 在 `getUser()` 上面
- 一个文件只做一件事（单一职责）
- 优先复用已有代码，禁止重复实现相同逻辑
- 不引入不必要的依赖
