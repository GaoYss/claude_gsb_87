import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/dashboard' },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: '总览' },
  },
  {
    path: '/reservoirs',
    name: 'reservoir-list',
    component: () => import('@/views/reservoir/ReservoirListView.vue'),
    meta: { title: '水库台账' },
  },
  {
    path: '/reservoirs/new',
    name: 'reservoir-create',
    component: () => import('@/views/reservoir/ReservoirFormView.vue'),
    meta: { title: '新增水库' },
  },
  {
    path: '/reservoirs/:id(\\d+)',
    name: 'reservoir-detail',
    component: () => import('@/views/reservoir/ReservoirDetailView.vue'),
    meta: { title: '水库详情' },
  },
  {
    path: '/reservoirs/:id(\\d+)/edit',
    name: 'reservoir-edit',
    component: () => import('@/views/reservoir/ReservoirFormView.vue'),
    meta: { title: '编辑水库' },
  },
  {
    path: '/inspections',
    name: 'inspection-list',
    component: () => import('@/views/inspection/InspectionListView.vue'),
    meta: { title: '巡查记录' },
  },
  {
    path: '/inspections/new',
    name: 'inspection-create',
    component: () => import('@/views/inspection/InspectionFormView.vue'),
    meta: { title: '录入巡查记录' },
  },
  {
    path: '/inspections/:id(\\d+)',
    name: 'inspection-detail',
    component: () => import('@/views/inspection/InspectionDetailView.vue'),
    meta: { title: '巡查记录详情' },
  },
  {
    path: '/inspections/:id(\\d+)/edit',
    name: 'inspection-edit',
    component: () => import('@/views/inspection/InspectionFormView.vue'),
    meta: { title: '编辑巡查记录' },
  },
  {
    path: '/hazards',
    name: 'hazard-list',
    component: () => import('@/views/hazard/HazardListView.vue'),
    meta: { title: '隐患与整改' },
  },
  {
    path: '/hazards/new',
    name: 'hazard-create',
    component: () => import('@/views/hazard/HazardFormView.vue'),
    meta: { title: '登记隐患' },
  },
  {
    path: '/hazards/:id(\\d+)',
    name: 'hazard-detail',
    component: () => import('@/views/hazard/HazardDetailView.vue'),
    meta: { title: '隐患详情' },
  },
  {
    path: '/hazards/:id(\\d+)/edit',
    name: 'hazard-edit',
    component: () => import('@/views/hazard/HazardFormView.vue'),
    meta: { title: '编辑隐患' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: '页面不存在' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.afterEach((to) => {
  document.title = to.meta?.title ? `${to.meta.title} · 水库巡查记录系统` : '水库日常巡查记录系统'
})

export default router

