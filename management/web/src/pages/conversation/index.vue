<script lang="ts" setup>
import type { TableData } from "@@/apis/tables/type"
import { getTableDataApi } from "@@/apis/tables"
import { ChatDotRound, User, Loading } from "@element-plus/icons-vue"
import { request } from "@/http/axios"

defineOptions({
  // 命名当前组件
  name: "ConversationManagement"
})

// #region 用户数据
const userList = ref<TableData[]>([])
const searchData = reactive({
  username: "",
  email: "",
  conversationKeyword: "" // 对话内容搜索关键字
})

// 用户列表滚动加载相关
const userLoading = ref(false)
const userHasMore = ref(true)
const userPage = ref(1)
const userPageSize = 20

// 排序状态
const sortData = reactive({
  sortBy: "create_date",
  sortOrder: "desc" // 默认排序顺序 (最新创建的在前)
})

/**
 * 获取用户列表数据
 * @param isLoadMore 是否为加载更多操作
 */
function getUserData(isLoadMore = false) {
  if (!isLoadMore) {
    userPage.value = 1
    userList.value = []
  }

  userLoading.value = true
  getTableDataApi({
    currentPage: userPage.value,
    size: userPageSize,
    username: searchData.username,
    email: searchData.email,
    sort_by: sortData.sortBy,
    sort_order: sortData.sortOrder
  }).then(({ data }) => {
    if (isLoadMore) {
      userList.value = [...userList.value, ...data.list]
    } else {
      userList.value = data.list
    }

    // 判断是否还有更多数据
    userHasMore.value = userList.value.length < data.total
  }).catch(() => {
    if (!isLoadMore) {
      userList.value = []
    }
  }).finally(() => {
    userLoading.value = false
  })
}

/**
 * 加载更多用户
 */
function loadMoreUsers() {
  if (userLoading.value || !userHasMore.value) return

  userPage.value++
  getUserData(true)
}

/**
 * 监听用户列表滚动事件
 * @param event DOM滚动事件对象
 */
function handleUserListScroll(event: Event) {
  // 将 event.target 断言为 HTMLElement 并检查是否存在
  const target = event.target as HTMLElement
  if (!target) return

  // 获取滚动相关属性
  const { scrollTop, scrollHeight, clientHeight } = target

  // 当滚动到距离底部100px时，加载更多数据
  if (scrollHeight - scrollTop - clientHeight < 100 && userHasMore.value && !userLoading.value) {
    loadMoreUsers()
  }
}
// #endregion

// #region 对话数据
// 定义对话数据类型
interface ConversationData {
  id: string // 修改为string类型
  name: string // 修改title为name
  latestMessage: string // 添加latestMessage字段
  createTime: string // 修改create_time为createTime
  updateTime: string
}

// 定义消息数据类型
interface MessageData {
  id: number
  conversation_id: number
  role: string
  content: string
  create_time: string
}

const conversationList = ref<ConversationData[]>([])
const messageList = ref<MessageData[]>([])
const conversationLoading = ref(false)
const messageLoading = ref(false)

// 对话列表滚动加载相关
const conversationHasMore = ref(true)
const conversationPage = ref(1)
const conversationPageSize = 20

// 消息列表滚动加载相关
const messageHasMore = ref(true)
const messagePage = ref(1)
const messagePageSize = 30

// 当前选中的用户和对话
const selectedUser = ref<TableData | null>(null)
const selectedConversation = ref<ConversationData | null>(null)

/**
 * 选择用户
 * @param user 用户数据
 */
function selectUser(user: TableData) {
  console.log("选择用户:", user)
  selectedUser.value = user
  selectedConversation.value = null
  messageList.value = []
  conversationPage.value = 1
  conversationHasMore.value = true
  getConversationsByUserId(user.id)
}

/**
 * 选择对话
 * @param conversation 对话数据
 */
function selectConversation(conversation: ConversationData) {
  selectedConversation.value = conversation
  messagePage.value = 1
  messageHasMore.value = true
  messageList.value = []
  getMessagesByConversationId(conversation.id)
}

/**
 * 获取用户的对话列表
 * @param userId 用户ID
 * @param isLoadMore 是否为加载更多操作
 */
function getConversationsByUserId(userId: string | number, isLoadMore = false) {
  conversationLoading.value = true
  
  // 构建请求参数
  const params: any = {
    user_id: userId,
    page: conversationPage.value,
    size: conversationPageSize,
    sort_by: "update_time",
    sort_order: "desc"
  }
  
  // 如果有搜索关键字，添加到参数中
  if (searchData.conversationKeyword.trim()) {
    params.keyword = searchData.conversationKeyword.trim()
  }
  
  console.log("请求对话列表，参数:", params)
  
  // 调用获取对话列表API
  request({
    url: `/api/v1/conversation`,
    method: 'GET',
    params
  }).then((response: any) => {
    console.log("对话列表API响应:", response)
    console.log("响应数据结构:", {
      hasData: !!response,
      hasDataData: !!response?.data,
      dataType: typeof response?.data,
      dataKeys: response?.data ? Object.keys(response.data) : 'undefined'
    })
    
    // 检查响应数据结构
    if (!response) {
      throw new Error("API响应为空")
    }
    
    if (!response.data) {
      throw new Error("API响应缺少data字段")
    }
    
    const data = response.data

    if (isLoadMore) {
      conversationList.value = [...conversationList.value, ...(data.list || [])]
    } else {
      conversationList.value = data.list || []
    }

    // 判断是否还有更多数据
    conversationHasMore.value = conversationList.value.length < (data.total || 0)
    
    console.log("处理后的对话列表:", conversationList.value)
    console.log("是否还有更多:", conversationHasMore.value)
    console.log("搜索结果数量:", conversationList.value.length)
    
    // 显示搜索结果信息
    if (searchData.conversationKeyword.trim()) {
      ElMessage.success(`搜索完成，找到 ${conversationList.value.length} 个对话`)
    }
  }).catch((error: any) => {
    console.error("获取对话列表失败:", error)
    ElMessage.error("获取对话列表失败")
    if (!isLoadMore) {
      conversationList.value = []
    }
  }).finally(() => {
    conversationLoading.value = false
  })
}

/**
 * 搜索对话
 */
function searchConversations() {
  const keyword = searchData.conversationKeyword.trim()
  console.log("执行搜索，关键字:", keyword)
  
  // 重置分页
  conversationPage.value = 1
  conversationHasMore.value = true
  conversationList.value = []
  
  // 显示搜索状态
  ElMessage.success(`正在搜索: ${keyword || '所有对话'}`)
  
  // 执行全局搜索，不需要选择用户
  searchAllConversations(keyword, false)
}

/**
 * 清空搜索
 */
function clearSearch() {
  searchData.conversationKeyword = ""
  
  // 重新加载所有对话（不带搜索条件）
  conversationPage.value = 1
  conversationHasMore.value = true
  conversationList.value = []
  searchAllConversations("", false)
}

/**
 * 加载更多对话
 */
function loadMoreConversations() {
  if (conversationLoading.value || !conversationHasMore.value) return

  conversationPage.value++
  
  if (searchData.conversationKeyword.trim()) {
    searchAllConversations(searchData.conversationKeyword.trim(), true)
  } else {
    searchAllConversations("", true)
  }
}

/**
 * 监听对话列表滚动事件
 */
function handleConversationListScroll(event: Event) {
  // 将 event.target 断言为 HTMLElement 并检查是否存在
  const target = event.target as HTMLElement
  if (!target) return

  // 获取滚动相关属性
  const { scrollTop, scrollHeight, clientHeight } = target

  // 当滚动到距离底部100px时，加载更多数据
  if (scrollHeight - scrollTop - clientHeight < 100 && conversationHasMore.value && !conversationLoading.value) {
    loadMoreConversations()
  }
}

/**
 * 全局搜索所有对话
 * @param keyword 搜索关键字
 * @param isLoadMore 是否为加载更多操作
 */
function searchAllConversations(keyword: string, isLoadMore = false) {
  conversationLoading.value = true
  
  // 构建请求参数 - 全局搜索不需要用户ID
  const params: any = {
    page: conversationPage.value,
    size: conversationPageSize,
    sort_by: "update_time",
    sort_order: "desc"
  }
  
  // 如果有搜索关键字，添加到参数中
  if (keyword) {
    params.keyword = keyword
  }
  
  console.log("全局搜索对话，参数:", params)
  
  // 调用全局搜索API - 使用新的全局搜索端点
  request({
    url: `/api/v1/conversation/search`,
    method: 'GET',
    params
  }).then((response: any) => {
    console.log("全局搜索API响应:", response)
    console.log("响应数据结构:", {
      hasData: !!response,
      hasDataData: !!response?.data,
      dataType: typeof response?.data,
      dataKeys: response?.data ? Object.keys(response.data) : 'undefined'
    })
    
    // 检查响应数据结构
    if (!response) {
      throw new Error("API响应为空")
    }
    
    if (!response.data) {
      throw new Error("API响应缺少data字段")
    }
    
    const data = response.data
    
    if (isLoadMore) {
      conversationList.value = [...conversationList.value, ...(data.list || [])]
    } else {
      conversationList.value = data.list || []
    }

    // 判断是否还有更多数据
    conversationHasMore.value = conversationList.value.length < (data.total || 0)
    
    console.log("全局搜索结果:", conversationList.value)
    console.log("是否还有更多:", conversationHasMore.value)
    console.log("搜索结果数量:", conversationList.value.length)
  }).catch((error: any) => {
    console.error("全局搜索失败:", error)
    console.error("错误详情:", {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      config: error.config,
      requestParams: params
    })
    
    // 根据错误类型显示不同的错误信息
    if (error.response?.status === 400) {
      ElMessage.error("请求参数错误，请检查搜索条件")
    } else if (error.response?.status === 404) {
      ElMessage.error("搜索API端点不存在，请联系管理员")
    } else if (error.response?.status === 500) {
      ElMessage.error("服务器内部错误，请稍后重试")
    } else if (error.code === 'NETWORK_ERROR') {
      ElMessage.error("网络连接失败，请检查网络")
    } else {
      ElMessage.error(`搜索失败: ${error.message}`)
    }
    
    conversationList.value = []
  }).finally(() => {
    conversationLoading.value = false
  })
}

/**
 * 获取对话的消息列表
 * @param conversationId 对话ID
 * @param isLoadMore 是否为加载更多操作
 */
function getMessagesByConversationId(conversationId: string, isLoadMore = false) {
  messageLoading.value = true

  // 调用获取消息列表API
  request({
    url: `/api/v1/conversation/${conversationId}/messages`,
    method: 'GET',
    params: {
      page: messagePage.value,
      size: messagePageSize,
      sort_by: "create_time",
      sort_order: "asc" // 按时间正序排列，旧消息在前
    }
  })
    .then((response: any) => {
      console.log("消息API响应:", response)
      console.log("响应数据结构:", {
        hasData: !!response,
        hasDataData: !!response?.data,
        dataType: typeof response?.data,
        dataKeys: response?.data ? Object.keys(response.data) : 'undefined'
      })
      
      // 检查响应数据结构
      if (!response) {
        throw new Error("API响应为空")
      }
      
      if (!response.data) {
        throw new Error("API响应缺少data字段")
      }
      
      const data = response.data
      // 在控制台输出获取到的消息数据
      console.log("获取到的消息数据:", data)

      // 处理消息数据
      let processedMessages: any[] = []

      if (data.list) {
        // 直接使用返回的消息列表
        const messages = data.list
        
        if (Array.isArray(messages)) {
          // 格式化消息数据
          processedMessages = messages.map((msg: any, index: number) => {
            return {
              id: msg.id || `msg-${index}`,
              conversation_id: conversationId,
              role: msg.role || "unknown",
              content: msg.content || "",
              create_time: msg.create_time || new Date().toISOString()
            }
          })
        } else {
          console.error("返回的消息数据不是数组:", messages)
        }
      } else {
        console.error("响应数据中没有list字段:", data)
      }

      console.log("处理后的消息数据:", processedMessages)

      if (isLoadMore) {
        // 防止重复加载：检查新消息是否已存在
        const existingIds = new Set(messageList.value.map(msg => msg.id))
        const uniqueNewMessages = processedMessages.filter((msg: { id: number }) => !existingIds.has(msg.id))

        // 追加新的唯一消息
        messageList.value = [...messageList.value, ...uniqueNewMessages]
        console.log(`加载了 ${uniqueNewMessages.length} 条新消息，过滤掉 ${processedMessages.length - uniqueNewMessages.length} 条重复消息`)
      } else {
        messageList.value = processedMessages
      }

      // 判断是否还有更多数据
      messageHasMore.value = messageList.value.length < (data.total || 0)

      // 如果不是加载更多，滚动到底部
      if (!isLoadMore && messageList.value.length > 0) {
        setTimeout(() => {
          const messageListEl = document.querySelector(".message-list")
          if (messageListEl) {
            messageListEl.scrollTop = messageListEl.scrollHeight
          }
        }, 100)
      }
    })
    .catch((error: any) => {
      console.error("获取消息列表失败:", error)
      ElMessage.error("获取消息列表失败")
      if (!isLoadMore) {
        messageList.value = []
      }
    })
    .finally(() => {
      messageLoading.value = false
    })
}

/**
 * 渲染消息内容，处理图片和链接
 * @param content 消息内容
 * @returns 处理后的HTML内容
 */
function renderMessageContent(content: string) {
  if (!content) return ""

  // 处理Markdown格式的图片
  let processedContent = content.replace(/!\[.*?\]\((.*?)\)/g, "<img src=\"$1\" class=\"message-image\" />")

  // 处理换行符
  processedContent = processedContent.replace(/\n/g, "<br>")

  return processedContent
}

/**
 * 加载更多消息
 */
function loadMoreMessages() {
  if (messageLoading.value || !messageHasMore.value || !selectedConversation.value) return

  messagePage.value++
  getMessagesByConversationId(selectedConversation.value.id, true)
}

/**
 * 监听消息列表滚动事件
 * @param event DOM滚动事件对象
 */
function handleMessageListScroll(event: Event) {
  // 将 event.target 断言为 HTMLElement 并检查是否存在
  const target = event.target as HTMLElement
  if (!target) return

  // 获取滚动相关属性
  const { scrollTop, scrollHeight, clientHeight } = target

  // 当滚动到距离底部100px时，加载更多数据（向下滚动加载更多）
  if (scrollHeight - scrollTop - clientHeight < 100 && messageHasMore.value && !messageLoading.value) {
    loadMoreMessages()
  }
}

// 初始加载数据
onMounted(() => {
  getUserData()
  // 默认加载所有对话
  searchAllConversations("", false)
})
</script>

<template>
  <div class="app-container">
    <!-- 多级卡片区域 -->
    <div class="conversation-cards-container">
      <!-- 第一个卡片：用户列表 -->
      <el-card shadow="hover" class="user-card">
        <template #header>
          <div class="card-header">
            <span>用户列表</span>
          </div>
        </template>
        <el-card v-loading="" shadow="never" class="search-wrapper">
          <el-form ref="searchFormRef" :inline="true" :model="searchData">
            <el-form-item prop="conversationKeyword" label="对话">
              <el-input 
                v-model="searchData.conversationKeyword" 
                placeholder="请输入" 
                @keyup.enter="searchConversations"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="searchConversations">
                搜索
              </el-button>
            </el-form-item>
            <el-form-item>
              <el-button @click="clearSearch">
                清空
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
        <div class="user-list" @scroll="handleUserListScroll">
          <div
            v-for="user in userList"
            :key="user.id"
            class="user-item"
            :class="{ active: selectedUser?.id === user.id }"
            @click="selectUser(user)"
          >
            <el-avatar :size="32" :icon="User" />
            <div class="user-info">
              <div class="username">
                {{ user.username }}
              </div>
              <div class="email">
                {{ user.email }}
              </div>
            </div>
          </div>
          <div v-if="userLoading" class="loading-more">
            <el-icon class="loading-icon">
              <Loading />
            </el-icon>
            <span>加载中...</span>
          </div>
          <el-empty v-if="userList.length === 0 && !userLoading" description="暂无用户数据" />
        </div>
      </el-card>

      <!-- 第二个卡片：对话标题列表 -->
      <el-card shadow="hover" class="conversation-card">
        <template #header>
          <div class="card-header">
            <span>对话列表</span>
          </div>
        </template>
        <div class="conversation-list" @scroll="handleConversationListScroll">
          <template v-if="conversationList.length > 0 || conversationLoading">
            <div
              v-for="conversation in conversationList"
              :key="conversation.id"
              class="conversation-item"
              :class="{ active: selectedConversation?.id === conversation.id }"
              @click="selectConversation(conversation)"
            >
              <div class="conversation-icon">
                <el-icon><ChatDotRound /></el-icon>
              </div>
              <div class="conversation-info">
                <div class="conversation-title">
                  {{ conversation.name }}
                </div>
                <div class="conversation-meta">
                  <span>{{ new Date(conversation.updateTime).toLocaleString() }}</span>
                </div>
              </div>
            </div>
            <div v-if="conversationLoading" class="loading-more">
              <el-icon class="loading-icon">
                <Loading />
              </el-icon>
              <span>加载中...</span>
            </div>
          </template>
          <el-empty v-else-if="!conversationLoading" description="暂无对话数据" />
        </div>
      </el-card>

      <!-- 第三个卡片：对话内容 -->
      <el-card shadow="hover" class="message-card">
        <template #header>
          <div class="card-header">
            <span>对话标题: {{ selectedConversation?.name || '未选择对话' }}</span>
          </div>
        </template>
        <div class="message-list" @scroll="handleMessageListScroll">
          <template v-if="selectedConversation">
            <div
              v-for="message in messageList"
              :key="message.id"
              class="message-item"
              :class="{ 'user-message': message.role === 'user', 'assistant-message': message.role === 'assistant' }"
            >
              <div class="message-header">
                <span class="message-role">{{ message.role === 'user' ? '用户' : '助手' }}</span>
                <span class="message-time">{{ new Date(message.create_time).toLocaleString() }}</span>
              </div>
              <div class="message-content" v-html="renderMessageContent(message.content)" />
            </div>
            <el-empty v-if="messageList.length === 0 && !messageLoading" description="暂无消息数据" />
            <!-- 加载提示 -->
            <!-- <div v-if="messageHasMore" class="loading-more bottom-loading">
              <el-icon class="loading-icon" :class="{ 'is-loading': messageLoading }">
                <Loading />
              </el-icon>
              <span>{{ messageLoading ? '加载中...' : '向下滚动加载更多' }}</span>
            </div> -->
          </template>
          <el-empty v-else description="请先选择对话" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.search-wrapper {
  margin-bottom: 20px;
  :deep(.el-card__body) {
    padding-bottom: 2px;
  }
  
  :deep(.el-form) {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  :deep(.el-form-item) {
    margin-bottom: 0;
    margin-right: 0;
  }
  
  :deep(.el-form-item__label) {
    white-space: nowrap;
  }
}

.conversation-preview {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.preview-label {
  font-size: 11px;
  color: #999;
  margin-bottom: 2px;
  font-weight: 500;
}

.preview-content {
  color: #333;
  background-color: #f8f9fa;
  padding: 6px 8px;
  border-radius: 4px;
  border-left: 3px solid #409eff;
  line-height: 1.5;
  max-height: 60px;
  overflow: hidden;
}

.highlight {
  background-color: #ffeb3b;
  color: #333;
  padding: 1px 2px;
  border-radius: 2px;
  font-weight: bold;
}

.search-stats {
  margin-left: auto;
  
  .stats-text {
    color: #409eff;
    font-weight: 500;
    font-size: 14px;
  }
}

.conversation-cards-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 240px);
  min-height: 750px;
  overflow-x: auto; /* 添加水平滚动 */
  padding-bottom: 10px; /* 添加底部内边距，避免滚动条遮挡内容 */
}

.user-card {
  width: 25%;
  min-width: 250px; /* 设置最小宽度，避免卡片过小 */
  display: flex;
  flex-direction: column;
  flex-shrink: 0; /* 防止卡片被压缩 */
}

.conversation-card {
  width: 25%;
  min-width: 250px; /* 设置最小宽度，避免卡片过小 */
  display: flex;
  flex-direction: column;
  flex-shrink: 0; /* 防止卡片被压缩 */
}

.message-card {
  flex: 1;
  min-width: 300px; /* 设置最小宽度，避免卡片过小 */
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.user-list,
.conversation-list,
.message-list {
  overflow-y: auto;
  flex: 1;
  position: relative;
  padding: 0 4px;
  max-height: calc(100vh - 300px); /* 设置最大高度，确保内容可滚动 */

  &::-webkit-scrollbar {
    width: 6px;
    height: 6px; /* 添加水平滚动条高度 */
  }

  &::-webkit-scrollbar-thumb {
    background-color: var(--el-border-color-darker);
    border-radius: 3px;
  }

  &::-webkit-scrollbar-track {
    background-color: var(--el-fill-color-lighter);
    border-radius: 3px;
  }
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;

  .loading-icon {
    margin-right: 6px;
    animation: rotating 2s linear infinite;
  }

  &.top-loading {
    position: sticky;
    top: 0;
    background-color: rgba(255, 255, 255, 0.8);
    z-index: 1;
  }

  &.bottom-loading {
    position: sticky;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.8);
    z-index: 1;
  }
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.user-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-bottom: 8px;

  &:hover {
    background-color: var(--el-fill-color-light);
  }

  &.active {
    background-color: var(--el-color-primary-light-9);
  }

  .user-info {
    margin-left: 10px;

    .username {
      font-weight: bold;
    }

    .email {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
  }
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-bottom: 8px;

  &:hover {
    background-color: var(--el-fill-color-light);
  }

  &.active {
    background-color: var(--el-color-primary-light-9);
  }

  .conversation-icon {
    font-size: 20px;
    color: var(--el-color-primary);
  }

  .conversation-info {
    margin-left: 10px;
    flex: 1;

    .conversation-title {
      font-weight: bold;
      margin-bottom: 4px;
    }

    .conversation-meta {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
  }
}

.message-item {
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;

  &.user-message {
    background-color: var(--el-color-primary-light-9);
    margin-left: 20px;
  }

  &.assistant-message {
    background-color: var(--el-fill-color-light);
    margin-right: 20px;
  }

  .message-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;

    .message-role {
      font-weight: bold;
    }

    .message-time {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
  }

  .message-content {
    white-space: pre-wrap;
    word-break: break-word;
    .message-image {
      max-width: 100%;
      border-radius: 4px;
      margin: 8px 0;
    }
  }
}
</style>

<!-- 添加全局滚动条样式 -->
<style lang="scss">
/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-thumb {
  background-color: var(--el-border-color);
  border-radius: 4px;

  &:hover {
    background-color: var(--el-border-color-darker);
  }
}

::-webkit-scrollbar-track {
  background-color: var(--el-fill-color-lighter);
  border-radius: 4px;
}
</style>
