<template>
  <div class="home">
    <h1>JWT测试应用</h1>
    <p>这是一个用于测试JWT令牌过期功能的Vue应用</p>
    <div class="features">
      <h3>功能特性：</h3>
      <ul>
        <li>用户登录认证</li>
        <li>JWT令牌管理</li>
        <li>自动检测令牌过期</li>
        <li>过期后自动退出登录</li>
        <li>路由保护</li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
.home {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.features {
  text-align: left;
  margin-top: 30px;
}

.features ul {
  list-style-type: disc;
  margin-left: 20px;
}

.features li {
  margin: 10px 0;
}
</style>
