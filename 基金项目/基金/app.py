# -*- coding: utf-8 -*-
"""
模块说明:
    Flask 应用工厂与路由注册
    - 统一注册 API 蓝图（/api/*）
    - 提供前端入口路由（/ 与 /* 兜底）
    - 集成 Socket.IO 并允许跨域
"""

import os
from flask import Flask, render_template
from flask_cors import CORS

from extensions import socketio
from api.crawl import api_bp
from api.bilibili import bili_bp
from api.stats import stats_bp


def create_app() -> Flask:
    """
    创建并配置 Flask 应用
    Returns:
        Flask: 应用实例
    """
    # 模板/静态目录: 统一指向 src/frontend/vue/dist 内部，彻底剥离 src 以外目录依赖
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), 'frontend', 'vue', 'dist'),
        static_folder=os.path.join(os.path.dirname(__file__), 'frontend', 'vue', 'dist'),
    )
    CORS(app)

    # 初始化 Socket.IO
    socketio.init_app(app, cors_allowed_origins="*")

    # 注册蓝图
    app.register_blueprint(api_bp)
    app.register_blueprint(bili_bp)
    app.register_blueprint(stats_bp)

    # 前端入口
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/<path:path>')
    def spa_fallback(path: str):
        if path.startswith('assets/') or path.endswith(('.js', '.css', '.png', '.jpg', '.ico', '.svg')):
            return app.send_static_file(path)
        return render_template('index.html')

    return app


# 供外部启动器导入
app = create_app()
if __name__ == '__main__':
    os.makedirs(os.path.join(os.path.dirname(__file__), 'crawler_results'), exist_ok=True)
    app = create_app()
    print("🚀 启动网络信息爬取系统...")
    print("📱 前端界面: http://localhost:5000")
    print("🔧 API文档: http://localhost:5000/api")
    print("\n按 Ctrl+C 停止服务")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)