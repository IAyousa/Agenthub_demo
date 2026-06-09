import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/chat'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/chat/:conversationId?',
      name: 'chat',
      component: ChatView
    },
    {
      path: '/office/:conversationId?',
      name: 'office',
      component: () => import('../views/OfficeView.vue')
    }
  ]
})

// 全局导航守卫：未登录 → 跳转 /login
router.beforeEach((to, _from, next) => {
  if (to.path === '/login') {
    // 已登录 → 不需要重复登录
    const token = localStorage.getItem('agenthub_token')
    if (token) {
      next('/chat')
      return
    }
    next()
    return
  }

  // 其他路由 → 检查登录态
  const token = localStorage.getItem('agenthub_token')
  if (!token) {
    next('/login')
    return
  }
  next()
})

export default router
