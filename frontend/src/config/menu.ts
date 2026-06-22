export interface MenuItem {
  path: string
  title: string
  icon?: string
  children?: MenuItem[]
}

export const menuConfig: MenuItem[] = [
  { path: '/dashboard', title: '概览', icon: 'Odometer' },
  {
    path: '/data',
    title: '数据管理',
    icon: 'Files',
    children: [
      { path: '/data/datasets', title: '数据集管理' },
      { path: '/data/preprocess', title: '预处理任务' },
    ],
  },
  {
    path: '/annotation',
    title: '标注管理',
    icon: 'Edit',
    children: [
      { path: '/annotation/workspace', title: '标注工作台' },
      { path: '/annotation/batches', title: '标注批次' },
      { path: '/annotation/review', title: '质检审核' },
    ],
  },
  {
    path: '/model',
    title: '模型中心',
    icon: 'Cpu',
    children: [
      { path: '/model/list', title: '模型管理' },
      { path: '/model/training', title: '训练任务' },
      { path: '/model/evaluation', title: '模型评估' },
      { path: '/model/evaluation-history', title: '评估历史' },
      { path: '/model/inference', title: '模型推理' },
    ],
  },
  {
    path: '/system',
    title: '系统管理',
    icon: 'Setting',
    children: [
      { path: '/system/users', title: '用户管理' },
      { path: '/system/roles', title: '角色权限' },
      { path: '/system/logs', title: '操作日志' },
      { path: '/system/config', title: '系统配置' },
    ],
  },
]
