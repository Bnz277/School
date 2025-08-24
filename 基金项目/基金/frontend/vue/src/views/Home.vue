<template>
  <div class="home">
    <div class="hero-section">
      <div class="hero-content fade-in-up">
        <h1 class="hero-title">NYLG爬虫工具</h1>
        <p class="hero-subtitle">强大的多平台数据爬取工具</p>
        <p class="hero-description">
          支持百度搜索、B站视频、CSDN文章、自定义URL等多种数据源，
          提供JSON、CSV、TXT、Markdown等多种导出格式
        </p>
        <div class="hero-actions">
          <el-button 
            type="primary" 
            size="large" 
            @click="$router.push('/crawler')"
            class="start-btn"
          >
            <el-icon><Search /></el-icon>
            开始爬取
          </el-button>
          <el-button 
            size="large" 
            @click="$router.push('/docs')"
            class="docs-btn"
          >
            <el-icon><Document /></el-icon>
            查看文档
          </el-button>
        </div>
      </div>
    </div>

    <div class="features-section">
      <div class="container">
        <h2 class="section-title fade-in-up">核心功能</h2>
        <div class="features-grid">
          <div class="feature-card glass-card fade-in-scale" v-for="(feature, index) in features" :key="index">
            <div class="feature-icon">
              <el-icon :size="40"><component :is="feature.icon" /></el-icon>
            </div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="stats-section">
      <div class="container">
        <div class="stats-grid">
          <div class="stat-card glass-card fade-in-scale" v-for="(stat, index) in stats" :key="index">
            <div class="stat-number">{{ stat.number }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Search, Document, DataBoard, Download, Setting, Lock } from '@element-plus/icons-vue'

export default {
  name: 'Home',
  components: {
    Search,
    Document,
    DataBoard,
    Download,
    Setting,
    Lock
  },
  data() {
    return {
      features: [
        {
          icon: 'DataBoard',
          title: '多平台支持',
          description: '支持百度搜索、B站视频、CSDN文章等多个主流平台的数据爬取'
        },
        {
          icon: 'Download',
          title: '多格式导出',
          description: '提供JSON、CSV、TXT、Markdown等多种数据导出格式'
        },
        {
          icon: 'Setting',
          title: '智能识别',
          description: '自动识别网页内容类型，无需手动选择数据类型'
        },
        // {
        //   icon: 'Lock',
        //   title: '稳定可靠',
        //   description: '采用先进的反爬虫技术，确保数据爬取的稳定性和可靠性'
        // }
      ],
      stats: [
        { number: '3+n', label: '支持平台' },
        { number: '4', label: '导出格式' },
        { number: '95%', label: '成功率' },
        { number: '24/7', label: '在线服务' }
      ]
    }
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.hero-section {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  position: relative;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 20% 80%, rgba(100, 206, 229, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgb(239, 169, 237) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgb(255, 255, 255) 0%, transparent 50%);
  pointer-events: none;
}

.hero-content {
  max-width: 800px;
  padding: 0 20px;
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 4.2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #c299be 0%, #d4a4c8 30%, #e6a8d0 70%, #f8bbd9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1.2rem;
  letter-spacing: -0.02em;
  text-shadow: 0 5px 25px rgba(194, 153, 190, 0.4);
}

.hero-subtitle {
  font-size: 1.6rem;
  color: #8b6f7d;
  margin-bottom: 1.2rem;
  font-weight: 700;
  text-shadow: 0 3px 12px rgba(255, 255, 255, 0.9);
}

.hero-description {
  font-size: 1.3rem;
  color: #7a5f6a;
  margin-bottom: 2.5rem;
  line-height: 1.9;
  text-shadow: 0 2px 10px rgba(255, 255, 255, 0.7);
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.start-btn {
  background: linear-gradient(135deg, #f8bbd9 0%, #e6a8d0 50%, #d4a4c8 100%);
  border: 3px solid rgba(248, 187, 208, 0.6);
  padding: 22px 48px;
  font-size: 20px;
  font-weight: 800;
  border-radius: 50px;
  box-shadow: 0 15px 35px rgba(248, 187, 208, 0.4), 0 8px 20px rgba(230, 168, 208, 0.3);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  color: #6b4c57;
  text-shadow: 0 2px 4px rgba(255, 255, 255, 0.9);
}

.start-btn:hover {
  transform: translateY(-6px) scale(1.1);
  box-shadow: 0 25px 55px rgba(248, 187, 208, 0.5), 0 12px 30px rgba(230, 168, 208, 0.4);
  background: linear-gradient(135deg, #e6a8d0 0%, #d4a4c8 50%, #c299be 100%);
  border-color: rgba(248, 187, 208, 0.8);
  color: #5a3f4a;
}

.docs-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 16px 32px;
  font-size: 18px;
  font-weight: 600;
  border-radius: 16px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.docs-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-3px);
}

.features-section {
  padding: 80px 0;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 3rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: rgba(255, 250, 245, 0.95);
  backdrop-filter: blur(25px);
  border: 2px solid rgba(248, 187, 208, 0.4);
  border-radius: 24px;
  padding: 2.5rem;
  text-align: center;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 12px 30px rgba(248, 187, 208, 0.3), 0 6px 18px rgba(255, 209, 220, 0.2);
  cursor: pointer;
}

.feature-card:hover {
  transform: translateY(-10px) scale(1.06);
  box-shadow: 0 25px 50px rgba(248, 187, 208, 0.4), 0 12px 30px rgba(255, 209, 220, 0.3);
  border-color: rgba(248, 187, 208, 0.6);
  background: rgba(255, 250, 245, 1);
}

.feature-icon {
  font-size: 3.2rem;
  margin-bottom: 1.2rem;
  background: linear-gradient(135deg, #f8bbd9 0%, #e6a8d0 50%, #d4a4c8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 2px 4px rgba(248, 187, 217, 0.3));
}

.feature-card h3 {
  font-size: 1.6rem;
  font-weight: 800;
  color: #8b6f7d;
  margin-bottom: 1.2rem;
  text-shadow: 0 2px 10px rgba(255, 255, 255, 0.7);
}

.feature-card p {
  color: #7a5f6a;
  line-height: 1.7;
  font-size: 1.05rem;
  text-shadow: 0 1px 5px rgba(255, 255, 255, 0.6);
}

.stats-section {
  padding: 60px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
}

.stat-card {
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: scale(1.05);
}

.stat-number {
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(135deg, #99e571 0%, #2671c9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1.1rem;
  color: rgba(190, 127, 150, 0.6);
  font-weight: 500;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>