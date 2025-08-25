<template>
  <div class="login">
    <h2>用户登录</h2>
    <div class="login-form">
      <div class="form-group">
        <label for="username">用户名：</label>
        <input 
          type="text" 
          id="username" 
          v-model="username" 
          placeholder="请输入用户名"
          required
        />
      </div>
      
      <div class="form-group">
        <label for="password">密码：</label>
        <input 
          type="password" 
          id="password" 
          v-model="password" 
          placeholder="请输入密码"
          required
        />
      </div>
      
      <button @click="handleLogin" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>
      
      <div v-if="message" :class="['message', messageType]">
        {{ message }}
      </div>
    </div>

  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const username = ref('')
    const password = ref('')
    const loading = ref(false)
    const message = ref('')
    const messageType = ref('')
    
    const handleLogin = async () => {
      if (!username.value || !password.value) {
        message.value = '请输入用户名和密码'
        messageType.value = 'error'
        return
      }
      
      loading.value = true
      message.value = ''
      
      try {
        const result = await authStore.login(username.value, password.value)
        
        if (result.success) {
          message.value = result.message
          messageType.value = 'success'
          
          // 延迟跳转，让用户看到成功消息
          setTimeout(() => {
            router.push('/dashboard')
          }, 1000)
        } else {
          message.value = result.message
          messageType.value = 'error'
        }
      } catch (error) {
        message.value = '登录失败，请重试'
        messageType.value = 'error'
      } finally {
        loading.value = false
      }
    }
    
    return {
      username,
      password,
      loading,
      message,
      messageType,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}

.login-form {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

button {
  width: 100%;
  padding: 12px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.message {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.info {
  background: #e7f3ff;
  padding: 15px;
  border-radius: 8px;
  text-align: left;
}

.info p {
  margin: 5px 0;
}

.info small {
  color: #666;
}
</style>
