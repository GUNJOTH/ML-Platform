---
name: code-style
description: 代码风格与格式规范，写入代码前必读
alwaysApply: true
globs: "**/*.py,**/*.ts,**/*.vue"
---

# 代码风格规范

## Python

- 函数体不超过 50 行，超出则拆分
- 类不超过 200 行，超出则拆分职责
- 所有函数参数和返回值必须有类型注解
- 禁止使用 print，使用 logging 模块
- 命名：snake_case（变量/函数/模块），PascalCase（类）
- 单个模块只导出一个核心类或一组紧密相关的函数
- 圈复杂度不超过 10

## TypeScript / Vue

- 禁止使用 any 类型，必须明确类型
- Vue 组件不超过 200 行，超出则拆分子组件
- Props 必须定义类型接口
- 命名：camelCase（变量/函数），PascalCase（类/组件/接口/类型）
- 使用 Composition API + setup 语法糖

## 通用

- 注释只写 WHY（为什么这样做），不写 WHAT（代码做了什么）
- 不写无意义的注释，如 "// 获取用户" 在 getUser() 上面
- 一个文件只做一件事（单一职责）
- 优先复用已有代码，禁止重复实现相同逻辑
- 不引入不必要的依赖
