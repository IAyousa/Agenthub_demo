import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/chat/conv_frontend_001'
    },
    {
      path: '/chat/:conversationId',
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

export default router
