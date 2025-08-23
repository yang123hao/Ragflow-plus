import { pinia } from "@/pinia"
import { resetRouter } from "@/router"
import { routerConfig } from "@/router/config"
import { getCurrentUserApi } from "@@/apis/users"
import { setToken as _setToken, getToken, removeToken } from "@@/utils/cache/cookies"
import { useSettingsStore } from "./settings"
import { useTagsViewStore } from "./tags-view"

export const useUserStore = defineStore("user", () => {
  const token = ref<string>(getToken() || "")
  const roles = ref<string[]>([])
  const username = ref<string>("")
  const avatar = ref<string>("https://pic1.zhimg.com/v2-aaf12b68b54b8812e6b449e7368d30cf_l.jpg?source=32738c0c&needBackground=1")
  const tagsViewStore = useTagsViewStore()
  const settingsStore = useSettingsStore()
  
  // JWT过期检查定时器
  let tokenCheckTimer: NodeJS.Timeout | null = null

  // 检查JWT是否过期
  const checkTokenExpiration = () => {
    const currentToken = getToken()
    if (!currentToken) return false
    
    try {
      // 解析JWT token（不验证签名，只获取payload）
      const base64Url = currentToken.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
      }).join(''))
      
      const payload = JSON.parse(jsonPayload)
      const currentTime = Math.floor(Date.now() / 1000)
      
      // 检查是否过期
      if (payload.exp && currentTime > payload.exp) {
        ElMessage.error("登录已过期，请重新登录")
        logout()
        return false
      }
      
      return true
    } catch (error) {
      console.error("Token解析失败:", error)
      logout()
      return false
    }
  }

  // 设置 Token
  const setToken = (value: string) => {
    _setToken(value)
    token.value = value
    
    // 清除之前的定时器
    if (tokenCheckTimer) {
      clearInterval(tokenCheckTimer)
    }
    
    // 设置定时检查JWT过期（每分钟检查一次）
    tokenCheckTimer = setInterval(() => {
      if (!checkTokenExpiration()) {
        // 如果token过期，清除定时器
        if (tokenCheckTimer) {
          clearInterval(tokenCheckTimer)
          tokenCheckTimer = null
        }
      }
    }, 60000) // 60秒检查一次
  }

  // 获取用户详情
  const getInfo = async () => {
    const { data } = await getCurrentUserApi()
    username.value = data.username
    // 验证返回的 roles 是否为一个非空数组，否则塞入一个没有任何作用的默认角色，防止路由守卫逻辑进入无限循环
    roles.value = data.roles?.length > 0 ? data.roles : routerConfig.defaultRoles
  }

  // 模拟角色变化
  const changeRoles = (role: string) => {
    const newToken = `token-${role}`
    token.value = newToken
    _setToken(newToken)
    // 用刷新页面代替重新登录
    location.reload()
  }

  // 登出
  const logout = () => {
    // 清除定时器
    if (tokenCheckTimer) {
      clearInterval(tokenCheckTimer)
      tokenCheckTimer = null
    }
    
    removeToken()
    token.value = ""
    roles.value = []
    resetRouter()
    resetTagsView()
    
    // 跳转到登录页
    window.location.href = "/login"
  }

  // 重置 Token
  const resetToken = () => {
    // 清除定时器
    if (tokenCheckTimer) {
      clearInterval(tokenCheckTimer)
      tokenCheckTimer = null
    }
    
    removeToken()
    token.value = ""
    roles.value = []
  }

  // 重置 Visited Views 和 Cached Views
  const resetTagsView = () => {
    if (!settingsStore.cacheTagsView) {
      tagsViewStore.delAllVisitedViews()
      tagsViewStore.delAllCachedViews()
    }
  }

  // 初始化时检查token
  const initTokenCheck = () => {
    if (getToken()) {
      checkTokenExpiration()
      // 设置定时检查
      tokenCheckTimer = setInterval(() => {
        if (!checkTokenExpiration()) {
          if (tokenCheckTimer) {
            clearInterval(tokenCheckTimer)
            tokenCheckTimer = null
          }
        }
      }, 60000)
    }
  }

  return { 
    token, 
    roles, 
    username, 
    avatar, 
    setToken, 
    getInfo, 
    changeRoles, 
    logout, 
    resetToken, 
    checkTokenExpiration,
    initTokenCheck
  }
})

/**
 * @description 在 SPA 应用中可用于在 pinia 实例被激活前使用 store
 * @description 在 SSR 应用中可用于在 setup 外使用 store
 */
export function useUserStoreOutside() {
  return useUserStore(pinia)
}
