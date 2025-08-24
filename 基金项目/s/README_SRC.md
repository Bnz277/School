# NYLG 爬虫项目 - 独立运行版本

本文件夹包含了NYLG爬虫项目的所有核心文件，可以独立运行整个项目。

## 🚀 快速启动

### 1. 安装依赖
```bash
cd src
pip install -r requirements.txt
```

### 2. 启动项目
```bash
# 使用默认配置启动 (端口5000)
python run.py

# 自定义端口启动
python run.py --port 8080

# 启用调试模式
python run.py --debug

# 自定义主机和端口
python run.py --host 127.0.0.1 --port 3000
```

### 3. 访问项目
启动成功后，在浏览器中访问：
- 主页: http://localhost:5000
- 爬虫工具: http://localhost:5000/crawler
- 文档页面: http://localhost:5000/docs
- 关于页面: http://localhost:5000/about

## 📁 文件结构

```
src/
├── run.py                 # 项目启动脚本
├── app.py                 # Flask主应用
├── crawler_main.py        # 爬虫核心逻辑
├── requirements.txt       # Python依赖
├── frontend/              # 前端文件
│   ├── vue/              # Vue.js前端项目
│   ├── static/           # 静态资源
│   └── templates/        # HTML模板
├── static/               # 构建后的静态文件
├── crawler_results/      # 爬取结果存储
├── downloads/            # 下载文件存储
└── __pycache__/         # Python缓存文件
```

## 🔧 开发说明

### 前端开发
如需修改前端界面，请进入 `frontend/vue/` 目录：
```bash
cd frontend/vue
npm install
npm run dev    # 开发模式
npm run build  # 构建生产版本
```

### 后端开发
- 主要逻辑在 `app.py` 中
- 爬虫功能在 `crawler_main.py` 中
- 修改后直接运行 `python run.py` 即可

## 📝 注意事项

1. **工作目录**: 启动脚本会自动设置工作目录为src文件夹
2. **路径问题**: 所有相对路径都基于src文件夹
3. **依赖安装**: 确保在src目录下安装依赖
4. **端口冲突**: 如果5000端口被占用，请使用 `--port` 参数指定其他端口

## 🆘 常见问题

### Q: 启动时提示模块找不到
A: 确保在src目录下运行，并且已安装所有依赖：
```bash
cd src
pip install -r requirements.txt
```

### Q: 前端页面显示异常
A: 检查static文件夹是否存在，如果缺失请重新构建前端：
```bash
cd frontend/vue
npm run build
```

### Q: B站下载功能异常
A: 确保downloads文件夹存在且有写入权限

---

✨ **现在您可以完全独立地运行这个src文件夹中的项目了！**