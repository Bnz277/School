# 智能网络爬虫平台

一个基于 Python Flask 和 Vue.js 开发的现代化网络爬虫平台，支持多平台数据采集、B站视频下载和多格式数据导出，具备实时进度显示和后台下载能力。

## 🚀 项目特性

### 🎯 v3.1.1 最新特性
- **下载按钮优化**：调整B站爬取结果页面下载按钮位置和样式，更加突出和美观
- **清晰度界面改进**：移除登录提示文字，隐藏保存路径输入框，简化用户操作
- **BV号显示**：在清晰度选择界面显示BV号而不是"未知作者"，提供更准确的视频标识
- **导出格式修复**：修正前端导出格式定义，确保与后端API完全匹配
- **文档更新**：更新所有.md文档以反映最新功能变更

### 🎯 v3.1 历史特性
- **清晰度显示优化**：在清晰度选择时显示文件大小（如10.3GB或832.62MB）
- **下载控制改进**：将下载任务的暂停功能改为取消功能
- **清晰度名称显示**：下载任务界面显示清晰度名称而不是数字（如"超清 1080P"而非"80"）
- **任务界面优化**：添加下载任务界面最小化功能和任务编号（实时更新）
- **界面简化**：移除下载任务界面的"已连接"状态显示
- **用户体验提升**：更直观的任务管理和状态显示

### 🔧 核心功能
- **多平台支持**：支持百度搜索、B站视频、CSDN文章、自定义URL爬取
- **B站视频下载**：支持B站登录、视频信息获取、多清晰度下载
- **多格式导出**：支持 JSON、CSV、TXT、Markdown 格式导出
- **智能识别**：自动识别网页结构和数据类型
- **温馨设计**：采用柔和暖色调，提供舒适的视觉体验
- **现代化UI**：毛玻璃效果、渐变色彩、流畅动画
- **智能交互**：实时反馈、状态指示、用户友好的操作流程
- **实时监控**：实时显示爬取进度和状态
- **稳定可靠**：多重错误处理机制，确保任务稳定执行
- **响应式设计**：支持桌面端和移动端的完美适配，一行显示4个爬虫选项
- **快捷操作**：支持回车键快速触发爬取任务
- **易于部署**：支持宝塔面板一键部署，简化运维流程
- **图片预览**：B站和CSDN爬取结果支持图片预览功能
- **智能提示**：零结果时提供反爬机制和关键词优化建议
- **精确统计**：修复成功率计算，显示真实的爬取效果

## 📋 目录结构

```
nylg/
├── app.py                 # Flask 后端主程序
├── requirements.txt       # Python 依赖
├── spiders/              # 爬虫模块
│   ├── __init__.py
│   ├── baidu_spider.py   # 百度搜索爬虫
│   ├── bilibili_spider.py # B站视频爬虫
│   ├── csdn_spider.py    # CSDN文章爬虫
│   └── url_spider.py     # 通用URL爬虫
├── utils/                # 工具模块
│   ├── __init__.py
│   ├── data_processor.py # 数据处理
│   └── export_utils.py   # 导出工具
├── frontend/             # 前端项目
│   ├── vue/             # Vue 3 前端
│   │   ├── package.json
│   │   ├── vite.config.js
│   │   ├── index.html
│   │   └── src/
│   │       ├── main.js
│   │       ├── App.vue
│   │       ├── router/
│   │       ├── views/
│   │       └── style/
│   └── static/          # 原版静态文件（备用）
└── README.md            # 项目文档
```

## 🛠️ 技术栈

### 后端
- **Python 3.9+**
- **Flask** - Web 框架
- **BeautifulSoup4** - HTML 解析
- **Requests** - HTTP 请求
- **Flask-CORS** - 跨域支持

### 前端
- **Vue.js 3** - 渐进式JavaScript框架，组合式API
- **Element Plus** - Vue 3组件库，丰富的UI组件
- **Vue Router** - 单页面应用路由管理
- **Axios** - 基于Promise的HTTP客户端
- **Vite** - 下一代前端构建工具，快速热重载
- **CSS3** - 现代化样式，渐变、动画、毛玻璃效果

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- 现代浏览器（Chrome、Firefox、Safari、Edge）

### 本地开发安装

#### 1. 克隆项目
```bash
git clone <repository-url>
cd nylg
```

#### 2. 后端设置
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 前端设置
```bash
cd frontend/vue
npm install
```

#### 4. 启动服务

**开发模式（推荐）**：
```bash
# 终端1：启动后端服务
python app.py

# 终端2：启动前端开发服务器
cd frontend/vue
npm run dev
```

**生产模式**：
```bash
# 构建前端
cd frontend/vue
npm run build

# 启动后端（前端通过后端提供）
python app.py
```

### 🌐 生产环境部署

#### 宝塔面板部署
详细部署指南请参考：
- 📋 **部署清单**：[宝塔部署清单.md](宝塔部署清单.md)
- 📖 **详细指南**：[宝塔部署详细指南.md](宝塔部署详细指南.md)

#### 快速部署步骤
1. **构建前端**：`npm run build`
2. **准备文件**：上传必需文件到服务器
3. **安装依赖**：`pip install -r requirements.txt`
4. **配置服务**：设置Python项目和Nginx代理

#### 部署文件清单
```
必需文件：
├── app.py + requirements.txt     # 后端核心
├── 测试/ (爬虫模块)              # 爬虫功能
└── frontend/vue/dist/           # 前端构建文件

总大小：~50-105MB
```

## 📦 详细部署指南

## 🏗️ 宝塔面板部署

### 1. 环境准备

确保服务器已安装：
- 宝塔面板 7.0+
- Python 3.9+
- Node.js 16+
- Nginx

### 2. 后端部署

1. **上传项目文件**
   - 将项目文件上传到服务器（如 `/www/wwwroot/nylg/`）

2. **安装Python依赖**
```bash
cd /www/wwwroot/nylg
pip3 install -r requirements.txt
```

3. **创建Python项目**
   - 在宝塔面板中进入「Python项目管理」
   - 点击「添加Python项目」
   - 设置项目名称：`nylg-backend`
   - 设置项目路径：`/www/wwwroot/nylg`
   - 设置启动文件：`app.py`
   - 设置端口：`5000`
   - Python版本：选择 3.9+

4. **启动项目**
   - 点击「启动」按钮启动后端服务

### 3. 前端部署

1. **构建前端项目**
```bash
cd /www/wwwroot/nylg/frontend/vue
npm install
npm run build
```

2. **创建网站**
   - 在宝塔面板中进入「网站」
   - 点击「添加站点」
   - 域名：填写您的域名
   - 根目录：`/www/wwwroot/nylg/frontend/vue/dist`

3. **配置Nginx反向代理**
   - 点击网站设置
   - 进入「配置文件」
   - 添加以下配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /www/wwwroot/nylg/frontend/vue/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }
    
    # API反向代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

4. **重载Nginx配置**
```bash
nginx -s reload
```

### 4. SSL证书配置（可选）

1. 在宝塔面板中进入网站设置
2. 点击「SSL」选项卡
3. 选择「Let's Encrypt」免费证书或上传自有证书
4. 开启「强制HTTPS」

### 5. 进程守护

为确保服务稳定运行，建议使用 PM2 管理 Python 进程：

1. **安装PM2**
```bash
npm install -g pm2
```

2. **创建PM2配置文件** (`ecosystem.config.js`)
```javascript
module.exports = {
  apps: [{
    name: 'nylg-backend',
    script: 'app.py',
    interpreter: 'python3',
    cwd: '/www/wwwroot/nylg',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    }
  }]
}
```

3. **启动PM2**
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## 🔧 配置说明

### 后端配置

在 `app.py` 中可以修改以下配置：

```python
# 服务器配置
HOST = '0.0.0.0'  # 监听地址
PORT = 5000       # 监听端口
DEBUG = False     # 生产环境设为 False

# 爬虫配置
DEFAULT_TIMEOUT = 10    # 请求超时时间
MAX_RESULTS = 100       # 最大结果数量（推荐20条以内）
REQUEST_DELAY = 1       # 请求间隔（秒）
```

### 前端配置

在 `frontend/vue/vite.config.js` 中可以修改：

```javascript
export default defineConfig({
  server: {
    port: 3000,  // 开发服务器端口
    proxy: {
      '/api': {
        target: 'http://localhost:5000',  // 后端API地址
        changeOrigin: true
      }
    }
  }
})
```

## 🎨 界面预览

项目采用温馨柔和的现代化Web界面设计，具有以下特点：
- 🎨 **温馨配色**: 采用粉色系暖色调，营造舒适的使用环境
- 💎 **毛玻璃效果**: 现代化的视觉设计，层次分明
- 📱 **响应式布局**: 完美支持桌面、平板和移动设备
- 🎯 **直观操作**: 清晰的步骤指引和状态反馈
- 📊 **智能表格**: 中文字段显示、序号排序、点击链接访问
- ✨ **流畅动画**: 悬停效果、过渡动画提升用户体验
- 🔍 **实时状态**: 爬取进度、结果统计、时间显示
- 🎨 **美化导出**: 精美的导出按钮设计，支持JSON/CSV格式
- 🔧 **功能完善**: 修复网页爬取功能，优化数据显示格式

## 📖 使用指南

### 1. 百度搜索爬虫

- **功能**：爬取百度搜索结果
- **参数**：
  - 搜索关键词：要搜索的内容
  - 搜索类型：网页搜索或图片搜索
  - 结果数量：1-100条（推荐20条以内，超过20条准确率可能下降）
- **返回数据**：标题、链接、描述、图片URL等

### 2. B站视频爬虫

- **功能**：爬取B站视频信息 + 增强视频下载系统
- **参数**：
  - 搜索关键词：视频相关关键词
  - 结果数量：1-100条（推荐20条以内，超过20条准确率可能下降）
- **返回数据**：视频标题、作者、播放量、时长、链接等
- **增强视频下载功能**：
  - 🔐 **B站登录**：扫码登录获取高清视频权限
  - 📱 **二维码登录**：使用B站APP扫码快速登录
  - 🎬 **清晰度选择**：支持多种清晰度选择（480P-4K）
  - 📦 **批量下载**：支持多个视频链接批量下载
  - 🔄 **音视频合并**：自动下载并合并视频音频文件
  - 📊 **下载进度**：实时显示下载进度和状态
  - 📋 **任务管理**：完整的下载任务管理界面
  - ⚙️ **下载设置**：可配置并发数、重试次数等参数
  - 🔧 **手动合并**：支持下载失败后手动触发音视频合并
  - 💾 **本地存储**：下载文件保存到服务器downloads目录
  - ⚡ **实时状态**：显示下载进度和状态反馈

### 3. CSDN文章爬虫

- **功能**：爬取CSDN技术文章
- **参数**：
  - 搜索关键词：技术相关关键词
  - 结果数量：1-100条（推荐20条以内，超过20条准确率可能下降）
- **返回数据**：文章标题、作者、发布时间、阅读量、链接等

### 4. 网页爬取

- **功能**：爬取指定URL的网页内容，智能识别数据类型，同时提取图片信息
- **参数**：
  - 目标URL：要爬取的网页地址（支持HTTP/HTTPS协议）
- **返回数据**：
  - 网页标题和完整文本内容
  - 图片列表（包含描述和链接）
  - 完整内容长度统计
  - 爬取时间记录
  - 自动识别网页编码
- **特色功能**：
  - 智能提取文本内容，保持原有格式
  - 自动识别和提取网页中的所有图片
  - 完整内容展示，支持折叠/展开功能
  - 图片信息美化显示，包含描述和链接

## 🔧 最新更新

### v3.1.2 (最新)
- 📊 **导出功能优化**: 修改导出功能为直接导出爬取结果数据，而不是爬虫工具页面
- 🗂️ **界面简化**: 移除B站视频下载完成后的打开文件夹按钮，简化用户界面
- 💾 **数据导出增强**: 支持JSON、CSV、TXT、Markdown格式的本地数据导出
- 🎯 **用户体验提升**: 优化导出流程，提供更直观的数据导出体验

### v3.0.0
- 🎬 **B站视频下载增强**: 全面升级B站视频下载功能
- 🎯 **清晰度选择**: 支持多种清晰度选择和预览
- 📦 **批量下载**: 支持多个视频链接批量下载
- 🔄 **音视频合并**: 智能下载并自动合并音视频文件
- 📊 **下载进度**: 实时显示下载进度和状态
- 📋 **任务管理**: 完整的下载任务管理界面
- ⚙️ **下载设置**: 可配置并发数、重试次数等参数
- 🔧 **手动合并**: 支持下载失败后手动触发音视频合并
- 🔐 **B站登录支持**: 二维码扫码登录，获取高清视频权限
- 💾 **本地文件管理**: 下载文件自动保存到downloads目录

### v2.4.0
- 🎬 **B站视频下载功能**: 全新集成B站视频下载系统
- 🔐 **B站登录支持**: 二维码扫码登录，获取高清视频权限
- 📱 **优化二维码显示**: 修复二维码显示问题，使用外部生成服务
- 🎯 **多清晰度选择**: 支持480P到4K多种清晰度下载
- 🔄 **自动音视频合并**: 智能下载并合并音视频文件
- ⚡ **修复加载状态**: 优化视频信息获取的loading状态管理
- 💾 **本地文件管理**: 下载文件自动保存到downloads目录

### v2.2.2 (最新)
- 🏷️ **关键词显示**: 在结果统计界面添加当前搜索关键词显示
- 🔄 **智能清空**: 切换爬虫类型时自动清空上次的爬取结果
- 📖 **URL展开**: 自定义URL爬取结果默认为展开状态，便于查看详情
- 🎯 **用户体验优化**: 提升操作流畅性和信息展示的直观性

### v2.3.0
- 🎨 **UI全面圆角化**: 所有界面元素采用圆角设计，提升视觉体验
- 📖 **内容完整展示**: 移除折叠功能，网页内容直接完整显示
- 🧹 **代码优化**: 简化组件结构，移除冗余代码和样式
- ⚡ **性能提升**: 减少不必要的响应式绑定和DOM操作

### v2.2.1
- 🐛 **展开功能修复**: 修复网页内容无法展开的响应式更新问题
- ⚡ **性能优化**: 改进Vue 3响应式属性绑定机制
- 🔧 **稳定性提升**: 增强内容展开/收起功能的可靠性

### v2.2.0
- 🖼️ **图片爬取功能**: 网页爬取时自动提取所有图片信息
- 📖 **完整内容展示**: 移除内容长度限制，支持完全展开显示
- 🎨 **内容格式优化**: 美化图片信息显示，增加图标和样式
- 📱 **响应式改进**: 优化移动端内容展示效果
- 🔗 **链接识别增强**: 智能识别并美化显示网页中的链接

### v2.1.0 功能优化

- ✅ **修复网页爬取功能**：解决URL爬取无响应问题，优化数据格式
- 🎨 **美化导出按钮**：重新设计导出按钮样式，提升用户体验
- 📊 **优化表格显示**：改进字段映射，隐藏冗余信息
- 🔍 **智能内容提取**：增强网页内容识别和格式化能力
- 📝 **完善文档系统**：更新使用指南和技术文档

## 🔌 API 接口

### 爬取接口

**POST** `/api/crawl`

**请求参数：**
```json
{
  "spider_type": "baidu|bilibili|csdn|url",
  "task_type": "search|url",
  "keyword": "搜索关键词",
  "url": "目标URL",
  "count": 10,
  "search_type": "web|image"
}
```

**响应格式：**
```json
{
  "success": true,
  "message": "爬取成功",
  "task_id": "任务ID",
  "results": [
    {
      "title": "标题",
      "url": "链接",
      "description": "描述"
    }
  ]
}
```

### B站视频相关接口

#### 获取登录二维码
**GET** `/api/bilibili/login/qr`

**响应格式：**
```json
{
  "qr_url": "二维码图片URL",
  "qrcode_key": "二维码密钥",
  "login_url": "原始登录URL"
}
```

#### 轮询登录状态
**POST** `/api/bilibili/login/poll`

**请求参数：**
```json
{
  "qrcode_key": "二维码密钥"
}
```

#### 获取视频信息
**POST** `/api/bilibili/video/info`

**请求参数：**
```json
{
  "video_url": "B站视频URL"
}
```

#### 下载视频
**POST** `/api/bilibili/video/download`

**请求参数：**
```json
{
  "video_url": "B站视频URL",
  "quality": "720"
}
```

#### 批量下载视频
**POST** `/api/bilibili/video/download/batch`

**请求参数：**
```json
{
  "urls": ["视频URL1", "视频URL2"],
  "quality": "720",
  "save_path": "保存路径（可选）",
  "max_concurrent": 3,
  "auto_retry": true,
  "retry_count": 3
}
```

#### 手动合并音视频
**POST** `/api/bilibili/video/merge`

**请求参数：**
```json
{
  "task_id": "任务ID",
  "video_path": "视频文件路径（可选）",
  "audio_path": "音频文件路径（可选）",
  "output_path": "输出文件路径（可选）"
}
```

#### 获取下载任务状态
**GET** `/api/bilibili/video/download/status/<task_id>`

#### 获取所有下载任务
**GET** `/api/bilibili/video/download/tasks`

### 导出接口

**POST** `/api/export`

**请求参数：**
```json
{
  "format": "json|csv|txt|markdown",
  "data": [...],
  "filename": "导出文件名"
}
```

## 🐛 常见问题

### Q: 爬取失败怎么办？
A: 请检查网络连接、参数设置是否正确，某些网站可能有反爬虫机制。

### Q: 支持哪些网站？
A: 目前支持百度、B站、CSDN和自定义URL爬取，后续会增加更多平台。

### Q: 数据量有限制吗？
A: 单次爬取最多100条数据，推荐20条以内以保证准确率，如需更多数据请分批爬取。

### Q: 如何提高爬取成功率？
A: 建议设置合理的爬取间隔，避免频繁请求，使用准确的关键词。

### Q: 部署后无法访问API？
A: 检查防火墙设置，确保5000端口已开放，Nginx配置正确。

### Q: B站登录二维码不显示？
A: 检查网络连接，确保可以访问外部二维码生成服务，或尝试刷新二维码。

### Q: B站视频下载失败？
A: 确认已登录B站账号，检查视频URL是否正确，部分视频可能需要大会员权限。

### Q: 下载的视频在哪里？
A: 视频文件保存在服务器的 `downloads` 目录下，文件名格式为：`视频标题_清晰度.mp4`。

### Q: 为什么有些清晰度选项不可用？
A: 高清晰度（1080P及以上）通常需要B站大会员权限，请确保登录的账号有相应权限。

## 📝 更新日志

### v2.0.0 (2024-01-XX)
- 🎉 全新Vue 3前端界面
- ✨ 新增Markdown导出格式
- 🎨 现代化UI设计
- 🔧 优化API接口
- 📱 响应式设计支持

### v1.0.0 (2024-01-XX)
- 🎉 项目初始版本
- 🕷️ 支持多平台爬虫
- 📊 多格式数据导出
- 🖥️ 基础Web界面

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- 邮箱：support@example.com
- GitHub：[项目地址](https://github.com/your-repo)
- 文档：[在线文档](https://your-docs-site.com)

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！