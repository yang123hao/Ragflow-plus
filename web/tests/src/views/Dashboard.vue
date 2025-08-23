<template>
  <div class="dashboard">
    <h2>仪表板</h2>
    <div class="welcome">
      <p>欢迎回来，{{ username }}！</p>
    </div>
    
    <div class="token-info">
      <h3>JWT令牌信息</h3>
      <div class="info-card">
        <p><strong>令牌状态：</strong> 
          <span :class="['status', tokenStatus]">{{ tokenStatusText }}</span>
        </p>
        <p><strong>过期时间：</strong> {{ expiryTime }}</p>
        <p><strong>剩余时间：</strong> {{ remainingTime }}</p>
        <p><strong>令牌：</strong></p>
        <div class="token-display">
          <code>{{ displayToken }}</code>
        </div>
      </div>
    </div>
    
    <div class="actions">
      <button @click="logout" class="logout-btn">退出登录</button>
      <button @click="refreshToken" class="refresh-btn">刷新令牌</button>
    </div>
    
    <div class="auto-logout-info">
      <h4>自动退出功能</h4>
      <p>系统会每30秒自动检查令牌是否过期</p>
      <p>如果令牌过期，将自动退出登录并跳转到登录页面</p>
      <p><strong>当前检查状态：</strong> 
        <span :class="['status', checkStatus]">{{ checkStatusText }}</span>
      </p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Dashboard',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const username = ref('administrator')
    const tokenStatus = ref('valid')
    const checkStatus = ref('active')
    const remainingTime = ref('')
    const expiryTime = ref('')
    const displayToken = ref('')
    
    let checkInterval = null
    let timeInterval = null
    
    // 计算属性
    const tokenStatusText = computed(() => {
      switch (tokenStatus.value) {
        case 'valid': return '有效'
        case 'expired': return '已过期'
        case 'expiring': return '即将过期'
        default: return '未知'
      }
    })
    
    const checkStatusText = computed(() => {
      switch (checkStatus.value) {
        case 'active': return '活跃'
        case 'inactive': return '停止'
        default: return '未知'
      }
    })
    
    // 解析JWT令牌
    const parseToken = () => {
      try {
        const token = authStore.getToken
        if (!token) {
          tokenStatus.value = 'expired'
          return
        }
        
        displayToken.value = token
        
        const payload = JSON.parse(atob(token.split('.')[1]))
        const currentTime = Math.floor(Date.now() / 1000)
        const expTime = payload.exp
        
        // 计算剩余时间
        const remaining = expTime - currentTime
        
        if (remaining <= 0) {
          tokenStatus.value = 'expired'
          remainingTime.value = '已过期'
          expiryTime.value = new Date(expTime * 1000).toLocaleString('zh-CN')
          // 自动退出
          setTimeout(() => {
            authStore.logout()
            router.push('/login')
          }, 1000)
        } else if (remaining <= 60) {
          tokenStatus.value = 'expiring'
          remainingTime.value = `${remaining}秒`
          expiryTime.value = new Date(expTime * 1000).toLocaleString('zh-CN')
        } else {
          tokenStatus.value = 'valid'
          const minutes = Math.floor(remaining / 60)
          const seconds = remaining % 60
          remainingTime.value = `${minutes}分${seconds}秒`
          expiryTime.value = new Date(expTime * 1000).toLocaleString('zh-CN')
        }
      } catch (error) {
        tokenStatus.value = 'expired'
        remainingTime.value = '解析错误'
      }
    }
    
    // 定期检查令牌
    const startTokenCheck = () => {
      parseToken()
      timeInterval = setInterval(parseToken, 1000) // 每秒更新一次
    }
    
    // 退出登录
    const logout = () => {
      authStore.logout()
      router.push('/login')
    }
    
    // 刷新令牌（重新登录）
    const refreshToken = () => {
      router.push('/login')
    }
    
    // 组件挂载
    onMounted(() => {
      if (!authStore.isAuthenticated) {
        router.push('/login')
        return
      }
      
      startTokenCheck()
      
      // 启动自动检查
      checkInterval = setInterval(() => {
        const isValid = authStore.checkTokenValidity()
        if (!isValid) {
          checkStatus.value = 'inactive'
          router.push('/login')
        }
      }, 30000)
    })
    
    // 组件卸载
    onUnmounted(() => {
      if (timeInterval) clearInterval(timeInterval)
      if (checkInterval) clearInterval(checkInterval)
    })
    
    return {
      username,
      tokenStatus,
      checkStatus,
      remainingTime,
      expiryTime,
      displayToken,
      tokenStatusText,
      checkStatusText,
      logout,
      refreshToken
    }
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.welcome {
  background: #e8f5e8;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: center;
}

.token-info {
  margin-bottom: 30px;
}

.info-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.info-card p {
  margin: 10px 0;
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
}

.status.valid {
  background: #d4edda;
  color: #155724;
}

.status.expired {
  background: #f8d7da;
  color: #721c24;
}

.status.expiring {
  background: #fff3cd;
  color: #856404;
}

.status.active {
  background: #d1ecf1;
  color: #0c5460;
}

.status.inactive {
  background: #f8d7da;
  color: #721c24;
}

.token-display {
  background: #f1f3f4;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
  word-break: break-all;
  font-size: 12px;
}

.actions {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.actions button {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

.logout-btn {
  background: #dc3545;
  color: white;
}

.refresh-btn {
  background: #17a2b8;
  color: white;
}

.auto-logout-info {
  background: #fff3cd;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #ffeaa7;
}

.auto-logout-info h4 {
  margin-top: 0;
  color: #856404;
}

.auto-logout-info p {
  margin: 8px 0;
  color: #856404;
}
</style>
