# 待处理问题清单

## 严重（阻碍核心功能运行）

| # | 缺失项 | 说明 | 状态 |
|---|--------|------|------|
| 1 | 认证/授权体系 | 无 User/Role 模型、无 JWT、无登录接口、无路由守卫 | 待处理 |
| 2 | 用户管理后端 | menu 有 /system/users 但后端无 user router/service/model | 待处理 |
| 3 | 标注批次后端 | 前端有 BatchList 但后端无 AnnotationBatch 表和接口 | 待处理 |
| 4 | 预处理任务后端 | 前端有 PreprocessList 但后端无对应逻辑 | 待处理 |
| 5 | Alembic 初始迁移 | versions/ 为空，数据库表无法创建 | 已处理 |
| 6 | YOLOv8 框架适配 | frameworks/yolov8/ 是空壳 | 已处理 |
| 7 | Canvas 标注实现 | useCanvas.ts 为空，无法画 BBox | 已处理 |
| 8 | Docker 部署 | 无 docker-compose.yml | 待处理 |

## 中等（功能不完整）

| # | 缺失项 | 说明 | 状态 |
|---|--------|------|------|
| 9 | 全局 exception handler | main.py 未注册异常处理器 | 待处理 |
| 10 | WebSocket 进度推送 | 训练进度无实时推送机制 | 已处理 |
| 11 | 结构化日志配置 | 无全局 logging 配置，无 JSON 输出 | 待处理 |
| 12 | TaskRunner 执行逻辑 | SyncRunner 什么都不做，create_task 不触发 runner | 已处理 |
| 13 | stats router 真实统计 | 当前返回硬编码字符串 | 待处理 |
| 14 | Inference/Evaluation 实现 | Service 仅打日志，不做实际推理/评估 | 已处理 |
| 15 | 后端测试用例 | tests/ 目录无实际测试 | 待处理 |
| 16 | 前端登录页面 | 无 /login 路由和 Login.vue | 待处理 |
| 17 | 前端 404 页面 | 无 catchall 路由，访问无效路径白屏 | 待处理 |
| 18 | 前端 api 封装不完整 | 缺少 user/role/log/batch/upload/stats/label API | 待处理 |
| 19 | 前端 types 不完整 | 缺少 User/Role/OperationLog/Batch 类型 | 待处理 |
| 20 | 前端 stores 不完整 | 缺少 userStore/datasetStore/annotationStore | 待处理 |
| 21 | Header 缺少用户功能 | 无用户头像、用户名、下拉菜单、登出按钮 | 待处理 |
| 22 | 页面未调用 API | 所有表格空 ref，无 onMounted 加载数据 | 待处理 |
| 23 | CI/CD 配置 | 无 .github/workflows/ | 待处理 |
| 24 | 架构文档 | 无 ARCHITECTURE.md | 待处理 |
| 25 | 质检审核后端接口 | 前端 ReviewList 有但后端无通过/驳回接口 | 待处理 |

## 轻微（代码清理/优化）

| # | 缺失项 | 说明 | 状态 |
|---|--------|------|------|
| 26 | 旧页面文件未清理 | views/dataset, views/inference, views/evaluation, views/task 重复 | 待处理 |
| 27 | SidebarItem 多余图标 | iconMap 有 VideoPlay/MagicStick/DataAnalysis 但 menu 未使用 | 待处理 |
| 28 | upload 大文件内存溢出 | await file.read() 对 500MB 文件会 OOM，应流式写入 | 待处理 |
| 29 | request.ts 缺 token 注入 | 请求拦截器无 Authorization header | 待处理 |
| 30 | 前端无全局 Loading | 无 NProgress 或加载指示器 | 待处理 |
| 31 | Doris 连接未使用 | db/doris.py 存在但无任何代码引用 | 待处理 |
| 32 | README 缺数据库初始化步骤 | 快速启动中未说明如何创建数据库 | 待处理 |
| 33 | 前端缺 .env.example | request.ts 引用环境变量但无示例文件 | 待处理 |
