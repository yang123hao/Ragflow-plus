import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
    isAuthenticated: false
  }),

  getters: {
    getToken: (state) => state.token,
    getUser: (state) => state.user
  },

  actions: {
    async login(username, password) {
      try {
        const response = await axios.post('/api/v1/auth/login', {
          username,
          password
        })
        
        if (response.data.code === 0) {
          this.token = response.data.data.token
          this.isAuthenticated = true
          localStorage.setItem('token', this.token)
          
          // 设置axios默认headers
          axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
          
          return { success: true, message: response.data.message }
        } else {
          return { success: false, message: response.data.message }
        }
      } catch (error) {
        return { success: false, message: '登录失败，请检查网络连接' }
      }
    },

    logout() {
      this.token = null
      this.user = null
      this.isAuthenticated = false
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    },

    // 检查token是否过期
    async checkTokenValidity() {
      if (!this.token) {
        this.logout()
        return false
      }

      try {
        // 解析JWT token
        const payload = JSON.parse(atob(this.token.split('.')[1]))
        const currentTime = Math.floor(Date.now() / 1000)
        
        if (currentTime > payload.exp) {
          // Token已过期
          this.logout()
          return false
        }
        
        return true
      } catch (error) {
        // Token格式错误
        this.logout()
        return false
      }
    },

    // 初始化时检查token
    init() {
      if (this.token) {
        this.isAuthenticated = true
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        
        // 定期检查token有效性
        setInterval(() => {
          this.checkTokenValidity()
        }, 30000) // 每30秒检查一次
      }
    }
  }
})
