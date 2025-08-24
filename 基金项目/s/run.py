#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目启动脚本
从src文件夹直接运行整个NYLG爬虫项目

使用方法:
    python run.py
    
或者:
    python run.py --port 5000
"""

import os
import sys
import argparse
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# 设置工作目录为src文件夹
# os.chdir(current_dir)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='NYLG爬虫项目启动器')
    parser.add_argument('--port', '-p', type=int, default=5000, help='服务器端口号 (默认: 5000)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='服务器主机地址 (默认: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    print(f"🚀 启动NYLG爬虫项目...")
    print(f"📁 工作目录: {current_dir}")
    print(f"🌐 服务器地址: http://{args.host}:{args.port}")
    print(f"🔧 调试模式: {'开启' if args.debug else '关闭'}")
    print("-" * 50)
    
    try:
        # 为了导入 src 包，加入项目根目录到 sys.path
        project_root = current_dir.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        # 将工作目录切换到项目根目录，确保下载目录/前端资源路径一致
        os.chdir(project_root)
        # 导入并运行Flask应用（来自 src.app）
        from src.app import app
        from src.extensions import socketio
        app.run(host=args.host, port=args.port, debug=args.debug)
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖已安装: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()