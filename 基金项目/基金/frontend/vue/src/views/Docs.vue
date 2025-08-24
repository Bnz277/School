<template>
  <div class="docs">
    <div class="container">
      <div class="docs-header fade-in-up">
        <h1>使用文档</h1>
        <p>详细的使用指南和API文档</p>
      </div>

      <div class="docs-content">
        <!-- 侧边栏导航 -->
        <div class="docs-sidebar glass-card">
          <el-menu 
            :default-active="activeSection"
            @select="scrollToSection"
            class="docs-menu"
          >
            <el-menu-item index="getting-started">
              <el-icon><Document /></el-icon>
              快速开始
            </el-menu-item>
            <el-menu-item index="spider-types">
              <el-icon><DataBoard /></el-icon>
              爬虫类型
            </el-menu-item>
            <el-menu-item index="export-formats">
              <el-icon><Download /></el-icon>
              导出格式
            </el-menu-item>
<!--            <el-menu-item index="api-reference">-->
<!--              <el-icon><Setting /></el-icon>-->
<!--              API参考-->
<!--            </el-menu-item>-->
<!--            <el-menu-item index="deployment">-->
<!--              <el-icon><Monitor /></el-icon>-->
<!--              部署指南-->
<!--            </el-menu-item>-->
            <el-menu-item index="faq">
              <el-icon><QuestionFilled /></el-icon>
              常见问题
            </el-menu-item>
          </el-menu>
        </div>

        <!-- 主要内容 -->
        <div class="docs-main">
          <!-- 快速开始 -->
          <section id="getting-started" class="docs-section glass-card fade-in-scale">
            <h2>快速开始</h2>
            <div class="section-content">
              <h3>1. 选择爬虫类型</h3>
              <p>在爬虫工具页面选择您需要的爬虫类型：</p>
              <ul>
                <li><strong>百度搜索</strong>：爬取百度搜索结果</li>
                <li><strong>B站视频</strong>：爬取B站视频信息</li>
                <li><strong>CSDN文章</strong>：爬取CSDN技术文章</li>
                <li><strong>网页爬取</strong>：爬取指定URL的内容</li>
              </ul>
              
              <h3>2. 设置参数</h3>
              <p>根据选择的爬虫类型，填写相应的参数：</p>
              <ul>
                <li>搜索关键词（百度、B站、CSDN）</li>
                <li>目标URL（网页爬取）</li>
                <li>结果数量限制</li>
              </ul>
              
              <h3>3. 执行爬取</h3>
              <p>点击"开始爬取"按钮，系统将自动执行爬取任务并展示结果。</p>
              
              <h3>4. 导出数据</h3>
              <p>爬取完成后，可以选择多种格式导出数据：JSON、CSV、TXT、Markdown。</p>
            </div>
          </section>

          <!-- 爬虫类型 -->
          <section id="spider-types" class="docs-section glass-card fade-in-scale">
            <h2>爬虫类型详解</h2>
            <div class="section-content">
              <div class="spider-type">
                <h3>百度搜索爬虫</h3>
                <p><strong>功能</strong>：爬取百度搜索结果，支持网页搜索和图片搜索</p>
                <p><strong>参数</strong>：</p>
                <ul>
                  <li>搜索关键词：要搜索的内容</li>
                  <li>搜索类型：网页搜索或图片搜索</li>
                  <li>结果数量：1-50条（推荐30条以内，超过30条准确率可能下降）</li>
                </ul>
                <p><strong>返回数据</strong>：标题、链接、描述、图片URL等</p>
              </div>
              
              <div class="spider-type">
                <h3>B站视频爬虫</h3>
                <p><strong>功能</strong>：爬取B站视频信息</p>
                <p><strong>参数</strong>：</p>
                <ul>
                  <li>搜索关键词：视频相关关键词</li>
                  <li>结果数量：1-50条（推荐30条以内，超过30条准确率可能下降）</li>
                </ul>
                <p><strong>返回数据</strong>：视频标题、作者、播放量、时长、链接等</p>
              </div>
              
              <div class="spider-type">
                <h3>CSDN文章爬虫</h3>
                <p><strong>功能</strong>：爬取CSDN技术文章</p>
                <p><strong>参数</strong>：</p>
                <ul>
                  <li>搜索关键词：技术相关关键词</li>
                  <li>结果数量：1-50条（推荐30条以内，超过30条准确率可能下降）</li>
                </ul>
                <p><strong>返回数据</strong>：文章标题、作者、发布时间、阅读量、链接等</p>
              </div>
              
              <div class="spider-type">
                <h3>网页爬取</h3>
                <p><strong>功能</strong>：爬取指定URL的网页内容，智能识别数据类型</p>
                <p><strong>参数</strong>：</p>
                <ul>
                  <li>目标URL：要爬取的网页地址</li>
                </ul>
                <p><strong>返回数据</strong>：根据网页内容自动识别和提取相关信息</p>
              </div>
            </div>
          </section>

          <!-- 导出格式 -->
          <section id="export-formats" class="docs-section glass-card fade-in-scale">
            <h2>导出格式说明</h2>
            <div class="section-content">
              <div class="export-format">
                <h3>JSON格式</h3>
                <p>标准的JSON格式，适合程序处理和API调用</p>
                <el-code-block language="json">
[
  {
    "title": "示例标题",
    "url": "https://example.com",
    "description": "示例描述"
  }
]
                </el-code-block>
              </div>
              
              <div class="export-format">
                <h3>CSV格式</h3>
                <p>逗号分隔值格式，适合Excel等表格软件打开</p>
                <el-code-block language="csv">
title,url,description
示例标题,https://example.com,示例描述
                </el-code-block>
              </div>
              
              <div class="export-format">
                <h3>TXT格式</h3>
                <p>纯文本格式，便于阅读和编辑</p>
                <el-code-block language="text">
=== 第 1 条数据 ===
标题: 示例标题
链接: https://example.com
描述: 示例描述
                </el-code-block>
              </div>
              
              <div class="export-format">
                <h3>Markdown格式</h3>
                <p>Markdown表格格式，适合文档编写</p>
                <el-code-block language="markdown">
| 标题 | 链接 | 描述 |
| --- | --- | --- |
| 示例标题 | https://example.com | 示例描述 |
                </el-code-block>
              </div>
            </div>
          </section>

<!--          &lt;!&ndash; API参考 &ndash;&gt;-->
<!--          <section id="api-reference" class="docs-section glass-card fade-in-scale">-->
<!--            <h2>API参考</h2>-->
<!--            <div class="section-content">-->
<!--              <h3>爬取接口</h3>-->
<!--              <p><strong>URL</strong>：<code>POST /api/crawl</code></p>-->
<!--              <p><strong>请求参数</strong>：</p>-->
<!--              <el-code-block language="json">-->
<!--{-->
<!--  "spider_type": "baidu|bilibili|csdn|url",-->
<!--  "task_type": "search|url",-->
<!--  "keyword": "搜索关键词",-->
<!--  "url": "目标URL",-->
<!--  "count": 10,-->
<!--  "search_type": "web|image"-->
<!--}-->
<!--              </el-code-block>-->
<!--              -->
<!--              <p><strong>响应格式</strong>：</p>-->
<!--              <el-code-block language="json">-->
<!--{-->
<!--  "success": true,-->
<!--  "message": "爬取成功",-->
<!--  "task_id": "任务ID",-->
<!--  "results": [-->
<!--    {-->
<!--      "title": "标题",-->
<!--      "url": "链接",-->
<!--      "description": "描述"-->
<!--    }-->
<!--  ]-->
<!--}-->
<!--              </el-code-block>-->
<!--            </div>-->
<!--          </section>-->

<!--          &lt;!&ndash; 部署指南 &ndash;&gt;-->
<!--          <section id="deployment" class="docs-section glass-card fade-in-scale">-->
<!--            <h2>部署指南</h2>-->
<!--            <div class="section-content">-->
<!--              <h3>宝塔面板部署</h3>-->
<!--              -->
<!--              <h4>1. 环境准备</h4>-->
<!--              <ul>-->
<!--                <li>Python 3.9+</li>-->
<!--                <li>Node.js 16+</li>-->
<!--                <li>宝塔面板 7.0+</li>-->
<!--              </ul>-->
<!--              -->
<!--              <h4>2. 后端部署</h4>-->
<!--              <ol>-->
<!--                <li>上传项目文件到服务器</li>-->
<!--                <li>安装Python依赖：<code>pip install -r requirements.txt</code></li>-->
<!--                <li>在宝塔面板中创建Python项目</li>-->
<!--                <li>设置启动文件为 <code>app.py</code></li>-->
<!--                <li>配置端口（默认5000）</li>-->
<!--              </ol>-->
<!--              -->
<!--              <h4>3. 前端部署</h4>-->
<!--              <ol>-->
<!--                <li>进入Vue项目目录：<code>cd frontend/vue</code></li>-->
<!--                <li>安装依赖：<code>npm install</code></li>-->
<!--                <li>构建项目：<code>npm run build</code></li>-->
<!--                <li>将dist目录内容上传到网站根目录</li>-->
<!--                <li>配置Nginx反向代理到后端API</li>-->
<!--              </ol>-->
<!--              -->
<!--              <h4>4. Nginx配置示例</h4>-->
<!--              <el-code-block language="nginx">-->
<!--server {-->
<!--    listen 80;-->
<!--    server_name your-domain.com;-->
<!--    -->
<!--    location / {-->
<!--        root /www/wwwroot/your-site/dist;-->
<!--        try_files $uri $uri/ /index.html;-->
<!--    }-->
<!--    -->
<!--    location /api {-->
<!--        proxy_pass http://127.0.0.1:5000;-->
<!--        proxy_set_header Host $host;-->
<!--        proxy_set_header X-Real-IP $remote_addr;-->
<!--    }-->
<!--}-->
<!--              </el-code-block>-->
<!--            </div>-->
<!--          </section>-->

          <!-- 常见问题 -->
          <section id="faq" class="docs-section glass-card fade-in-scale">
            <h2>常见问题</h2>
            <div class="section-content">
              <div class="faq-item">
                <h3>Q: 爬取失败怎么办？</h3>
                <p>A: 请检查网络连接、参数设置是否正确，某些网站可能有反爬虫机制。</p>
              </div>
              
              <div class="faq-item">
                <h3>Q: 支持哪些网站？</h3>
                <p>A: 目前支持百度、B站、CSDN和自定义URL爬取，后续会增加更多平台。</p>
              </div>
              
              <div class="faq-item">
                <h3>Q: 数据量有限制吗？</h3>
                <p>A: 单次爬取最多50条数据，推荐30条以内以保证准确率，如需更多数据请分批爬取。</p>
              </div>
              
              <div class="faq-item">
                <h3>Q: 如何提高爬取成功率？</h3>
                <p>A: 使用准确的关键词，且遵循目标网站 Robots 协议，避免在单个平台短时间内多次爬取大量内容。</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Document, DataBoard, Download, Setting, Monitor, QuestionFilled } from '@element-plus/icons-vue'

export default {
  name: 'Docs',
  components: {
    Document,
    DataBoard,
    Download,
    Setting,
    Monitor,
    QuestionFilled
  },
  data() {
    return {
      activeSection: 'getting-started'
    }
  },
  mounted() {
    this.handleScroll()
    window.addEventListener('scroll', this.handleScroll)
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.handleScroll)
  },
  methods: {
    scrollToSection(index) {
      const element = document.getElementById(index)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' })
      }
    },
    
    handleScroll() {
      const sections = ['getting-started', 'spider-types', 'export-formats', 'api-reference', 'deployment', 'faq']
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop
      
      for (let i = sections.length - 1; i >= 0; i--) {
        const element = document.getElementById(sections[i])
        if (element && element.offsetTop <= scrollTop + 100) {
          this.activeSection = sections[i]
          break
        }
      }
    }
  }
}
</script>

<style scoped>
.docs {
  min-height: 100vh;
  padding: 20px 0;
  background: linear-gradient(135deg, #fff5f0 0%, #ffe4e1 25%, #ffd1dc 50%, #f8bbd9 75%, #e6a8d0 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.docs-header {
  text-align: center;
  margin-bottom: 3rem;
}

.docs-header h1 {
  font-size: 3.2rem;
  font-weight: 900;
  background: linear-gradient(135deg, #c299be 0%, #d4a4c8 30%, #e6a8d0 70%, #f8bbd9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
  text-shadow: 0 5px 25px rgba(194, 153, 190, 0.4);
}

.docs-header p {
  font-size: 1.2rem;
  color: #6b4c6b;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6);
}

.docs-content {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 2rem;
  align-items: start;
}

.docs-sidebar {
  position: sticky;
  top: 20px;
  padding: 2rem;
  background: rgba(255, 250, 245, 0.95);
  backdrop-filter: blur(25px);
  border: 2px solid rgba(248, 187, 208, 0.4);
  border-radius: 24px;
  box-shadow: 0 15px 35px rgba(248, 187, 208, 0.25);
}

.docs-menu {
  background: transparent;
  border: none;
}

.docs-main {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.docs-section {
  padding: 2.5rem;
  background: rgba(255, 250, 245, 0.95);
  backdrop-filter: blur(25px);
  border: 2px solid rgba(248, 187, 208, 0.4);
  border-radius: 25px;
  box-shadow: 0 15px 35px rgba(248, 187, 208, 0.25);
}

.docs-section h2 {
  color: #8b5a83;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  border-bottom: 3px solid rgba(255, 182, 193, 0.4);
  padding-bottom: 0.5rem;
  text-shadow: 0 2px 8px rgba(139, 90, 131, 0.3);
}

.docs-section h3 {
  color: #8b5a83;
  font-size: 1.3rem;
  font-weight: 600;
  margin: 1.5rem 0 1rem 0;
  text-shadow: 0 1px 3px rgba(255, 255, 255, 0.8);
}

.docs-section h4 {
  color: #6b4c6b;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 1rem 0 0.5rem 0;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6);
}

.docs-section p {
  color: #6b4c6b;
  line-height: 1.6;
  margin-bottom: 1rem;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6);
}

.docs-section ul,
.docs-section ol {
  color: #6b4c6b;
  margin-bottom: 1rem;
  padding-left: 1.5rem;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6);
}

.docs-section li {
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.docs-section code {
  background: rgba(139, 90, 131, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  color: #8b5a83;
  border: 1px solid rgba(255, 182, 193, 0.3);
}

.spider-type,
.export-format,
.faq-item {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 15px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border-left: 4px solid #8b5a83;
  box-shadow: 0 8px 20px rgba(255, 182, 193, 0.2);
}

.section-content {
  animation: fadeInUp 0.6s ease-out;
}

/* Element Plus 样式覆盖 */
:deep(.el-menu-item) {
  color: #6b4c6b !important;
  border-radius: 12px;
  margin-bottom: 8px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6);
}

:deep(.el-menu-item:hover) {
  background: rgba(248, 187, 208, 0.25) !important;
  color: #8b6f7d !important;
  transform: translateX(8px) scale(1.02);
  box-shadow: 0 5px 15px rgba(248, 187, 208, 0.3);
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #f8bbd9 0%, #e6a8d0 50%, #d4a4c8 100%) !important;
  color: #ffffff !important;
  border-right: 4px solid #8b5a83;
  box-shadow: 0 8px 20px rgba(248, 187, 208, 0.4);
  text-shadow: 0 1px 3px rgba(139, 90, 131, 0.3);
}

:deep(.el-code-block) {
  background: rgba(139, 90, 131, 0.1) !important;
  border: 2px solid rgba(255, 182, 193, 0.3);
  border-radius: 12px;
  margin: 1rem 0;
  box-shadow: 0 8px 20px rgba(255, 182, 193, 0.2);
}

@media (max-width: 768px) {
  .docs-content {
    grid-template-columns: 1fr;
  }
  
  .docs-sidebar {
    position: static;
    order: 2;
  }
  
  .docs-main {
    order: 1;
  }
  
  .docs-header h1 {
    font-size: 2rem;
  }
}
</style>