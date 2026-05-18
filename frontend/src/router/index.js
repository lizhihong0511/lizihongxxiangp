import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'dashboard', component: () => import('../views/DashboardView.vue') },
  { path: '/qa', name: 'qa', component: () => import('../views/QaView.vue') },
  { path: '/bank', name: 'bank', component: () => import('../views/QuestionBankView.vue') },
  { path: '/practice', name: 'practice', component: () => import('../views/PracticeView.vue') },
  { path: '/wrong', name: 'wrong', component: () => import('../views/WrongBookView.vue') },
  { path: '/profile', name: 'profile', component: () => import('../views/ProfileView.vue') },
  { path: '/admin', name: 'admin', component: () => import('../views/AdminView.vue') },
]

export default createRouter({
  history: createWebHashHistory(),
  routes,
})
