<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 顶部导航栏 -->
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo">
            <h1>NYLG爬虫工具</h1>
          </div>
          <div class="nav-menu">
            <router-link to="/" class="nav-link">首页</router-link>
            <router-link to="/crawler" class="nav-link">爬虫工具</router-link>
            <router-link to="/docs" class="nav-link">使用文档</router-link>
            <router-link to="/about" class="nav-link">关于</router-link>
          </div>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main class="app-main">
        <router-view />
      </el-main>

      <!-- 底部 -->
      <el-footer class="app-footer">
        <div class="footer-content">
          <p>&copy; 2025 NYLG爬虫工具</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #e58cdf 0%, #a8bde8 50%, #f093fb 100%);
  background-attachment: fixed;
}

.app-header {
  background: rgba(255, 250, 245, 0.98);
  backdrop-filter: blur(25px);
  border-bottom: 2px solid rgba(248, 187, 208, 0.4);
  padding: 0;
  box-shadow: 0 6px 25px rgba(248, 187, 208, 0.25);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
}

.logo h1 {
  background: linear-gradient(135deg, #c299be 0%, #d4a4c8 40%, #e6a8d0 80%, #f8bbd9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  font-size: 28px;
  font-weight: 900;
  text-shadow: 0 3px 10px rgb(230, 168, 208);
}

.nav-menu {
  display: flex;
  gap: 25px;
}

.nav-link {
  color: #8b6f7d;
  text-decoration: none;
  padding: 12px 20px;
  border-radius: 28px;
  border: 2px solid transparent;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 700;
  text-shadow: 0 1px 4px rgba(255, 255, 255, 0.9);
}

.nav-link:hover {
  color: #7a5f6a;
  background: rgba(248, 187, 208, 0.25);
  transform: translateY(-3px) scale(1.05);
  border-color: rgba(248, 187, 208, 0.4);
  box-shadow: 0 8px 20px rgba(248, 187, 208, 0.35);
}

.nav-link.router-link-active {
  color: #6b4c57;
  background: linear-gradient(135deg, #f8bbd9 0%, #e6a8d0 50%, #d4a4c8 100%);
  border-color: rgba(255, 255, 255, 0.6);
  box-shadow: 0 8px 25px rgba(248, 187, 208, 0.45);
  text-shadow: 0 1px 3px rgba(139, 90, 131, 0.3);
}

.app-main {
  padding: 40px 20px;
  min-height: calc(100vh - 120px);
}

.app-footer {
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.footer-content p {
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}
</style>