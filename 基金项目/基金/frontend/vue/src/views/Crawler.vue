<!--
  网络信息爬取系统主界面组件
  功能：
  1. 支持多平台爬虫（百度、B站、CSDN、自定义URL）
  2. 实时显示爬取进度和结果
  3. 支持多格式导出（JSON、CSV、Excel、Markdown）
  4. B站视频下载功能
  5. 图片预览和智能提示
  
  v2.0 功能改进：
  - 成功率更新机制：改为爬取完成后手动更新，提升性能
  - URL显示优化：长URL自动省略，防止界面溢出
  - 结果默认收起：所有结果默认收起状态，提升页面加载速度
  - 智能排序：B站按播放量、CSDN按浏览量降序排列
  - 数量限制：设置最低爬取数量为1，防止空值输入
  - 按钮美化：导出按钮和展开/收起按钮采用渐变色设计
  - 代码注释：完善所有函数和组件的文档说明
  
  v2.1 优化调整：
  - 警告阈值优化：将准确率警告从20调整为30（适配50最大值）
  - 分页优化：每页显示数量从10调整为15，提升浏览效率
  
  v2.2 功能增强：
  - 关键词显示：在结果统计界面添加当前搜索关键词显示
  - 智能清空：切换爬虫类型时自动清空上次的爬取结果
  - URL展开：自定义URL爬取结果默认为展开状态，便于查看详情
  - B站下载：在B站爬取结果中添加直接下载按钮，支持一键下载视频
-->
<template>
  <div class="crawler-container">
    <!-- 页面头部 -->
    <div class="crawler-header">
      <h1>🕷️ 网络信息爬取系统</h1>
      <p class="subtitle">支持多平台数据采集与智能分析</p>
    </div>

    <div class="crawler-content">
      <!-- 爬虫选择区域 - 一行4个，粉色配色方案 -->
      <div class="spider-selection">
        <h2>📊 选择爬虫类型</h2>
        <div class="spider-grid">
          <div 
            v-for="spider in spiders" 
            :key="spider.id"
            :class="['spider-card', { active: selectedSpider === spider.id }]"
            @click="selectedSpider = spider.id"
          >
            <div class="spider-icon">{{ spider.icon }}</div>
            <h3>{{ spider.name }}</h3>
            <p>{{ spider.description }}</p>
            <div class="spider-features">
              <span v-for="feature in spider.features" :key="feature" class="feature-tag">
                {{ feature }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 参数配置 -->
      <div v-if="selectedSpider" class="parameter-section">
        <h2>⚙️ 参数配置</h2>
        
        <!-- 百度搜索参数 -->
        <div v-if="selectedSpider === 'baidu'" class="parameter-form">
          <el-form :model="baiduParams" label-width="120px">
            <el-form-item label="搜索关键词">
              <el-input 
                v-model="baiduParams.keyword" 
                placeholder="请输入搜索关键词"
                clearable
                @keyup.enter="executeCrawl"
              />
            </el-form-item>
            <el-form-item label="结果数量">
              <el-input-number 
                v-model="baiduParams.count" 
                :min="1" 
                :max="50"
                :step="1"
                placeholder="爬取结果数量"
                @change="handleCountChange('baidu', baiduParams.count)"
                @keydown.enter.stop.prevent="executeCrawl"
              />
              <div v-if="baiduParams.count > 30" class="count-warning">
                ⚠️ 爬取数量超过30时，准确率可能会下降
              </div>
            </el-form-item>
          </el-form>
        </div>

        <!-- B站搜索参数 -->
        <div v-if="selectedSpider === 'bilibili'" class="parameter-form">
          <!-- B站登录状态 -->
          <div class="bilibili-login-status">
            <el-card class="login-card">
              <!-- 已登录状态 - 用户信息卡片 -->
              <div v-if="bilibiliLogin.isLoggedIn" class="user-info-card">
                <div class="user-avatar-section">
                  <el-avatar 
                    :src="bilibiliLogin.userInfo?.face" 
                    :size="60"
                    class="user-avatar"
                  >
                    <el-icon><User /></el-icon>
                  </el-avatar>
                  <div class="vip-badge" v-if="bilibiliLogin.userInfo?.vip_status === 1">
                    <el-tag type="warning" size="small" effect="dark">大会员</el-tag>
                  </div>
                </div>
                <div class="user-details">
                  <div class="user-name-section">
                    <h4 class="username">{{ bilibiliLogin.userInfo?.username }}</h4>
                    <el-tag size="small" class="level-tag">LV{{ bilibiliLogin.userInfo?.level }}</el-tag>
                  </div>
                  <div class="user-uid">
                    <el-text type="info" size="small">
                      <el-icon><Key /></el-icon>
                      UID: {{ bilibiliLogin.userInfo?.uid }}
                    </el-text>
                  </div>
                  <div class="user-status">
                    <el-tag type="success" size="small" effect="light">
                      <el-icon><CircleCheck /></el-icon>
                      已登录B站
                    </el-tag>
                  </div>
                </div>
                <div class="user-actions">
                  <el-button type="danger" size="small" @click="bilibiliLogout" plain>
                    <el-icon><SwitchButton /></el-icon>
                    注销
                  </el-button>
                </div>
              </div>
              
              <!-- 未登录状态 -->
              <div v-else class="not-logged-in">
                <div class="login-prompt">
                  <el-icon class="login-icon"><Lock /></el-icon>
                  <div class="login-text">
                    <h4>未登录B站</h4>
                    <p>登录后可下载更高清晰度视频</p>
                  </div>
                </div>
                <el-button type="primary" @click="showBilibiliLogin" class="login-btn">
                  <el-icon><User /></el-icon>
                  立即登录
                </el-button>
              </div>
              
              <div class="login-note">
                <el-text type="info" size="small">
                  <el-icon><InfoFilled /></el-icon>
                  部分高清晰度需要"大会员"权限
                </el-text>
              </div>
            </el-card>
          </div>
          
          <el-form :model="bilibiliParams" label-width="120px">
            <el-form-item label="搜索关键词">
              <el-input 
                v-model="bilibiliParams.keyword" 
                placeholder="请输入搜索关键词"
                clearable
                @keyup.enter="executeCrawl"
              />
            </el-form-item>
            <el-form-item label="结果数量">
              <el-input-number 
                v-model="bilibiliParams.count" 
                :min="1" 
                :max="50"
                :step="1"
                placeholder="爬取结果数量"
                @change="handleCountChange('bilibili', bilibiliParams.count)"
                @keydown.enter.stop.prevent="executeCrawl"
              />
              <div v-if="bilibiliParams.count > 30" class="count-warning">
                ⚠️ 爬取数量超过30时，准确率可能会下降
              </div>
            </el-form-item>
          </el-form>
        </div>

        <!-- CSDN搜索参数 -->
        <div v-if="selectedSpider === 'csdn'" class="parameter-form">
          <el-form :model="csdnParams" label-width="120px">
            <el-form-item label="搜索关键词">
              <el-input 
                v-model="csdnParams.keyword" 
                placeholder="请输入搜索关键词"
                clearable
                @keyup.enter="executeCrawl"
              />
            </el-form-item>
            <el-form-item label="结果数量">
              <el-input-number 
                v-model="csdnParams.count" 
                :min="1" 
                :max="50"
                :step="1"
                placeholder="爬取结果数量"
                @change="handleCountChange('csdn', csdnParams.count)"
                @keydown.enter.stop.prevent="executeCrawl"
              />
              <div v-if="csdnParams.count > 30" class="count-warning">
                ⚠️ 爬取数量超过30时，准确率可能会下降
              </div>
            </el-form-item>
          </el-form>
        </div>

        <!-- URL爬取参数 -->
        <div v-if="selectedSpider === 'url'" class="parameter-form">
          <el-form :model="urlParams" label-width="120px">
            <el-form-item label="目标URL">
              <el-input 
                v-model="urlParams.url" 
                placeholder="请输入要爬取的网页URL"
                clearable
                @keyup.enter="executeCrawl"
              />
            </el-form-item>
            <!-- 自定义URL爬取暂时隐藏数据类型选择 -->
            <!-- <el-form-item label="数据类型">
              <el-select v-model="urlParams.dataType" placeholder="选择数据类型">
                <el-option label="文本内容" value="text" />
                <el-option label="图片链接" value="images" />
                <el-option label="所有链接" value="links" />
              </el-select>
            </el-form-item> -->
          </el-form>
        </div>

        <!-- 执行按钮 -->
        <div class="action-section">
          <el-button 
            type="primary" 
            size="large" 
            @click="executeCrawl" 
            :loading="isExecuting"
            :disabled="!canExecute"
            class="execute-btn"
          >
            <el-icon><Search /></el-icon>
            {{ isExecuting ? '执行中...' : '开始爬取' }}
          </el-button>
        </div>
      </div>

      <!-- 零结果提示 -->
      <div v-if="results.length === 0 && hasExecuted" class="no-results-section">
        <div class="no-results-content">
          <el-icon size="48" color="#f56c6c"><Warning /></el-icon>
          <h3>未获取到结果</h3>
          <p>可能的原因：</p>
          <ul>
            <li>触发了网站的反爬虫机制</li>
            <li>关键词过于特殊或不存在相关内容</li>
            <li>网络连接问题</li>
          </ul>
          <p>建议：</p>
          <ul>
            <li>尝试更换关键词</li>
            <li>稍后重试</li>
            <li>检查网络连接</li>
          </ul>
        </div>
      </div>

      <!-- 结果展示 -->
      <div v-if="results.length > 0" class="results-section">
        <div class="results-header">
          <h2>📋 爬取结果</h2>
          <div class="export-buttons">
            <el-button 
              v-for="format in exportFormats" 
              :key="format.type"
              :type="format.type === 'json' ? 'primary' : 'default'"
              size="small"
              class="export-btn"
              @click="exportResults(format.type)"
            >
              <el-icon><Download /></el-icon>
              {{ format.label }}
            </el-button>
          </div>
        </div>

        <div class="results-stats">
          <div class="results-stats-header">
            <el-statistic title="总结果数" :value="results.length" />
            <el-statistic title="关键词" :value="truncateKeyword(displayedKeyword)" />
            <el-statistic title="成功率" :value="successRate" suffix="%" />
            <el-statistic title="当前页数" :value="`${currentPage}/${totalPages}`" />
          </div>
        </div>

        <div class="results-list">
          <div 
            v-for="(result, index) in paginatedResults" 
            :key="index"
            class="result-item"
          >
            <div class="result-header">
              <span class="result-index">#{{ (currentPage - 1) * pageSize + index + 1 }}</span>
              <div class="header-actions">
                <!-- B站结果显示下载按钮 -->
                <el-button 
                  v-if="selectedSpider === 'bilibili'"
                  type="primary" 
                  size="small" 
                  class="download-btn"
                  @click="downloadBilibiliVideo(result)"
                >
                  <el-icon><Download /></el-icon>
                  下载视频
                </el-button>
                <!-- 百度结果不显示展开按钮 -->
                <el-button 
                  v-if="!isBaiduResult(result)"
                  type="text" 
                  size="small" 
                  class="toggle-btn"
                  @click="toggleResultDetail((currentPage - 1) * pageSize + index)"
                >
                  {{ expandedResults.includes((currentPage - 1) * pageSize + index) ? '收起' : '展开' }}
                </el-button>
              </div>
            </div>
            
            <div class="result-preview">
              <div class="result-content">
                <h4 v-if="result.title">{{ result.title }}</h4>
                <p v-if="result.description" class="result-description">
                  {{ truncateText(result.description, 100) }}
                </p>
                <div v-if="result.url" class="url-meta">
                  <el-link :href="result.url" target="_blank" type="primary">
                    <el-icon><Link /></el-icon>
                    {{ result.url }}
                  </el-link>
                </div>
              </div>
            </div>

            <div v-if="expandedResults.includes((currentPage - 1) * pageSize + index) && !isBaiduResult(result)" class="result-detail">
              <!-- 百度结果的特殊显示 -->
              <div v-if="isBaiduResult(result)" class="baidu-detail">
                <!-- 百度结果不显示展开内容 -->
              </div>
              
              <!-- B站结果的特殊显示 -->
              <div v-else-if="isBilibiliResult(result)" class="bilibili-detail">
                <div class="detail-item" v-if="result.author || result.up_name">
                  <span class="detail-label">👤 作者:</span>
                  <span class="detail-value">{{ result.author || result.up_name }}</span>
                </div>
                <div class="detail-item" v-if="result.publish_time || result.pubdate">
                  <span class="detail-label">📅 发布日期:</span>
                  <span class="detail-value">{{ result.publish_time || result.pubdate }}</span>
                </div>
                <div class="detail-item" v-if="result.view_count || result.play">
                  <span class="detail-label">👁️ 播放量:</span>
                  <span class="detail-value">{{ result.view_count || result.play }}</span>
                </div>
              </div>
              
              <!-- CSDN结果的特殊显示 -->
              <div v-else-if="isCSDNResult(result)" class="csdn-detail">
                <div class="detail-item" v-if="result.author">
                  <span class="detail-label">👤 作者:</span>
                  <span class="detail-value">{{ result.author }}</span>
                </div>
                <div class="detail-item" v-if="result.publish_time || result.date">
                  <span class="detail-label">📅 发布日期:</span>
                  <span class="detail-value">{{ result.publish_time || result.date }}</span>
                </div>
                <div class="detail-item" v-if="result.view_count || result.views">
                  <span class="detail-label">👁️ 浏览量:</span>
                  <span class="detail-value">{{ result.view_count || result.views }}</span>
                </div>
              </div>
              
              <!-- 自定义URL结果的完整显示（不隐藏任何内容） -->
              <div v-else-if="selectedSpider === 'url'" class="url-detail">
                <div class="url-full-content">
                  <!-- 网页基本信息 -->
                  <div class="url-metadata">
                    <h4>📄 网页信息</h4>
                    <div class="metadata-grid">
                      <div class="metadata-item">
                        <span class="label">标题:</span>
                        <span class="value">{{ result.title || '无标题' }}</span>
                      </div>
                      <div class="metadata-item">
                        <span class="label">URL:</span>
                        <a :href="result.url" target="_blank" class="url-link">{{ result.url }}</a>
                      </div>
                      <div class="metadata-item">
                        <span class="label">文本长度:</span>
                        <span class="value">{{ result.text_length || 0 }} 字符</span>
                      </div>
                      <div class="metadata-item">
                        <span class="label">图片数量:</span>
                        <span class="value">{{ result.images_count || 0 }} 张</span>
                      </div>
                      <div class="metadata-item">
                        <span class="label">爬取时间:</span>
                        <span class="value">{{ result.crawl_time }}</span>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 完整文本内容 -->
                  <div v-if="result.full_content" class="url-full-text">
                    <h4>📝 完整文本内容</h4>
                    <div class="full-text-content">
                      {{ result.full_content }}
                    </div>
                  </div>
                  
                  <!-- 图片展示 -->
                  <div v-if="result.images && result.images.length > 0" class="url-images">
                    <h4>🖼️ 网页图片 ({{ result.images.length }} 张)</h4>
                    <div class="images-grid">
                      <div 
                        v-for="(image, imgIndex) in result.images" 
                        :key="imgIndex" 
                        class="image-item"
                      >
                        <img 
                          :src="image" 
                          :alt="`图片 ${imgIndex + 1}`" 
                          @error="handleImageError"
                          @click="previewImage(image)"
                        />
                        <div class="image-url">
                          <a :href="image" target="_blank" class="image-link">查看原图</a>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 技术元数据 -->
                  <div v-if="result.metadata" class="url-tech-metadata">
                    <h4>🔧 技术信息</h4>
                    <div class="tech-metadata-grid">
                      <div v-if="result.metadata.content_type" class="tech-item">
                        <span class="label">内容类型:</span>
                        <span class="value">{{ result.metadata.content_type }}</span>
                      </div>
                      <div v-if="result.metadata.status_code" class="tech-item">
                        <span class="label">状态码:</span>
                        <span class="value">{{ result.metadata.status_code }}</span>
                      </div>
                      <div v-if="result.metadata.charset" class="tech-item">
                        <span class="label">字符编码:</span>
                        <span class="value">{{ result.metadata.charset }}</span>
                      </div>
                      <div v-if="result.metadata.final_url && result.metadata.final_url !== result.url" class="tech-item">
                        <span class="label">最终URL:</span>
                        <span class="value">{{ result.metadata.final_url }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 通用结果显示 -->
              <div v-else class="generic-detail">
                <div v-if="result.content" class="content-section">
                  <h5>📄 内容详情</h5>
                  <div class="content-text" v-html="formatContent(result.content)"></div>
                </div>
                
                <div v-if="result.images && result.images.length > 0" class="images-section">
                  <h5>🖼️ 相关图片</h5>
                  <div class="images-grid">
                    <div 
                      v-for="(image, imgIndex) in result.images.slice(0, 6)" 
                      :key="imgIndex"
                      class="image-item"
                    >
                      <img :src="image" :alt="`图片 ${imgIndex + 1}`" @error="handleImageError" />
                    </div>
                  </div>
                </div>
                
                <div v-if="result.metadata" class="metadata-section">
                  <h5>ℹ️ 元数据</h5>
                  <div class="metadata-grid">
                    <div 
                      v-for="(value, key) in result.metadata" 
                      :key="key"
                      class="metadata-item"
                    >
                      <span class="metadata-key">{{ key }}:</span>
                      <span class="metadata-value">{{ value }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="totalPages > 1" class="pagination-section">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="results.length"
            layout="prev, pager, next, jumper"
            @current-change="handlePageChange"
          />
        </div>
      </div>

      <!-- 任务状态 -->
      <div v-if="tasks.length > 0" class="tasks-section">
        <h2>⏳ 任务状态</h2>
        <div class="tasks-list">
          <div 
            v-for="task in tasks" 
            :key="task.id"
            class="task-item"
          >
            <div class="task-info">
              <span class="task-id">#{{ task.id }}</span>
              <span class="task-type">{{ task.spider_type }}</span>
              <span class="task-keyword">{{ task.keyword || task.url }}</span>
            </div>
            <div class="task-status">
              <el-tag 
                :type="getTaskStatusType(task.status)"
                size="small"
              >
                {{ getTaskStatusLabel(task.status) }}
              </el-tag>
            </div>
            <div class="task-progress">
              <el-progress 
                :percentage="task.progress || 0"
                :status="task.status === 'completed' ? 'success' : task.status === 'failed' ? 'exception' : ''"
                :stroke-width="6"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- B站登录对话框 -->
    <el-dialog 
      v-model="bilibiliLogin.showLoginDialog" 
      title="B站登录" 
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="login-dialog-content">
        <div class="qr-code-section">
          <div class="qr-code-title">扫码登录B站</div>
          <div class="qr-code-container">
            <img 
              v-if="bilibiliLogin.qrCodeUrl" 
              :src="bilibiliLogin.qrCodeUrl" 
              alt="登录二维码" 
              class="qr-code-img"
            />
            <div v-else class="qr-code-loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              <p>正在生成二维码...</p>
            </div>
          </div>
          <div class="qr-code-tips">
            <p>请使用B站手机客户端扫描二维码</p>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="closeBilibiliLoginDialog">取消</el-button>
      </template>
    </el-dialog>

    <!-- B站视频下载对话框 -->
    <el-dialog 
      v-model="showVideoDownloadDialog" 
      title="B站视频下载" 
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="download-dialog-content">
        <el-tabs v-model="downloadDialogActiveTab" type="border-card">
          <!-- 单个视频下载 -->
          <el-tab-pane label="单个下载" name="single">
            <el-form :model="videoDownloadForm" label-width="100px">
              <el-form-item label="视频链接">
                <el-input 
                  v-model="videoDownloadForm.url" 
                  placeholder="请输入B站视频链接"
                  clearable
                >
                  <template #append>
                    <el-button 
                      @click="getVideoInfo" 
                      :loading="gettingVideoInfo"
                      type="primary"
                    >
                      获取信息
                    </el-button>
                  </template>
                </el-input>
              </el-form-item>
            </el-form>

            <div v-if="videoInfo" class="video-info-section">
              <el-form :model="videoDownloadForm" label-width="100px">
                <el-form-item label="视频标题">
                  <el-input v-model="videoInfo.title" readonly />
                </el-form-item>
                <el-form-item label="视频时长">
                  <el-input v-model="videoInfo.duration" readonly />
                </el-form-item>
                <el-form-item label="清晰度">
                  <el-select v-model="videoDownloadForm.quality" placeholder="选择清晰度">
                    <el-option 
                      v-for="quality in videoInfo.qualities" 
                      :key="quality.quality"
                      :label="quality.display_desc || quality.description" 
                      :value="quality.quality"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item label="保存路径">
                  <el-input v-model="videoDownloadForm.savePath" placeholder="下载保存路径（可选）" />
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>
          
          <!-- 批量下载 -->
          <el-tab-pane label="批量下载" name="batch">
            <el-form label-width="100px">
              <el-form-item label="视频链接">
                <el-input 
                  v-model="batchDownloadForm.urls" 
                  type="textarea" 
                  :rows="6"
                  placeholder="请输入多个B站视频链接，每行一个"
                />
              </el-form-item>
              <el-form-item label="默认清晰度">
                <el-select v-model="batchDownloadForm.defaultQuality" placeholder="选择默认清晰度">
                  <el-option label="1080P" :value="80" />
                  <el-option label="720P" :value="64" />
                  <el-option label="480P" :value="32" />
                  <el-option label="360P" :value="16" />
                </el-select>
              </el-form-item>
              <el-form-item label="保存路径">
                <el-input v-model="batchDownloadForm.savePath" placeholder="批量下载保存路径（可选）" />
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <!-- 下载设置 -->
          <el-tab-pane label="下载设置" name="settings">
            <el-form label-width="120px">
              <el-form-item label="同时下载数">
                <el-input-number v-model="downloadSettings.maxConcurrent" :min="1" :max="5" />
              </el-form-item>
              <el-form-item label="自动重试">
                <el-switch v-model="downloadSettings.autoRetry" />
              </el-form-item>
              <el-form-item label="重试次数">
                <el-input-number v-model="downloadSettings.retryCount" :min="1" :max="10" :disabled="!downloadSettings.autoRetry" />
              </el-form-item>
              <el-form-item label="下载完成提醒">
                <el-switch v-model="downloadSettings.notification" />
              </el-form-item>
              <el-form-item label="自动合并音视频">
                <el-switch v-model="downloadSettings.autoMerge" />
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <el-button @click="showVideoDownloadDialog = false">取消</el-button>
        
        <!-- 单个下载按钮 -->
        <el-button 
          v-if="downloadDialogActiveTab === 'single'"
          type="primary" 
          @click="downloadVideo" 
          :loading="downloadingVideo"
          :disabled="!videoInfo || !videoDownloadForm.quality"
        >
          开始下载
        </el-button>
        
        <!-- 批量下载按钮 -->
        <el-button 
          v-if="downloadDialogActiveTab === 'batch'"
          type="primary" 
          @click="startBatchDownload" 
          :loading="batchDownloading"
          :disabled="!batchDownloadForm.urls || !batchDownloadForm.defaultQuality"
        >
          开始批量下载
        </el-button>
        
        <!-- 设置保存按钮 -->
        <el-button 
          v-if="downloadDialogActiveTab === 'settings'"
          type="primary" 
          @click="saveDownloadSettings"
        >
          保存设置
        </el-button>
      </template>
    </el-dialog>

    <!-- B站清晰度选择对话框 -->    
    <el-dialog v-model="showQualityDialog" title="选择清晰度" width="400px">
      <div class="quality-selection-content">
        <div class="video-info-preview">
          <h4>{{ selectedVideoForDownload?.title || '视频标题' }}</h4>
          <p class="video-meta">{{ selectedVideoForDownload?.bv_id || selectedVideoForDownload?.url?.match(/BV[a-zA-Z0-9]+/)?.[0] || 'BV号获取中...' }}</p>
        </div>
        
        <el-form :model="qualityForm" label-width="80px">
          <el-form-item label="清晰度">
            <el-select v-model="qualityForm.quality" placeholder="选择清晰度" style="width: 100%">
              <el-option 
                v-for="quality in availableQualities" 
                :key="quality.quality"
                :label="quality.display_desc || quality.description" 
                :value="quality.quality"
                :disabled="!quality.available"
              >
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span>{{ quality.display_desc || quality.description }}</span>
                  <span style="color: #409EFF; font-size: 12px; margin-left: 10px;">
                    {{ quality.file_size_text || '计算中...' }}
                  </span>
                </div>
                <span v-if="!quality.available" style="color: #ff6b6b; font-size: 12px;"> (需要登录获取)</span>
              </el-option>
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <el-button @click="showQualityDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="confirmDownloadWithQuality" 
          :loading="downloadingVideo"
          :disabled="!qualityForm.quality"
        >
          开始下载
        </el-button>
      </template>
    </el-dialog>

    <!-- 下载任务管理 -->
    <div v-if="downloadTasks.length > 0" class="download-tasks-section">
      <el-card class="download-tasks-card">
        <template #header>
          <div class="download-tasks-header">
            <div class="header-left">
              <h3>📥 下载任务 ({{ downloadTasks.length }})</h3>
            </div>
            <div class="header-right">
              <el-button 
                :icon="isTasksMinimized ? 'ArrowDown' : 'ArrowUp'"
                @click="isTasksMinimized = !isTasksMinimized"
                size="small"
                text
                :title="isTasksMinimized ? '展开任务列表' : '最小化任务列表'"
              >
                {{ isTasksMinimized ? '展开' : '最小化' }}
              </el-button>
            </div>
          </div>
        </template>
        
        <div class="download-tasks-list" v-show="!isTasksMinimized">
          <div 
            v-for="(task, index) in downloadTasks" 
            :key="task.id"
            class="download-task-item"
          >
            <div class="task-info">
              <div class="task-title">
                <span class="task-number">#{{ index + 1 }}</span>
                <el-icon><VideoPlay /></el-icon>
                <span>{{ task.title || task.filename || '未知任务' }}</span>
              </div>
              <div class="task-meta">
                <span class="task-id">ID: {{ task.id }}</span>
                <span class="task-quality" v-if="task.quality">{{ getQualityName(task.quality) }}</span>
              </div>
            </div>
            
            <div class="task-progress">
              <div class="progress-info">
                <span class="progress-text">{{ getTaskStatusText(task) }}</span>
                <span class="progress-percent">{{ Math.round(task.progress || 0) }}%</span>
              </div>
              <el-progress 
                :percentage="task.progress || 0"
                :status="getProgressStatus(task.status)"
                :stroke-width="8"
                :show-text="false"
              />
              <div v-if="task.speed || task.downloaded || task.total" class="speed-info">
                <span v-if="task.speed" class="speed-text">{{ formatSpeed(task.speed) }}</span>
                <span v-if="task.downloaded && task.total" class="size-text">
                  {{ formatFileSize(task.downloaded) }} / {{ formatFileSize(task.total) }}
                </span>
                <span v-if="task.eta" class="eta-text">剩余: {{ formatTime(task.eta) }}</span>
                <span v-if="task.file_type" class="file-type-text">[{{ task.file_type }}]</span>
              </div>
            </div>
            
            <div class="task-actions">

              <el-button 
                v-if="task.status === 'error'"
                type="danger" 
                size="small" 
                @click="retryDownload(task)"
              >
                重试
              </el-button>
              <el-button 
                v-if="task.status === 'downloading'"
                type="danger" 
                size="small" 
                @click="cancelDownload(task)"
              >
                取消
              </el-button>
              <el-button 
                v-if="task.status === 'error' && task.message && task.message.includes('合并')"
                type="primary" 
                size="small" 
                @click="mergeVideoAudio(task)"
              >
                手动合并
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, Download, Link, User, Lock, Loading, 
  Key, CircleCheck, SwitchButton, InfoFilled, VideoPlay, Warning,
  ArrowDown, ArrowUp
} from '@element-plus/icons-vue'
import { io } from 'socket.io-client'

export default {
  name: 'Crawler',
  components: {
    Search, Download, Link, User, Lock, Loading,
    Key, CircleCheck, SwitchButton, InfoFilled, VideoPlay,
    ArrowDown, ArrowUp, Warning
  },
  setup() {
    // ==================== 核心状态管理 ====================
    const selectedSpider = ref('')        // 当前选择的爬虫类型（baidu/bilibili/csdn/url）
    const isExecuting = ref(false)         // 是否正在执行爬取任务
    const hasExecuted = ref(false)         // 是否已执行过爬取（用于显示结果区域）
    const results = ref([])               // 爬取结果数组
    const displayedKeyword = ref('')      // 显示的关键词（固定不变）
    const tasks = ref([])                 // 任务状态列表
    const expandedResults = ref([])       // 展开的结果项索引数组（v2.0: 默认全部收起）
    const currentPage = ref(1)            // 当前分页页码
    const pageSize = ref(15)              // 每页显示数量（v2.1: 优化为15条）
    const executionTime = ref(0)          // 爬取执行时间（毫秒）
    
    // ==================== WebSocket 连接管理 ====================
    const socket = ref(null)              // Socket.IO 连接实例
    const downloadTasks = ref([])         // 下载任务列表
    const isTasksMinimized = ref(false)   // 下载任务界面最小化状态
    
    // ==================== 爬虫配置 ====================
    const spiders = ref([])               // 可用爬虫列表（从后端获取）
    
    // ==================== 爬虫参数配置 ====================
    const baiduParams = reactive({
      keyword: '',                        // 百度搜索关键词
      count: 10                          // 爬取数量（v2.0: 最低限制为1）
    })
    
    const bilibiliParams = reactive({
      keyword: '',                        // B站搜索关键词
      count: 10                          // 爬取数量（v2.0: 结果按播放量排序）
    })
    
    const csdnParams = reactive({
      keyword: '',                        // CSDN搜索关键词
      count: 10                          // 爬取数量（v2.0: 结果按浏览量排序）
    })
    
    const urlParams = reactive({
      url: '',                           // 自定义URL地址
      dataType: 'text'                   // 数据类型（text/json）
    })
    
    // B站登录相关
    const bilibiliLogin = reactive({
      isLoggedIn: false,
      userInfo: null,
      showLoginDialog: false,
      qrCodeUrl: '',
      qrcodeKey: '',
      loginPolling: null
    })
    
    // B站视频下载相关
    const showVideoDownloadDialog = ref(false)
    const gettingVideoInfo = ref(false)
    const downloadingVideo = ref(false)
    const videoInfo = ref(null)
    const videoDownloadForm = reactive({
      url: '',
      quality: '',
      savePath: ''
    })
    
    // B站清晰度选择相关
    const showQualityDialog = ref(false)
    const selectedVideoForDownload = ref(null)
    const availableQualities = ref([])
    const qualityForm = reactive({
      quality: '',
      savePath: ''
    })
    
    // 增强下载对话框相关
    const downloadDialogActiveTab = ref('single')
    const batchDownloading = ref(false)
    const batchDownloadForm = reactive({
      urls: '',
      defaultQuality: 80,
      savePath: ''
    })
    const downloadSettings = reactive({
      maxConcurrent: 2,
      autoRetry: true,
      retryCount: 3,
      notification: true,
      autoMerge: true
    })
    
    // 导出格式
    const exportFormats = [
      { type: 'json', label: 'JSON' },
      { type: 'csv', label: 'CSV' },
      { type: 'txt', label: 'TXT' },
      { type: 'md', label: 'Markdown' }
    ]
    
    // 计算属性
    /**
     * 检查是否可以执行爬取任务
     * 根据选中的爬虫类型验证必要参数是否已填写
     */
    const canExecute = computed(() => {
      if (!selectedSpider.value) return false
      
      switch (selectedSpider.value) {
        case 'baidu':
        case 'bilibili':
        case 'csdn':
          return baiduParams.keyword || bilibiliParams.keyword || csdnParams.keyword
        case 'url':
          return urlParams.url
        default:
          return false
      }
    })
    
    /**
     * 获取当前搜索关键词
     * 根据选中的爬虫类型返回对应的关键词或URL
     */
    const currentKeyword = computed(() => {
      switch (selectedSpider.value) {
        case 'baidu':
          return baiduParams.keyword || ''
        case 'bilibili':
          return bilibiliParams.keyword || ''
        case 'csdn':
          return csdnParams.keyword || ''
        case 'url':
          return urlParams.url || ''
        default:
          return ''
      }
    })
    
    /**
     * 分页显示的结果列表
     * 根据当前页码和每页大小计算显示的结果
     */
    const paginatedResults = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return results.value.slice(start, end)
    })
    
    /**
     * 总页数计算
     * 根据结果总数和每页大小计算总页数
     */
    const totalPages = computed(() => {
      return Math.ceil(results.value.length / pageSize.value)
    })
    
    // ==================== 成功率管理（v2.0 优化） ====================
    /**
     * 成功率百分比（响应式变量）
     * v2.0 改进：改为爬取完成后手动更新，而非实时计算属性
     * 计算公式：(实际获取数量 / 期望数量) * 100
     * 自定义URL爬取不显示成功率
     */
    const successRate = ref(0)
    
    /**
     * 更新成功率
     * 在爬取完成后调用，计算并更新成功率
     */
    const updateSuccessRate = () => {
      if (results.value.length === 0) {
        successRate.value = 0
        return
      }
      
      // 获取用户设置的期望结果数量
      let expectedCount = 10
      switch (selectedSpider.value) {
        case 'baidu':
          expectedCount = baiduParams.count
          break
        case 'bilibili':
          expectedCount = bilibiliParams.count
          break
        case 'csdn':
          expectedCount = csdnParams.count
          break
      }
      
      // 成功率 = 实际获取结果数 / 期望结果数
      successRate.value = Math.round((results.value.length / expectedCount) * 100)
    }
    
    /**
     * 按指标排序结果
     * 根据播放量、浏览量等指标由高到低排序
     */
    const sortResultsByMetrics = (results) => {
      return results.sort((a, b) => {
        // B站结果按播放量排序
        if (selectedSpider.value === 'bilibili') {
          const aPlay = parseInt(a.play || a.view_count || 0)
          const bPlay = parseInt(b.play || b.view_count || 0)
          return bPlay - aPlay
        }
        // CSDN结果按浏览量排序
        else if (selectedSpider.value === 'csdn') {
          const aViews = parseInt(a.views || a.view_count || 0)
          const bViews = parseInt(b.views || b.view_count || 0)
          return bViews - aViews
        }
        // 百度和其他结果保持原有顺序
        return 0
      })
    }
    
    // 方法定义
    /**
     * 加载可用的爬虫列表
     * 从后端API获取支持的爬虫类型和配置信息
     */
    const loadSpiders = async () => {
      try {
        const response = await axios.get('/api/spiders')
        spiders.value = response.data
      } catch (error) {
        console.error('加载爬虫列表失败:', error)
        ElMessage.error('加载爬虫列表失败')
      }
    }
    
    /**
     * 执行爬取任务
     * 增强版：增加displayedKeyword固定设置
     */
    const executeCrawl = async () => {
      if (!canExecute.value) return

      try {
        isExecuting.value = true
        
        // 清空之前的结果
        results.value = []
        expandedResults.value = []
        
        // 设置固定的显示关键词（爬取时确定，不再实时变化）
        if (selectedSpider.value === 'baidu') {
          displayedKeyword.value = baiduParams.keyword
        } else if (selectedSpider.value === 'bilibili') {
          displayedKeyword.value = bilibiliParams.keyword
        } else if (selectedSpider.value === 'csdn') {
          displayedKeyword.value = csdnParams.keyword
        } else if (selectedSpider.value === 'url') {
          displayedKeyword.value = urlParams.url
        }

        // 构建请求参数
        let requestData = {
          spider_type: selectedSpider.value
        }

        if (selectedSpider.value === 'url') {
          requestData.url = urlParams.url
        } else {
          requestData.keyword = displayedKeyword.value
          requestData.max_results = selectedSpider.value === 'baidu' ? baiduParams.count :
                                  selectedSpider.value === 'bilibili' ? bilibiliParams.count :
                                  csdnParams.count
          requestData.data_type = selectedSpider.value === 'baidu' ? baiduParams.dataType : 'text'
        }

        ElMessage.info('开始爬取数据...')
        
        const response = await axios.post('/api/crawl', requestData)
        
        if (response.data.success) {
          const crawlResults = response.data.results || []
          
          ElMessage.success(`爬取完成！获取到 ${crawlResults.length} 条结果`)
          results.value = crawlResults

          // 自定义URL爬取结果默认展开全部内容，其他爬虫默认收起
          if (selectedSpider.value === 'url') {
            expandedResults.value = crawlResults.map((_, index) => index)
          } else {
            expandedResults.value = []
          }

          hasExecuted.value = true
          
          // 更新成功率（爬取完成后）
          updateSuccessRate()
        } else {
          ElMessage.error(response.data.message || '爬取失败')
        }
      } catch (error) {
        console.error('爬取错误:', error)
        ElMessage.error(`爬取失败: ${error.response?.data?.message || error.message}`)
      } finally {
        isExecuting.value = false
      }
    }
    
    const exportResults = async (format) => {
      if (results.value.length === 0) {
        ElMessage.warning('没有可导出的数据')
        return
      }
      
      try {
        let content = ''
        let filename = `crawler_results_${Date.now()}`
        let mimeType = 'text/plain'
        
        // 根据格式生成不同的导出内容
        switch (format) {
          case 'json':
            content = JSON.stringify(results.value, null, 2)
            filename += '.json'
            mimeType = 'application/json'
            break
            
          case 'csv':
            // 生成CSV格式
            if (results.value.length > 0) {
              const headers = Object.keys(results.value[0]).join(',')
              const rows = results.value.map(item => 
                Object.values(item).map(val => 
                  typeof val === 'string' && val.includes(',') ? `"${val}"` : val
                ).join(',')
              )
              content = [headers, ...rows].join('\n')
            }
            filename += '.csv'
            mimeType = 'text/csv'
            break
            
          case 'txt':
            content = results.value.map((item, index) => {
              const lines = [`结果 ${index + 1}:`]
              Object.entries(item).forEach(([key, value]) => {
                lines.push(`${key}: ${value}`)
              })
              return lines.join('\n')
            }).join('\n\n')
            filename += '.txt'
            mimeType = 'text/plain'
            break
            
          case 'markdown':
            content = '# 爬取结果\n\n'
            results.value.forEach((item, index) => {
              content += `## 结果 ${index + 1}\n\n`
              Object.entries(item).forEach(([key, value]) => {
                content += `**${key}**: ${value}\n\n`
              })
            })
            filename += '.md'
            mimeType = 'text/markdown'
            break
            
          default:
            throw new Error('不支持的导出格式')
        }
        
        // 创建并下载文件
        const blob = new Blob([content], { type: mimeType })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        link.click()
        window.URL.revokeObjectURL(url)
        
        ElMessage.success('导出成功')
      } catch (error) {
        console.error('导出失败:', error)
        ElMessage.error('导出失败')
      }
    }
    
    const toggleResultDetail = (index) => {
      const expandedIndex = expandedResults.value.indexOf(index)
      if (expandedIndex > -1) {
        expandedResults.value.splice(expandedIndex, 1)
      } else {
        expandedResults.value.push(index)
      }
    }
    
    const handlePageChange = (page) => {
      currentPage.value = page
      expandedResults.value = []
    }
    
    /**
     * 判断是否为百度搜索结果
     */
    const isBaiduResult = (result) => {
      return selectedSpider.value === 'baidu' || (result.url && result.url.includes('baidu.com'))
    }
    
    /**
     * 判断是否为B站搜索结果
     */
    const isBilibiliResult = (result) => {
      return selectedSpider.value === 'bilibili' || (result.url && result.url.includes('bilibili.com'))
    }
    
    /**
     * 判断是否为CSDN搜索结果
     */
    const isCSDNResult = (result) => {
      return selectedSpider.value === 'csdn' || (result.url && result.url.includes('csdn.net'))
    }
    
    /**
     * 处理爬取数量变化，确保只能使用整数
     * - 非数字或空值 -> 设为 1
     * - 小数 -> 向下取整
     * - 边界 -> [1, 50]
     * 处理后调用原有 checkCrawlCount 以维持提示逻辑
     */
    const handleCountChange = (spiderType, count) => {
      // 非数字或空值矫正
      if (typeof count !== 'number' || isNaN(count)) {
        count = 1
      }

      // 小数自动向下取整
      count = Math.floor(count)

      // 边界限制
      if (count < 1) count = 1
      if (count > 50) count = 50

      // 写回对应参数
      switch (spiderType) {
        case 'baidu':
          baiduParams.count = count
          break
        case 'bilibili':
          bilibiliParams.count = count
          break
        case 'csdn':
          csdnParams.count = count
          break
      }

      // 保持原有提示逻辑
      checkCrawlCount(spiderType, count)
    }
    
    /**
     * 检查爬取数量并显示提示
     * 确保爬取数量最低为1，不能为空
     */
    const checkCrawlCount = (spiderType, count) => {
      // 检查最小值限制
      if (!count || count < 1) {
        ElMessage.error('爬取数量不能为空，最低为1条')
        // 自动修正为最小值
        switch (spiderType) {
          case 'baidu':
            baiduParams.count = 1
            break
          case 'bilibili':
            bilibiliParams.count = 1
            break
          case 'csdn':
            csdnParams.count = 1
            break
        }
        return
      }
      
      // 检查准确率警告
      if (count > 30) {
        ElMessage.warning(`爬取数量超过30时，${spiderType === 'baidu' ? '百度' : spiderType === 'bilibili' ? 'B站' : 'CSDN'}搜索的准确率可能会下降`)
      }
    }
    
    const getTaskStatusType = (status) => {
      switch (status) {
        case 'completed': return 'success'
        case 'failed': return 'danger'
        case 'running': return 'warning'
        default: return 'info'
      }
    }
    
    const getTaskStatusLabel = (status) => {
      switch (status) {
        case 'pending': return '等待中'
        case 'running': return '执行中'
        case 'completed': return '已完成'
        case 'failed': return '失败'
        default: return '未知'
      }
    }
    
    const truncateText = (text, maxLength) => {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    }
    
    /**
     * 截断关键词显示，防止过长影响界面布局
     */
    const truncateKeyword = (keyword) => {
      if (!keyword) return '未设置'
      return keyword.length > 20 ? keyword.substring(0, 20) + '...' : keyword
    }
    
    const handleImageError = (event) => {
      event.target.style.display = 'none'
    }
    

    

    
    /**
     * 格式化显示内容
     * 处理换行、链接、标题等格式化显示
     * 提供更好的内容阅读体验
     */
    const formatContent = (content) => {
      if (!content) return ''
      
      // 简单的内容格式化
      let formatted = content.replace(/\n/g, '<br>')
      
      // 处理链接
      formatted = formatted.replace(
        /(https?:\/\/[^\s<>"]+)/g,
        '<a href="$1" target="_blank" class="content-link">$1</a>'
      )
      
      // 处理标题部分，使其更加突出
      formatted = formatted.replace(
        /^标题: (.+?)<br>/,
        '<div class="content-title">📄 $1</div><br>'
      )
      
      // 处理图片部分标题
      formatted = formatted.replace(
        /<br>网页包含以下图片:<br>/g,
        '<br><div class="images-section-title">🖼️ 网页包含的图片:</div>'
      )
      
      return formatted
    }

    /**
     * 图片预览功能
     */
    const previewImage = (imageUrl) => {
      // 创建图片预览弹窗
      ElMessageBox({
        title: '图片预览',
        message: `<img src="${imageUrl}" style="max-width: 100%; max-height: 400px;" />`,
        dangerouslyUseHTMLString: true,
        showCancelButton: false,
        confirmButtonText: '关闭'
      })
    }

    // B站登录相关方法
    const checkBilibiliLoginStatus = async () => {
      try {
        const response = await axios.get('/api/bilibili/login/status')
        if (response.data.success) {
          bilibiliLogin.isLoggedIn = response.data.logged_in
          bilibiliLogin.userInfo = response.data.user_info || null
        }
      } catch (error) {
        console.error('检查登录状态失败:', error)
      }
    }

    const showBilibiliLogin = async () => {
      bilibiliLogin.showLoginDialog = true
      await getBilibiliQRCode()
    }

    const getBilibiliQRCode = async () => {
      try {
        const response = await axios.get('/api/bilibili/login/qr')
        if (response.data.success) {
          bilibiliLogin.qrCodeUrl = response.data.qr_url
          bilibiliLogin.qrcodeKey = response.data.qrcode_key
          startLoginPolling()
        } else {
          ElMessage.error('获取登录二维码失败')
        }
      } catch (error) {
        console.error('获取二维码失败:', error)
        ElMessage.error('获取登录二维码失败')
      }
    }

    const startLoginPolling = () => {
      if (bilibiliLogin.loginPolling) {
        clearInterval(bilibiliLogin.loginPolling)
      }
      
      bilibiliLogin.loginPolling = setInterval(async () => {
        try {
          const response = await axios.post('/api/bilibili/login/poll', {
            qrcode_key: bilibiliLogin.qrcodeKey
          })
          
          if (response.data.success) {
            if (response.data.status === 'success') {
              clearInterval(bilibiliLogin.loginPolling)
              bilibiliLogin.showLoginDialog = false
              await checkBilibiliLoginStatus()
              ElMessage.success('B站登录成功！')
            }
          }
        } catch (error) {
          console.error('轮询登录状态失败:', error)
        }
      }, 2000)
    }

    const bilibiliLogout = async () => {
      try {
        const response = await axios.post('/api/bilibili/logout')
        if (response.data.success) {
          bilibiliLogin.isLoggedIn = false
          bilibiliLogin.userInfo = null
          ElMessage.success('已注销B站登录')
        }
      } catch (error) {
        console.error('注销失败:', error)
        ElMessage.error('注销失败')
      }
    }

    const closeBilibiliLoginDialog = () => {
      bilibiliLogin.showLoginDialog = false
      if (bilibiliLogin.loginPolling) {
        clearInterval(bilibiliLogin.loginPolling)
        bilibiliLogin.loginPolling = null
      }
    }

    // B站视频下载相关方法
    const getVideoInfo = async () => {
      if (!videoDownloadForm.url) {
        ElMessage.warning('请输入视频链接')
        return
      }
      
      gettingVideoInfo.value = true
      try {
        const response = await axios.post('/api/bilibili/video/info', {
          video_url: videoDownloadForm.url
        })
        
        if (response.data.success) {
          videoInfo.value = response.data.data
          ElMessage.success('获取视频信息成功')
        } else {
          ElMessage.error(response.data.message || '获取视频信息失败')
        }
      } catch (error) {
        console.error('获取视频信息失败:', error)
        ElMessage.error('获取视频信息失败')
      } finally {
        gettingVideoInfo.value = false
      }
    }

    const downloadVideo = async () => {
      if (!videoInfo.value || !videoDownloadForm.quality) {
        ElMessage.warning('请先获取视频信息并选择清晰度')
        return
      }
      
      downloadingVideo.value = true
      try {
        const response = await axios.post('/api/bilibili/video/download', {
          video_url: videoDownloadForm.url,
          quality: videoDownloadForm.quality,
          save_path: videoDownloadForm.savePath
        })
        
        if (response.data.success) {
          ElMessage.success('下载任务已启动！')
          
          // 添加任务到下载列表
          const newTask = {
            id: response.data.task_id,
            title: videoInfo.value.title || '未知视频',
            status: 'pending',
            progress: 0,
            quality: videoDownloadForm.quality,
            url: videoDownloadForm.url
          }
          downloadTasks.value.push(newTask)
          
          showVideoDownloadDialog.value = false
        } else {
          ElMessage.error(response.data.message || '启动下载失败')
        }
      } catch (error) {
        console.error('启动下载失败:', error)
        ElMessage.error('启动下载失败，请重试')
      } finally {
        downloadingVideo.value = false
      }
    }
    
    // B站结果直接下载方法
    const downloadBilibiliVideo = async (result) => {
      if (!result.url) {
        ElMessage.warning('无法获取视频链接')
        return
      }
      
      try {
        // 先获取视频信息和清晰度选项
        const response = await axios.post('/api/bilibili/video/info', {
          video_url: result.url
        })
        
        if (response.data.success) {
          // 设置可用清晰度
          availableQualities.value = response.data.qualities.map(q => ({
            ...q,
            available: response.data.logged_in || q.quality <= 80
          }))
          
          // 设置默认清晰度（选择最高可用清晰度）
          const defaultQuality = availableQualities.value.find(q => q.available)?.quality || 80
          qualityForm.quality = defaultQuality
          qualityForm.savePath = ''
          
          // 设置选中的视频信息
          selectedVideoForDownload.value = {
            ...result,
            title: response.data.title,
            duration: response.data.duration
          }
          
          // 显示清晰度选择对话框
          showQualityDialog.value = true
        } else {
          ElMessage.error(response.data.message || '获取视频信息失败')
        }
      } catch (error) {
        console.error('获取视频信息失败:', error)
        ElMessage.error('获取视频信息失败，请重试')
      }
    }
    
    // 确认下载（带清晰度选择）
    const confirmDownloadWithQuality = async () => {
      if (!selectedVideoForDownload.value || !qualityForm.quality) {
        ElMessage.warning('请选择清晰度')
        return
      }
      
      downloadingVideo.value = true
      try {
        const response = await axios.post('/api/bilibili/video/download', {
          video_url: selectedVideoForDownload.value.url,
          quality: qualityForm.quality,
          save_path: qualityForm.savePath || ''
        })
        
        if (response.data.success) {
          ElMessage.success('下载任务已启动！')
          
          // 添加任务到下载列表
          const newTask = {
            id: response.data.task_id,
            title: selectedVideoForDownload.value.title || '未知视频',
            status: 'pending',
            progress: 0,
            quality: qualityForm.quality,
            url: selectedVideoForDownload.value.url
          }
          downloadTasks.value.push(newTask)
          
          // 关闭对话框
          showQualityDialog.value = false
        } else {
          ElMessage.error(response.data.message || '启动下载失败')
        }
      } catch (error) {
        console.error('启动下载失败:', error)
        ElMessage.error('启动下载失败，请重试')
      } finally {
        downloadingVideo.value = false
      }
    }

    // 下载任务管理方法
    const getTaskStatusText = (task) => {
      switch (task.status) {
        case 'downloading': return '下载中'
        case 'completed': return '已完成'
        case 'error': return '下载失败'
        case 'cancelled': return '已取消'
        case 'pending': return '等待中'
        default: return '未知状态'
      }
    }
    
    const getProgressStatus = (status) => {
      switch (status) {
        case 'completed': return 'success'
        case 'error': return 'exception'
        case 'cancelled': return 'warning'
        default: return ''
      }
    }
    

    
    const retryDownload = (task) => {
      // 重试下载
      axios.post('/api/retry-download', { task_id: task.id })
        .then(response => {
          if (response.data.success) {
            ElMessage.success('重试下载已开始')
          }
        })
        .catch(error => {
          console.error('重试下载失败:', error)
          ElMessage.error('重试下载失败')
        })
    }
    
    const cancelDownload = (task) => {
      // 取消下载
      ElMessageBox.confirm(
        '确定要取消这个下载任务吗？此操作不可恢复。',
        '确认取消',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      ).then(() => {
        axios.post('/api/bilibili/video/download/cancel', { task_id: task.id })
          .then(response => {
            if (response.data.success) {
              ElMessage.success('下载任务已取消')
              // 从任务列表中移除
              const taskIndex = downloadTasks.value.findIndex(t => t.id === task.id)
              if (taskIndex !== -1) {
                downloadTasks.value.splice(taskIndex, 1)
              }
            }
          })
          .catch(error => {
            console.error('取消下载失败:', error)
            ElMessage.error('取消下载失败')
          })
      }).catch(() => {
        // 用户取消操作
      })
    }
    
    // 格式化函数
    const formatSpeed = (speed) => {
      if (typeof speed === 'string') return speed
      if (!speed || speed === 0) return '0 B/s'
      
      const units = ['B/s', 'KB/s', 'MB/s', 'GB/s']
      let size = speed
      let unitIndex = 0
      
      while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024
        unitIndex++
      }
      
      return `${size.toFixed(1)} ${units[unitIndex]}`
    }
    
    const formatFileSize = (bytes) => {
      if (!bytes || bytes === 0) return '0 B'
      
      const units = ['B', 'KB', 'MB', 'GB', 'TB']
      let size = bytes
      let unitIndex = 0
      
      while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024
        unitIndex++
      }
      
      return `${size.toFixed(1)} ${units[unitIndex]}`
    }
    
    const getQualityName = (qualityCode) => {
      const qualityMap = {
        '16': '流畅 360P',
        '32': '清晰 480P',
        '64': '高清 720P',
        '74': '高清 720P60',
        '80': '超清 1080P',
        '112': '超清 1080P+',
        '116': '超清 1080P60',
        '120': '超清 4K',
        '125': 'HDR真彩',
        '126': '杜比视界',
        '127': '超高清 8K'
      }
      return qualityMap[String(qualityCode)] || `清晰度${qualityCode}`
    }
    
    const formatTime = (seconds) => {
      if (typeof seconds === 'string') return seconds
      if (!seconds || seconds === 0) return '0秒'
      
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = Math.floor(seconds % 60)
      
      if (hours > 0) {
        return `${hours}小时${minutes}分钟`
      } else if (minutes > 0) {
        return `${minutes}分钟${secs}秒`
      } else {
        return `${secs}秒`
      }
    }
    
    // 音视频合并功能
    const mergeVideoAudio = async (task) => {
      try {
        ElMessage.info('开始合并音视频文件...')
        
        const response = await axios.post('/api/bilibili/video/merge', {
          task_id: task.id,
          video_path: task.video_path,
          audio_path: task.audio_path,
          output_path: task.file_path
        })
        
        if (response.data.success) {
          ElMessage.success('音视频合并完成！')
          // 更新任务状态
          const taskIndex = downloadTasks.value.findIndex(t => t.id === task.id)
          if (taskIndex !== -1) {
            downloadTasks.value[taskIndex].status = 'completed'
            downloadTasks.value[taskIndex].message = '合并完成'
          }
        } else {
          ElMessage.error(`合并失败: ${response.data.message}`)
        }
      } catch (error) {
        console.error('合并音视频失败:', error)
        ElMessage.error('合并音视频失败，请检查文件是否存在')
      }
    }
    
    // 批量下载功能
    const startBatchDownload = async () => {
      if (!batchDownloadForm.urls.trim()) {
        ElMessage.warning('请输入视频链接')
        return
      }
      
      const urls = batchDownloadForm.urls.split('\n').filter(url => url.trim())
      if (urls.length === 0) {
        ElMessage.warning('请输入有效的视频链接')
        return
      }
      
      batchDownloading.value = true
      
      try {
        const response = await axios.post('/api/bilibili/video/download/batch', {
          urls: urls,
          quality: batchDownloadForm.defaultQuality,
          save_path: batchDownloadForm.savePath,
          max_concurrent: downloadSettings.maxConcurrent,
          auto_retry: downloadSettings.autoRetry,
          retry_count: downloadSettings.retryCount
        })
        
        if (response.data.success) {
          // 添加成功创建的任务到下载任务列表
          response.data.task_ids.forEach((taskId, index) => {
            const url = urls[index]
            downloadTasks.value.push({
              id: taskId,
              title: `批量下载 - ${url.substring(0, 50)}...`,
              url: url,
              quality: batchDownloadForm.defaultQuality,
              status: 'pending',
              progress: 0,
              message: '等待开始下载',
              type: 'bilibili'
            })
          })
          
          ElMessage.success(response.data.message)
          
          // 如果有失败的URL，显示详细信息
          if (response.data.failed_urls.length > 0) {
            console.warn('以下URL创建任务失败:', response.data.failed_urls)
          }
          
          showVideoDownloadDialog.value = false
        } else {
          ElMessage.error(response.data.message)
        }
        
      } catch (error) {
        console.error('批量下载失败:', error)
        ElMessage.error('批量下载启动失败')
      } finally {
        batchDownloading.value = false
      }
    }
    
    // 保存下载设置
    const saveDownloadSettings = () => {
      try {
        // 保存到本地存储
        localStorage.setItem('downloadSettings', JSON.stringify(downloadSettings))
        ElMessage.success('下载设置已保存')
      } catch (error) {
        console.error('保存设置失败:', error)
        ElMessage.error('保存设置失败')
      }
    }
    
    // 加载下载设置
    const loadDownloadSettings = () => {
      try {
        const saved = localStorage.getItem('downloadSettings')
        if (saved) {
          const settings = JSON.parse(saved)
          Object.assign(downloadSettings, settings)
        }
      } catch (error) {
        console.error('加载设置失败:', error)
      }
    }
    
    // Socket.IO 连接管理
    const initSocket = () => {
      socket.value = io('http://localhost:5000')
      
      socket.value.on('connect', () => {
        console.log('Socket.IO 连接成功')
      })
      
      socket.value.on('disconnect', () => {
        console.log('Socket.IO 连接断开')
      })
      
      socket.value.on('download_progress', (data) => {
         const taskIndex = downloadTasks.value.findIndex(task => task.id === data.task_id)
         if (taskIndex !== -1) {
           downloadTasks.value[taskIndex] = {
             ...downloadTasks.value[taskIndex],
             progress: data.progress,
             speed: data.speed,
             eta: data.eta,
             file_type: data.file_type
           }
         }
       })
       
       socket.value.on('download_status', (data) => {
         const taskIndex = downloadTasks.value.findIndex(task => task.id === data.task_id)
         if (taskIndex !== -1) {
           downloadTasks.value[taskIndex] = {
             ...downloadTasks.value[taskIndex],
             status: data.status,
             message: data.message,
             ...data
           }
           
           if (data.status === 'completed') {
             downloadTasks.value[taskIndex].progress = 100
             ElMessage.success(`下载完成: ${data.title}`)
           } else if (data.status === 'failed') {
             ElMessage.error(`下载失败: ${data.message}`)
           }
         }
       })
    }
    
    const disconnectSocket = () => {
      if (socket.value) {
        socket.value.disconnect()
        socket.value = null
      }
    }
    
    // 监听爬虫类型切换，清空结果
    watch(selectedSpider, (newSpider, oldSpider) => {
      if (oldSpider && newSpider !== oldSpider) {
        results.value = []
        expandedResults.value = []
        currentPage.value = 1
        executionTime.value = 0
        successRate.value = 0
      }
    })
    
    // 生命周期
    onMounted(async () => {
      await loadSpiders()
      await checkBilibiliLoginStatus()
      loadDownloadSettings()
      initSocket()
    })
    
    onUnmounted(() => {
      disconnectSocket()
    })
    
    return {
      // 响应式数据
      selectedSpider,
      isExecuting,
      hasExecuted,
      results,
      displayedKeyword,
      tasks,
      expandedResults,
      currentPage,
      pageSize,
      executionTime,
      spiders,
      baiduParams,
      bilibiliParams,
      csdnParams,
      urlParams,
      bilibiliLogin,
      showVideoDownloadDialog,
      gettingVideoInfo,
      downloadingVideo,
      videoInfo,
      videoDownloadForm,
      exportFormats,
      
      // 计算属性
      canExecute,
      currentKeyword,
      paginatedResults,
      totalPages,
      successRate,
      
      // Socket.IO 相关
      socket,
      downloadTasks,
      isTasksMinimized,
      
      // 方法
      executeCrawl,
      exportResults,
      toggleResultDetail,
      handlePageChange,
      isBaiduResult,
      isBilibiliResult,
      isCSDNResult,
      handleCountChange,
      checkCrawlCount,
      getTaskStatusType,
      getTaskStatusLabel,
      truncateText,
      handleImageError,
      formatContent,
      checkBilibiliLoginStatus,
      showBilibiliLogin,
      getBilibiliQRCode,
      startLoginPolling,
      bilibiliLogout,
      closeBilibiliLoginDialog,
      getVideoInfo,
      downloadVideo,
      downloadBilibiliVideo,
      confirmDownloadWithQuality,
      getTaskStatusText,
      getProgressStatus,
      cancelDownload,
      retryDownload,
      
      // 清晰度选择相关
      showQualityDialog,
      selectedVideoForDownload,
      availableQualities,
      qualityForm,
      
      // 增强下载对话框相关
      downloadDialogActiveTab,
      batchDownloading,
      batchDownloadForm,
      downloadSettings,
      startBatchDownload,
      saveDownloadSettings,
      loadDownloadSettings,
      
      // 格式化函数
      formatSpeed,
      formatFileSize,
      formatTime,
      getQualityName,
      truncateKeyword,
      handleCountChange,
      previewImage,
      
      // 音视频合并功能
      mergeVideoAudio,
      cancelDownload
    }
  }
}
</script>

<style scoped>
.crawler-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #fff5f0 0%, #ffe4e1 25%, #ffd1dc 50%, #f8bbd9 75%, #e6a8d0 100%);
  min-height: 100vh;
}

.crawler-header {
  text-align: center;
  margin-bottom: 3rem;
}

.crawler-header h1 {
  font-size: 3.2rem;
  font-weight: 900;
  background: linear-gradient(135deg, #c299be 0%, #d4a4c8 30%, #e6a8d0 70%, #f8bbd9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
  text-shadow: 0 5px 25px rgba(194, 153, 190, 0.4);
}

.subtitle {
  font-size: 1.2rem;
  color: #6b4c6b;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6);
  margin: 0;
}

.crawler-content {
  background: rgba(255, 250, 245, 0.95);
  backdrop-filter: blur(25px);
  border: 2px solid rgba(248, 187, 208, 0.4);
  border-radius: 24px;
  padding: 2rem;
  box-shadow: 0 15px 35px rgba(248, 187, 208, 0.25);
}

.spider-selection {
  margin-bottom: 2rem;
}

.spider-selection h2 {
  color: #8b5a83;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  text-shadow: 0 1px 3px rgba(255, 255, 255, 0.8);
}

.spider-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.spider-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-shadow: 0 5px 15px rgba(255, 182, 193, 0.2);
}

.spider-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(248, 187, 208, 0.3);
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(248, 187, 208, 0.5);
}

.spider-card.active {
  border-color: #f8bbd9;
  background: linear-gradient(135deg, #f8bbd9 0%, #e6a8d0 100%);
  color: white;
  box-shadow: 0 8px 20px rgba(248, 187, 208, 0.4);
}

.spider-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.spider-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.3rem;
}

.spider-card p {
  margin: 0 0 1rem 0;
  opacity: 0.8;
  line-height: 1.5;
}

.spider-features {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.feature-tag {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  backdrop-filter: blur(10px);
}

.spider-card.active .feature-tag {
  background: rgba(255, 255, 255, 0.3);
}

.parameter-section {
  margin-bottom: 2rem;
}

.parameter-section h2 {
  color: #8b5a83;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  text-shadow: 0 1px 3px rgba(255, 255, 255, 0.8);
}

.parameter-form {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 5px 15px rgba(255, 182, 193, 0.2);
}

.action-section {
  text-align: center;
  margin: 2rem 0;
}

.execute-btn {
  padding: 1rem 3rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 25px;
  background: linear-gradient(135deg, #f8bbd9 0%, #e6a8d0 100%);
  border: none;
  color: white;
  box-shadow: 0 8px 20px rgba(248, 187, 208, 0.3);
  transition: all 0.3s ease;
}

.execute-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(248, 187, 208, 0.5);
  background: linear-gradient(135deg, #e6a8d0 0%, #d4a4c8 100%);
}

/* 零结果提示区域 */
.no-results-section {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.no-results-content {
  text-align: center;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(248, 187, 208, 0.3);
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(248, 187, 208, 0.2);
  max-width: 500px;
}

.no-results-content h3 {
  color: #8b5a83;
  margin: 1rem 0;
  font-size: 1.5rem;
}

.no-results-content p {
  color: #6b4c6b;
  margin: 1rem 0 0.5rem 0;
  font-weight: 600;
}

.no-results-content ul {
  text-align: left;
  color: #6b4c6b;
  margin: 0.5rem 0 1rem 0;
  padding-left: 1.5rem;
}

.no-results-content li {
  margin: 0.25rem 0;
}

.results-section {
  margin-top: 2rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.results-header h2 {
  color: #8b5a83;
  margin: 0;
  font-size: 1.5rem;
  text-shadow: 0 1px 3px rgba(255, 255, 255, 0.8);
}

.export-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* 导出按钮美化样式 */
.export-btn {
  background: linear-gradient(135deg, #f8bbd0 0%, #f48fb1 100%);
  border: 1px solid rgba(244, 143, 177, 0.3);
  border-radius: 8px;
  color: #8b5a83;
  font-weight: 600;
  padding: 8px 16px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(244, 143, 177, 0.2);
}

.export-btn:hover {
  background: linear-gradient(135deg, #f48fb1 0%, #f06292 100%);
  border-color: rgba(240, 98, 146, 0.5);
  color: #6d1b7b;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(244, 143, 177, 0.4);
}

.export-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(244, 143, 177, 0.3);
}

/* 下载按钮美化样式 */
.download-btn {
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  padding: 8px 16px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
  display: flex;
  align-items: center;
  gap: 4px;
}

.download-btn:hover {
  background: linear-gradient(135deg, #45a049 0%, #3d8b40 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
}

.download-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

/* 清晰度选择对话框样式 */
.quality-selection-content {
  padding: 10px 0;
}

.video-info-preview {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.video-info-preview h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.video-meta {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.login-tip {
  margin-top: 15px;
}

/* 下载进度增强样式 */
.speed-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  flex-wrap: wrap;
  gap: 8px;
}

.speed-text {
  color: #409eff;
  font-weight: 500;
}

.size-text {
  color: #67c23a;
}

.eta-text {
  color: #e6a23c;
}

.file-type-text {
  color: #f56c6c;
  font-weight: 500;
  background: #fef0f0;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
}

.task-progress {
  flex: 1;
  margin: 0 15px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-text {
  font-size: 14px;
  color: #606266;
}

.progress-percent {
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
}

/* 展开/收起按钮美化样式 */
.toggle-btn {
  background: linear-gradient(135deg, #e1bee7 0%, #ce93d8 100%);
  border: 1px solid rgba(206, 147, 216, 0.3);
  border-radius: 6px;
  color: #7b1fa2;
  font-weight: 500;
  padding: 4px 12px;
  transition: all 0.3s ease;
  box-shadow: 0 1px 4px rgba(206, 147, 216, 0.2);
}

.toggle-btn:hover {
  background: linear-gradient(135deg, #ce93d8 0%, #ba68c8 100%);
  border-color: rgba(186, 104, 200, 0.5);
  color: #4a148c;
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(206, 147, 216, 0.4);
}

.toggle-btn:active {
  transform: translateY(0);
  box-shadow: 0 1px 4px rgba(206, 147, 216, 0.3);
}

.results-stats {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(248, 187, 208, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 5px 15px rgba(255, 182, 193, 0.2);
}

.results-stats-header {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.results-list {
  space-y: 1rem;
}

.result-item {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(248, 187, 208, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 3px 10px rgba(255, 182, 193, 0.15);
}

.result-item:hover {
  box-shadow: 0 8px 25px rgba(248, 187, 208, 0.25);
  border-color: rgba(248, 187, 208, 0.5);
  transform: translateY(-2px);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.result-index {
  background: linear-gradient(135deg, #f8bbd9 0%, #e6a8d0 100%);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-weight: 600;
  font-size: 0.9rem;
  box-shadow: 0 2px 8px rgba(248, 187, 208, 0.3);
}

.result-type {
  background: rgba(248, 187, 208, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.9rem;
  color: #8b5a83;
  border: 1px solid rgba(248, 187, 208, 0.3);
}

/* 结果图片预览 */
.result-preview {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}



.result-content {
  flex: 1;
  min-width: 0;
}

.result-preview h4 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.1rem;
  line-height: 1.4;
}

.result-description {
  color: #666;
  line-height: 1.6;
  margin: 0 0 1rem 0;
}

.url-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  max-width: 100%;
  overflow: hidden;
}

.url-meta .el-link {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}

.result-detail {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e0e0e0;
}

.bilibili-detail,
.csdn-detail {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 6px;
}

.detail-label {
  font-weight: 600;
  color: #333;
  min-width: 80px;
}

.detail-value {
  color: #666;
  flex: 1;
}

.content-section,
.images-section,
.metadata-section {
  margin-bottom: 1.5rem;
}

.content-section h5,
.images-section h5,
.metadata-section h5 {
  color: #333;
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.content-text {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  line-height: 1.6;
  color: #555;
}

.content-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.images-section-title {
  font-weight: 600;
  color: #333;
  margin: 1rem 0 0.5rem 0;
}

.content-link {
  color: #6c757d;
  text-decoration: none;
}

.content-link:hover {
  text-decoration: underline;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
}

.image-item {
  border-radius: 8px;
  overflow: hidden;
  background: #f0f0f0;
  aspect-ratio: 1;
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.image-item img:hover {
  transform: scale(1.05);
}

.metadata-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

.metadata-item {
  background: #f8f9fa;
  padding: 0.75rem;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metadata-key {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
}

.metadata-value {
  color: #666;
  font-size: 0.9rem;
  word-break: break-word;
}

/* URL详情特殊样式 */
.url-detail {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 1rem;
}

.url-full-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.url-metadata h4,
.url-full-text h4,
.url-images h4,
.url-tech-metadata h4 {
  color: #333;
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 0.5rem;
}

.url-metadata {
  margin-bottom: 1.5rem;
}

.url-metadata .metadata-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.url-metadata .metadata-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.url-metadata .label {
  font-weight: bold;
  color: #666;
  min-width: 80px;
}

.url-metadata .value {
  color: #333;
  word-break: break-all;
}

.url-link {
  color: #409eff;
  text-decoration: none;
}

.url-link:hover {
  text-decoration: underline;
}

.url-full-text {
  margin-bottom: 1.5rem;
}

.full-text-content {
  background: white;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
  font-family: 'Arial', sans-serif;
}

.url-images {
  margin-bottom: 1.5rem;
}

.url-images .images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.url-images .image-item {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}

.url-images .image-item:hover {
  transform: translateY(-2px);
}

.url-images .image-item img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  cursor: pointer;
}

.image-url {
  padding: 0.5rem;
  text-align: center;
}

.image-link {
  color: #409eff;
  text-decoration: none;
  font-size: 0.9rem;
}

.image-link:hover {
  text-decoration: underline;
}

.url-tech-metadata {
  margin-bottom: 1rem;
}

.tech-metadata-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.tech-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.tech-item .label {
  font-weight: bold;
  color: #666;
  min-width: 80px;
}

.tech-item .value {
  color: #333;
  word-break: break-all;
}

.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.tasks-section {
  margin-top: 2rem;
}

.tasks-section h2 {
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.tasks-list {
  space-y: 1rem;
}

.task-item {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 1rem;
  display: grid;
  grid-template-columns: 1fr auto 200px;
  gap: 1rem;
  align-items: center;
}

.task-info {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.task-id {
  background: #6c757d;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-weight: 600;
  font-size: 0.9rem;
}

.task-type {
  background: #f0f0f0;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.9rem;
  color: #666;
}

.task-keyword {
  color: #333;
  font-weight: 500;
}

@media (max-width: 1200px) {
  .spider-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 900px) {
  .spider-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .crawler-header h1 {
    font-size: 2rem;
  }
  
  .spider-grid {
    grid-template-columns: 1fr;
  }
  
  .results-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .export-buttons {
    justify-content: center;
  }
  
  .url-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .results-stats-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

/* B站登录相关样式 */
.bilibili-login-status {
  margin-bottom: 1.5rem;
}

.login-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 1px solid rgba(108, 117, 125, 0.2);
}

/* 用户信息卡片样式 */
.user-info-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
}

.user-avatar-section {
  position: relative;
  flex-shrink: 0;
}

.user-avatar {
  border: 3px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.vip-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  z-index: 1;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name-section {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.username {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.level-tag {
  background: linear-gradient(45deg, #ff6b6b, #ffa726);
  color: white;
  border: none;
}

.user-uid {
  margin-bottom: 0.25rem;
}

.user-uid .el-icon {
  margin-right: 0.25rem;
}

.user-status {
  margin-bottom: 0;
}

.user-actions {
  flex-shrink: 0;
}

/* 未登录状态样式 */
.not-logged-in {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  margin-bottom: 0.5rem;
}

.login-prompt {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.login-icon {
  font-size: 2rem;
  color: #6c757d;
}

.login-text h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  color: #333;
}

.login-text p {
  margin: 0;
  font-size: 0.9rem;
  color: #666;
}

.login-btn {
  padding: 0.75rem 1.5rem;
  font-weight: 600;
}

.login-note {
  text-align: center;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 6px;
  margin-top: 0.5rem;
}

.login-note .el-icon {
  margin-right: 0.25rem;
}

/* B站登录对话框样式 */
.login-dialog-content {
  text-align: center;
}

.qr-code-section {
  padding: 1rem;
}

.qr-code-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
}

.qr-code-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  margin-bottom: 1rem;
}

.qr-code-img {
  width: 180px;
  height: 180px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
}

.qr-code-loading {
  color: #666;
  font-size: 1rem;
}

.qr-code-tips {
  color: #666;
}

/* 视频下载对话框样式 */
.download-dialog-content {
  padding: 1rem 0;
}

.video-info-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
}

.video-info-section .el-form-item {
  margin-bottom: 1rem;
}

.video-info-section .el-form-item:last-child {
  margin-bottom: 0;
}

/* 下载任务管理样式 */
.download-tasks-section {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 400px;
  max-height: 500px;
  z-index: 1000;
}

.download-tasks-card {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-radius: 12px;
  overflow: hidden;
}

.download-tasks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.download-tasks-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
}

.download-tasks-list {
  max-height: 400px;
  overflow-y: auto;
}

.download-task-item {
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.3s ease;
}

.download-task-item:last-child {
  border-bottom: none;
}

.download-task-item:hover {
  background-color: #f8f9fa;
}

.task-info {
  margin-bottom: 0.75rem;
}

.task-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
}

.task-title span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-number {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  min-width: 2rem;
  text-align: center;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
  flex-shrink: 0;
}

.task-meta {
  display: flex;
  gap: 0.75rem;
  font-size: 0.8rem;
  color: #666;
}

.task-id {
  background: #e3f2fd;
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  color: #495057;
}

.task-quality {
  background: #f3e5f5;
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  color: #6c757d;
}

.task-progress {
  margin-bottom: 0.75rem;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
}

.progress-text {
  color: #666;
  font-weight: 500;
}

.progress-percent {
  color: #333;
  font-weight: 600;
}

.speed-info {
  display: flex;
  justify-content: space-between;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #888;
}

.task-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.task-actions .el-button {
  padding: 0.25rem 0.75rem;
  font-size: 0.8rem;
}

@media (max-width: 768px) {
  .download-tasks-section {
    position: relative;
    bottom: auto;
    right: auto;
    width: 100%;
    margin-top: 2rem;
  }
}

.count-warning {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
  color: #856404;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
</style>