import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import router from '../router'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const auth = useAuthStore()
      // vault/auth 状态检查相关接口的 401 不触发 logout，避免死循环
      const url = err.config?.url || ''
      if (url.includes('vault-status') || url.includes('unlock-vault') || url.includes('/auth/status') || url.includes('/auth/me')) {
        return Promise.reject(err)
      }
      auth.logout()
      router.push('/login')
    }
    return Promise.reject(err)
  }
)

export default api
