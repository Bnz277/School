<template>
  <div class="about">
    <div class="container">
      <!-- 页面标题 -->
      <div class="about-header fade-in-up">
        <h1>关于我们</h1>
        <p>了解我们</p>
      </div>

      <!-- 项目介绍 -->
      <div class="about-content">
        <div class="project-intro glass-card fade-in-scale">
          <div class="intro-icon">
            <el-icon size="60"><DataBoard /></el-icon>
          </div>
          <h2>项目简介</h2>
          <p>
            这是一个基于Python Flask和Vue.js开发的智能网络爬虫平台。
            我们致力于为用户提供简单易用、功能强大的数据采集工具，
            支持多平台数据爬取和多格式数据导出，
            方便用户更加便捷的查询所需资料。
          </p>
          <div class="project-stats">
            <div class="stat-item">
              <div class="stat-number">3+n</div>
              <div class="stat-label">支持平台</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">4</div>
              <div class="stat-label">导出格式</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">95%</div>
              <div class="stat-label">成功率</div>
            </div>
          </div>
        </div>

        <!-- 技术栈 -->
        <div class="tech-stack glass-card fade-in-scale">
          <h2>技术栈</h2>
          <div class="tech-grid">
            <div class="tech-category">
              <h3>后端技术</h3>
              <div class="tech-items">
                <div class="tech-item">
                  <el-icon><Monitor /></el-icon>
                  <span>Python 3.9+</span>
                </div>
                <div class="tech-item">
                  <el-icon><Setting /></el-icon>
                  <span>Flask</span>
                </div>
                <div class="tech-item">
                  <el-icon><DataBoard /></el-icon>
                  <span>BeautifulSoup</span>
                </div>
                <div class="tech-item">
                  <el-icon><Connection /></el-icon>
                  <span>Requests</span>
                </div>
              </div>
            </div>
            
            <div class="tech-category">
              <h3>前端技术</h3>
              <div class="tech-items">
                <div class="tech-item">
                  <el-icon><Monitor /></el-icon>
                  <span>Vue.js 3</span>
                </div>
                <div class="tech-item">
                  <el-icon><Setting /></el-icon>
                  <span>Element Plus</span>
                </div>
                <div class="tech-item">
                  <el-icon><DataBoard /></el-icon>
                  <span>Vite</span>
                </div>
                <div class="tech-item">
                  <el-icon><Connection /></el-icon>
                  <span>Axios</span>
                </div>
              </div>
            </div>
            
            <div class="tech-category">
              <h3>部署运维</h3>
              <div class="tech-items">
                <div class="tech-item">
                  <el-icon><Monitor /></el-icon>
                  <span>宝塔面板</span>
                </div>
                <div class="tech-item">
                  <el-icon><Setting /></el-icon>
                  <span>Nginx</span>
                </div>
                <div class="tech-item">
                  <el-icon><DataBoard /></el-icon>
                  <span>PM2</span>
                </div>
                <div class="tech-item">
                  <el-icon><Connection /></el-icon>
                  <span>SSL证书</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 功能特性 -->
        <div class="features glass-card fade-in-scale">
          <h2>核心特性</h2>
          <div class="features-grid">
            <div class="feature-item">
              <div class="feature-icon">
                <el-icon size="40"><DataBoard /></el-icon>
              </div>
              <h3>多平台支持</h3>
              <p>支持百度、B站、CSDN等主流平台的数据爬取，满足不同场景需求。</p>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon">
                <el-icon size="40"><Download /></el-icon>
              </div>
              <h3>多格式导出</h3>
              <p>支持JSON、CSV、TXT、Markdown等多种格式导出，便于后续处理。</p>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon">
                <el-icon size="40"><Setting /></el-icon>
              </div>
              <h3>智能识别</h3>
              <p>自动识别网页结构和数据类型，提供最优的爬取策略。</p>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon">
                <el-icon size="40"><Monitor /></el-icon>
              </div>
              <h3>实时监控</h3>
              <p>显示爬取结果与状态，提供详细的执行日志。</p>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon">
                <el-icon size="40"><Lock /></el-icon>
              </div>
              <h3>稳定可靠</h3>
              <p>采用多重错误处理机制，确保爬取任务的稳定执行。</p>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon">
                <el-icon size="40"><User /></el-icon>
              </div>
              <h3>易于使用</h3>
              <p>简洁直观的用户界面，无需编程基础即可轻松上手。</p>
            </div>
          </div>
        </div>

<!--        &lt;!&ndash; 开发团队 &ndash;&gt;-->
<!--        <div class="team glass-card fade-in-scale">-->
<!--          <h2>开发团队</h2>-->
<!--          <div class="team-content">-->
<!--            <div class="team-intro">-->
<!--              <p>-->
<!--                我们是一支专注于数据采集和处理技术的开发团队，-->
<!--                拥有丰富的Python开发和前端技术经验。-->
<!--                我们致力于为用户提供高质量的数据采集解决方案。-->
<!--              </p>-->
<!--            </div>-->
<!--            -->
<!--            <div class="team-values">-->
<!--              <div class="value-item">-->
<!--                <el-icon size="30"><Star /></el-icon>-->
<!--                <h4>创新驱动</h4>-->
<!--                <p>持续探索新技术，提供更好的用户体验</p>-->
<!--              </div>-->
<!--              -->
<!--              <div class="value-item">-->
<!--                <el-icon size="30"><Trophy /></el-icon>-->
<!--                <h4>质量至上</h4>-->
<!--                <p>严格的代码审查和测试，确保产品质量</p>-->
<!--              </div>-->
<!--              -->
<!--              <div class="value-item">-->
<!--                <el-icon size="30"><ChatDotRound /></el-icon>-->
<!--                <h4>用户第一</h4>-->
<!--                <p>倾听用户反馈，持续优化产品功能</p>-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--        </div>-->

        <!-- 联系方式 -->
        <div class="contact glass-card fade-in-scale">
          <h2>联系我们</h2>
          <div class="contact-content">
            <div class="contact-info">
              <div class="contact-item">
                <el-icon size="24"><Message /></el-icon>
                <div class="contact-details">
                  <h4>邮箱</h4>
                  <p>2773434682@qq.com</p>
                </div>
              </div>
              
              <div class="contact-item">
                <el-icon size="24"><Link /></el-icon>
                <div class="contact-details">
                  <h4>GitHub</h4>
                  <p>github.com/LuvGaze</p>
                </div>
              </div>
              
              <div class="contact-item">
                <el-icon size="24"><Document /></el-icon>
                <div class="contact-details">
                  <h4>文档</h4>
                  <p>查看详细的API文档和使用指南</p>
                </div>
              </div>
            </div>
            
            <div class="contact-form">
              <h3>意见反馈</h3>
              <el-form :model="feedbackForm" label-width="80px">
                <el-form-item label="姓名">
                  <el-input v-model="feedbackForm.name" placeholder="请输入您的姓名"></el-input>
                </el-form-item>
                <el-form-item label="邮箱">
                  <el-input v-model="feedbackForm.email" placeholder="请输入您的邮箱"></el-input>
                </el-form-item>
                <el-form-item label="反馈">
                  <el-input 
                    v-model="feedbackForm.message" 
                    type="textarea" 
                    :rows="4"
                    placeholder="请输入您的意见或建议"
                  ></el-input>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="submitFeedback">提交反馈</el-button>
                </el-form-item>
              </el-form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { 
  DataBoard, Monitor, Setting, Connection, Download, Lock, User,
  Star, Trophy, ChatDotRound, Message, Link, Document
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'About',
  components: {
    DataBoard, Monitor, Setting, Connection, Download, Lock, User,
    Star, Trophy, ChatDotRound, Message, Link, Document
  },
  data() {
    return {
      feedbackForm: {
        name: '',
        email: '',
        message: ''
      }
    }
  },
  methods: {
    submitFeedback() {
      if (!this.feedbackForm.name || !this.feedbackForm.email || !this.feedbackForm.message) {
        ElMessage.warning('请填写完整信息')
        return
      }
      
      // 这里可以添加提交反馈的API调用
      ElMessage.success('感谢您的反馈，我们会认真考虑您的建议！')
      
      // 重置表单
      this.feedbackForm = {
        name: '',
        email: '',
        message: ''
      }
    }
  }
}
</script>

<style scoped>
.about {
  min-height: 100vh;
  padding: 20px 0;
  background: linear-gradient(135deg, #fff5f0 0%, #ffe4e1 25%, #ffd1dc 50%, #f8bbd9 75%, #e6a8d0 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.about-header {
  text-align: center;
  margin-bottom: 3rem;
}

.about-header h1 {
  font-size: 3.2rem;
  font-weight: 900;
  background: linear-gradient(135deg, #c299be 0%, #d4a4c8 30%, #e6a8d0 70%, #f8bbd9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
  text-shadow: 0 5px 25px rgba(194, 153, 190, 0.4);
}

.about-header p {
  font-size: 1.2rem;
  color: #6b4c6b;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6);
}

.about-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.glass-card {
  padding: 2.5rem;
  background: rgba(255, 250, 245, 0.95);
  backdrop-filter: blur(25px);
  border: 2px solid rgba(248, 187, 208, 0.4);
  border-radius: 25px;
  box-shadow: 0 15px 35px rgba(248, 187, 208, 0.25), 0 8px 20px rgba(248, 187, 208, 0.2);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 25px 50px rgba(248, 187, 208, 0.35), 0 15px 30px rgba(248, 187, 208, 0.3);
  background: rgba(255, 250, 245, 0.98);
}

.glass-card h2 {
  color: #8b5a83;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  text-align: center;
  text-shadow: 0 1px 3px rgba(255, 255, 255, 0.8);
}

/* 项目介绍 */
.project-intro {
  text-align: center;
}

.intro-icon {
  background: linear-gradient(135deg, #f8bbd9 0%, #e6a8d0 50%, #d4a4c8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
  filter: drop-shadow(0 2px 4px rgba(248, 187, 217, 0.3));
}

.project-intro p {
  color: #6b4c6b;
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 2rem;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6);
}

.project-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #f8bbd9 0%, #e6a8d0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #6b4c6b;
  font-size: 1rem;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6);
}

/* 技术栈 */
.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.tech-category h3 {
  color: #8b5a83;
  font-size: 1.3rem;
  margin-bottom: 1rem;
  text-align: center;
  text-shadow: 0 1px 3px rgba(255, 255, 255, 0.8);
}

.tech-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
}

.tech-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(255, 182, 193, 0.2);
}

.tech-item:hover {
  background: rgba(255, 255, 255, 0.95);
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(255, 182, 193, 0.3);
}

.tech-item .el-icon {
  background: linear-gradient(135deg, #f8bbd9 0%, #e6a8d0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.tech-item span {
  color: #6b4c6b;
  font-size: 0.9rem;
  text-align: center;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6);
}

/* 功能特性 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-item {
  text-align: center;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 8px 20px rgba(255, 182, 193, 0.2);
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.95);
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(255, 182, 193, 0.3);
}

.feature-icon {
  background: linear-gradient(135deg, #f8bbd9 0%, #e6a8d0 50%, #d4a4c8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
  filter: drop-shadow(0 2px 4px rgba(248, 187, 217, 0.3));
}

.feature-item h3 {
  color: #8b5a83;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
  text-shadow: 0 1px 3px rgba(255, 255, 255, 0.8);
}

.feature-item p {
  color: #6b4c6b;
  line-height: 1.5;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6);
}

/* 开发团队 */
.team-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  align-items: start;
}

.team-intro p {
  color: #6b4c6b;
  font-size: 1.1rem;
  line-height: 1.6;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6);
}

.team-values {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.value-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(255, 182, 193, 0.2);
}

.value-item .el-icon {
  background: linear-gradient(135deg, #f8bbd9 0%, #e6a8d0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-top: 0.2rem;
}

.value-item h4 {
  color: #8b5a83;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  text-shadow: 0 1px 3px rgba(255, 255, 255, 0.8);
}

.value-item p {
  color: #6b4c6b;
  font-size: 0.9rem;
  line-height: 1.4;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6);
}

/* 联系方式 */
.contact-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(255, 182, 193, 0.2);
}

.contact-item .el-icon {
  background: linear-gradient(135deg, #f8bbd9 0%, #e6a8d0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.contact-details h4 {
  color: #8b5a83;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.3rem;
  text-shadow: 0 1px 3px rgba(255, 255, 255, 0.8);
}

.contact-details p {
  color: #6b4c6b;
  font-size: 0.9rem;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6);
}

.contact-form h3 {
  color: #8b5a83;
  font-size: 1.3rem;
  margin-bottom: 1.5rem;
  text-shadow: 0 1px 3px rgba(255, 255, 255, 0.8);
}

/* Element Plus 样式覆盖 */
:deep(.el-form-item__label) {
  color: #8b5a83 !important;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8) !important;
}

:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.9) !important;
  border: 1px solid rgba(255, 182, 193, 0.3) !important;
  border-radius: 8px !important;
  box-shadow: 0 2px 8px rgba(255, 182, 193, 0.1) !important;
}

:deep(.el-input__inner) {
  color: #6b4c6b !important;
  background: transparent !important;
}

:deep(.el-input__inner::placeholder) {
  color: rgba(107, 76, 107, 0.6) !important;
}

:deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.9) !important;
  border: 1px solid rgba(255, 182, 193, 0.3) !important;
  border-radius: 8px !important;
  color: #6b4c6b !important;
  box-shadow: 0 2px 8px rgba(255, 182, 193, 0.1) !important;
}

:deep(.el-textarea__inner::placeholder) {
  color: rgba(107, 76, 107, 0.6) !important;
}

@media (max-width: 768px) {
  .about-header h1 {
    font-size: 2rem;
  }
  
  .tech-grid,
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .team-content,
  .contact-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .project-stats {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  }
}
</style>