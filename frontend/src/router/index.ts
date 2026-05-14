import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '../components/layout/AppLayout.vue'

const routes = [
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', name: 'dashboard', component: () => import('../views/DashboardView.vue') },
      { path: 'templates', name: 'templates', component: () => import('../views/TemplateListView.vue') },
      { path: 'templates/:id', name: 'template-detail', component: () => import('../views/TemplateDetailView.vue') },
      { path: 'releases', name: 'releases', component: () => import('../views/ReleaseListView.vue') },
      { path: 'releases/:id', name: 'release-detail', component: () => import('../views/ReleaseDetailView.vue') },
      { path: 'settings', name: 'settings', component: () => import('../views/SettingsView.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
