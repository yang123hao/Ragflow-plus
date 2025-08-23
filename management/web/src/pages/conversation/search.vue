<script lang="ts" setup>
import { ChatDotRound, Loading } from "@element-plus/icons-vue"
import { request } from "@/http/axios"

defineOptions({
  // 命名当前组件
  name: "ConversationManagement"
})

// 搜索数据
const searchData = reactive({
  conversationKeyword: "" // 对话内容搜索关键字
})

// #region 对话数据
// 定义对话数据类型
interface ConversationData {
  id: string // 修改为string类型
  content: string // 对话内容
  name?: string // 对话名称（可选）
  latestMessage?: string // 最新消息（可选）
  createTime?: string // 创建时间（可选）
  updateTime?: string // 更新时间（可选）
  tenantId?: string // 租户ID（可选）
  role?: string // 角色（可选）
}

const conversationList = ref<ConversationData[]>([])
const conversationLoading = ref(false)

// 对话列表滚动加载相关
const conversationHasMore = ref(true)
const conversationPage = ref(1)
const conversationPageSize = 20

// 当前选中的对话
const selectedConversation = ref<ConversationData | null>(null)

/**
 * 选择对话
 * @param conversation 对话数据
 */
function selectConversation(conversation: ConversationData) {
  selectedConversation.value = conversation
}

/**
 * 格式化对话内容，将换行符转换为HTML换行标签
 * @param content 对话内容
 * @returns 格式化后的HTML内容
 */
function formatContent(content: string | undefined): string {
  if (!content) return '无内容'
  
  // 添加调试日志
  console.log('原始内容:', content)
  console.log('内容类型:', typeof content)
  console.log('是否包含\\n:', content.includes('\\n'))
  console.log('是否包含换行符:', content.includes('\n'))
  
  // 处理两种可能的换行符格式
  let formatted = content
  
  // 先处理真正的换行符 \n
  formatted = formatted.replace(/\n/g, '<br>')
  
  // 再处理转义的换行符 \\n
  formatted = formatted.replace(/\\n/g, '<br>')
  
  console.log('格式化后:', formatted)
  
  return formatted
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
  
  // 执行全局搜索，不需要选择用户
  searchAllConversations(keyword, false)
}

/**
 * 清空搜索
 */
function clearSearch() {
  searchData.conversationKeyword = ""
  
  // 清空对话列表，不自动搜索
  conversationPage.value = 1
  conversationHasMore.value = true
  conversationList.value = []
  
  // 显示清空成功消息
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
    url: `/api/v1/conversation/search2`,
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

// 初始加载数据
onMounted(() => {
  // 页面加载时不自动搜索，等待用户手动搜索
  //console.log("页面加载完成，等待用户搜索")
  searchConversations()
})
</script>

<template>
  <div class="app-container">
    <!-- 顶部搜索栏 -->
    <el-card shadow="never" class="global-search-wrapper">
      <el-form ref="searchFormRef" :inline="true" :model="searchData">
        <el-form-item prop="conversationKeyword" label="全局对话搜索:">
          <el-input 
            v-model="searchData.conversationKeyword" 
            placeholder="请输入搜索关键字" 
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

    <!-- 多级卡片区域 -->
    <div class="conversation-cards-container">
      <!-- 对话列表卡片 -->
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
                <span class="message-role" :style="{ color: conversation.role === 'user' ? '#67c23a' : '#606266' }">
                  {{ conversation.role === 'user' ? '用户' : '助手' }}
                </span>
                  <div class="conversation-title" v-html="formatContent(conversation.content)">
                  </div>
                <!-- 调试信息 -->
                <div class="debug-info" style="font-size: 12px; color: #999; margin-top: 4px;">
                  ID: {{ conversation.id }} | 
                  名称: {{ conversation.name || '无名称' }} 
                  创建时间: {{ conversation.createTime || '' }} | 
                  更新时间: {{ conversation.updateTime || '' }} | 
                  内容长度: {{ (conversation.content || '').length }}
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
          <el-empty v-else-if="!conversationLoading && conversationList.length === 0" description="请输入搜索关键字并点击搜索按钮" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.global-search-wrapper {
  margin-bottom: 20px;
  :deep(.el-card__body) {
    padding: 16px 20px;
  }
  
  :deep(.el-form) {
    display: flex;
    align-items: center;
    gap: 15px;
    justify-content: flex-start;
  }
  
  :deep(.el-form-item) {
    margin-bottom: 0;
    margin-right: 0;
  }
  
  :deep(.el-form-item__label) {
    white-space: nowrap;
    font-weight: 500;
    color: var(--el-text-color-primary);
  }
  
  :deep(.el-input) {
    width: 300px;
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

.conversation-card {
  width: 100%;
  min-width: 600px; /* 设置最小宽度，让卡片更宽 */
  display: flex;
  flex-direction: column;
  flex-shrink: 0; /* 防止卡片被压缩 */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.conversation-list {
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
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.conversation-item {
  display: flex;
  align-items: flex-start;
  padding: 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-bottom: 12px;
  border: 1px solid var(--el-border-color-light);

  &:hover {
    background-color: var(--el-fill-color-light);
    border-color: var(--el-color-primary-light-7);
  }

  &.active {
    background-color: var(--el-color-primary-light-9);
    border-color: var(--el-color-primary);
  }

  .conversation-icon {
    font-size: 24px;
    color: var(--el-color-primary);
    margin-right: 12px;
    flex-shrink: 0;
  }

  .conversation-info {
    flex: 1;
    min-width: 0;

    .conversation-title {
      font-weight: bold;
      margin-bottom: 8px;
      font-size: 16px;
      color: var(--el-text-color-primary);
    }

    .conversation-meta {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: var(--el-text-color-secondary);
      margin-bottom: 8px;
    }

    .conversation-preview {
      font-size: 14px;
      color: var(--el-text-color-regular);
      line-height: 1.5;
      background-color: var(--el-fill-color-lighter);
      padding: 8px 12px;
      border-radius: 6px;
      border-left: 3px solid var(--el-color-primary);
      max-height: 80px;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
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
