#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块说明:
    NYLG 项目 src 内部独立启动器
    - 只依赖 src 目录内容即可运行
    - 通过 Socket.IO 启动，支持进度推送
用法:
    python src/run.py
    python src/run.py --port 5000 --host 0.0.0.0 --debug
"""

import os
import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='NYLG 爬虫项目启动器')
    parser.add_argument('--port', '-p', type=int, default=5000, help='服务器端口号 (默认: 5000)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='服务器主机地址 (默认: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    args = parser.parse_args()

    current_dir = Path(__file__).parent.absolute()
    # 切换工作目录至 src，确保下载目录/前端dist路径全部在 src 下
    os.chdir(current_dir)

    # 将项目根路径与 src 路径均加入 sys.path，确保相对导入稳定
    project_root = current_dir.parent
    for p in (project_root, current_dir):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))

    print("🚀 启动 NYLG 爬虫项目")
    print(f"📁 工作目录: {current_dir}")
    print(f"🌐 服务器地址: http://{args.host}:{args.port}")
    print(f"🔧 调试模式: {'开启' if args.debug else '关闭'}")
    print("-" * 50)

    try:
        from app import app
        from extensions import socketio
        socketio.run(app, host=args.host, port=args.port, debug=args.debug, allow_unsafe_werkzeug=True)
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保依赖已安装: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()