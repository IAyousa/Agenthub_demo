import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(
  (config) => {
    // 注入 JWT Token（Auth Store 的 token 持久化在 localStorage）
    const token = localStorage.getItem('agenthub_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        // Token 过期或无效 → 清除登录态并跳转登录页
        localStorage.removeItem('agenthub_token')
        localStorage.removeItem('agenthub_user')
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      } else if (status === 404) {
        console.warn(`[API] 资源未找到: ${error.config?.url}`)
      } else if (status === 500) {
        console.error(`[API] 服务器错误: ${error.config?.url}`, data)
      }
    } else if (error.request) {
      console.error('[API] 网络错误: 无法连接到后端服务')
    }
    return Promise.reject(error)
  }
)

export default apiClient
