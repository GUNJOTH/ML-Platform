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
        meta: { title: '仪表盘', icon: 'Odometer' },
      },
      {
        path: 'datasets',
        name: 'Datasets',
        component: () => import('@/views/dataset/DatasetList.vue'),
        meta: { title: '数据集管理', icon: 'Files' },
      },
      {
        path: 'annotation/:datasetId?',
        name: 'Annotation',
        component: () => import('@/views/annotation/AnnotationWorkspace.vue'),
        meta: { title: '数据标注', icon: 'Edit' },
      },
      {
        path: 'models',
        name: 'Models',
        component: () => import('@/views/model/ModelList.vue'),
        meta: { title: '模型管理', icon: 'Cpu' },
      },
      {
        path: 'tasks',
        name: 'Tasks',
        component: () => import('@/views/task/TaskList.vue'),
        meta: { title: '训练任务', icon: 'VideoPlay' },
      },
      {
        path: 'inference',
        name: 'Inference',
        component: () => import('@/views/inference/InferenceWorkspace.vue'),
        meta: { title: '模型推理', icon: 'MagicStick' },
      },
      {
        path: 'evaluation',
        name: 'Evaluation',
        component: () => import('@/views/evaluation/EvaluationReport.vue'),
        meta: { title: '模型评估', icon: 'DataAnalysis' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
