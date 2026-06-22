import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Dashboard.vue'),
        meta: { title: '概览' },
      },
      {
        path: 'data/datasets',
        name: 'Datasets',
        component: () => import('@/views/data/DatasetList.vue'),
        meta: { title: '数据集管理' },
      },
      {
        path: 'data/preprocess',
        name: 'Preprocess',
        component: () => import('@/views/data/PreprocessList.vue'),
        meta: { title: '预处理任务' },
      },
      {
        path: 'data/versions',
        name: 'DatasetVersions',
        component: () => import('@/views/data/DatasetVersionList.vue'),
        meta: { title: '数据集版本 / 导出记录' },
      },
      {
        path: 'data/versions/new',
        name: 'DatasetVersionCreate',
        component: () => import('@/views/data/DatasetVersionCreate.vue'),
        meta: { title: '新建数据集版本' },
      },
      {
        path: 'data/versions/compare',
        name: 'DatasetVersionCompare',
        component: () => import('@/views/data/DatasetVersionCompare.vue'),
        meta: { title: '数据集版本对比' },
      },
      {
        path: 'data/versions/rules',
        name: 'DatasetVersionRules',
        component: () => import('@/views/data/DatasetVersionRules.vue'),
        meta: { title: '版本规则' },
      },
      {
        path: 'data/versions/validation/:versionId',
        name: 'DatasetVersionValidation',
        component: () => import('@/views/data/DatasetVersionValidation.vue'),
        meta: { title: '版本校验结果' },
      },
      {
        path: 'data/versions/exports/:recordId',
        name: 'DatasetExportRecordDetail',
        component: () => import('@/views/data/DatasetExportRecordDetail.vue'),
        meta: { title: '导出记录详情' },
      },
      {
        path: 'annotation/workspace/:datasetId?',
        name: 'AnnotationWorkspace',
        component: () => import('@/views/annotation/AnnotationWorkspace.vue'),
        meta: { title: '标注工作台' },
      },
      {
        path: 'annotation/batches',
        name: 'AnnotationBatches',
        component: () => import('@/views/annotation/BatchList.vue'),
        meta: { title: '标注批次' },
      },
      {
        path: 'annotation/review',
        name: 'AnnotationReview',
        component: () => import('@/views/annotation/ReviewList.vue'),
        meta: { title: '质检审核' },
      },
      {
        path: 'model/list',
        name: 'Models',
        component: () => import('@/views/model/ModelList.vue'),
        meta: { title: '模型管理' },
      },
      {
        path: 'model/training',
        name: 'Training',
        component: () => import('@/views/model/TrainingList.vue'),
        meta: { title: '训练任务' },
      },
      {
        path: 'model/evaluation',
        name: 'Evaluation',
        component: () => import('@/views/model/EvaluationReport.vue'),
        meta: { title: '模型评估' },
      },
      {
        path: 'model/evaluation-history',
        name: 'EvaluationHistory',
        component: () => import('@/views/model/EvaluationHistory.vue'),
        meta: { title: '评估历史' },
      },
      {
        path: 'model/inference',
        name: 'Inference',
        component: () => import('@/views/model/InferenceWorkspace.vue'),
        meta: { title: '模型推理' },
      },
      {
        path: 'system/users',
        name: 'Users',
        component: () => import('@/views/system/UserList.vue'),
        meta: { title: '用户管理' },
      },
      {
        path: 'system/roles',
        name: 'Roles',
        component: () => import('@/views/system/RoleList.vue'),
        meta: { title: '角色权限' },
      },
      {
        path: 'system/logs',
        name: 'Logs',
        component: () => import('@/views/system/LogList.vue'),
        meta: { title: '操作日志' },
      },
      {
        path: 'system/config',
        name: 'Config',
        component: () => import('@/views/system/ConfigPage.vue'),
        meta: { title: '系统配置' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
