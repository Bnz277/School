#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NYLG爬虫系统 - 宝塔部署文件准备脚本
自动创建部署包，包含所有必需文件
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_deployment_package():
    """
    创建宝塔部署包
    """
    print("🚀 开始准备NYLG爬虫系统部署文件...")
    
    # 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 创建部署目录
    deploy_dir = os.path.join(project_root, 'nylg-deploy')
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    os.makedirs(deploy_dir)
    
    print(f"📁 部署目录: {deploy_dir}")
    
    # 必需文件列表
    required_files = [
        'app.py',
        'requirements.txt',
        'README.md',
        '宝塔部署清单.md',
        '宝塔部署详细指南.md'
    ]
    
    # 复制必需文件
    print("\n📋 复制核心文件:")
    for file in required_files:
        src = os.path.join(project_root, file)
        if os.path.exists(src):
            dst = os.path.join(deploy_dir, file)
            shutil.copy2(src, dst)
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (文件不存在)")
    
    # 复制爬虫模块
    print("\n🕷️ 复制爬虫模块:")
    spider_src = os.path.join(project_root, '测试')
    spider_dst = os.path.join(deploy_dir, '测试')
    if os.path.exists(spider_src):
        shutil.copytree(spider_src, spider_dst, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        spider_files = ['baidu.py', 'bilibili.py', 'csdn.py', 'url.py']
        for spider_file in spider_files:
            if os.path.exists(os.path.join(spider_dst, spider_file)):
                print(f"  ✅ 测试/{spider_file}")
            else:
                print(f"  ❌ 测试/{spider_file} (文件不存在)")
    else:
        print("  ❌ 测试/ 目录不存在")
    
    # 复制前端构建文件
    print("\n🎨 复制前端构建文件:")
    frontend_src = os.path.join(project_root, 'frontend', 'vue', 'dist')
    frontend_dst = os.path.join(deploy_dir, 'frontend', 'vue', 'dist')
    if os.path.exists(frontend_src):
        os.makedirs(os.path.dirname(frontend_dst), exist_ok=True)
        shutil.copytree(frontend_src, frontend_dst)
        print(f"  ✅ frontend/vue/dist/ (构建文件)")
        
        # 检查关键文件
        key_files = ['index.html', 'assets']
        for key_file in key_files:
            if os.path.exists(os.path.join(frontend_dst, key_file)):
                print(f"    ✅ {key_file}")
            else:
                print(f"    ❌ {key_file} (缺失)")
    else:
        print("  ❌ frontend/vue/dist/ 目录不存在")
        print("     请先运行: cd frontend/vue && npm run build")
    
    # 创建部署说明文件
    print("\n📝 创建部署说明:")
    deploy_readme = os.path.join(deploy_dir, '部署说明.txt')
    with open(deploy_readme, 'w', encoding='utf-8') as f:
        f.write(f"""NYLG爬虫系统 - 宝塔部署包
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📦 部署文件说明:
├── app.py                    # Flask主应用
├── requirements.txt          # Python依赖
├── 测试/                     # 爬虫模块
│   ├── baidu.py             # 百度爬虫
│   ├── bilibili.py          # B站爬虫
│   ├── csdn.py              # CSDN爬虫
│   └── url.py               # URL爬虫
├── frontend/vue/dist/        # 前端构建文件
├── README.md                # 项目说明
├── 宝塔部署清单.md           # 部署清单
├── 宝塔部署详细指南.md       # 详细指南
└── 部署说明.txt             # 本文件

🚀 快速部署步骤:
1. 上传所有文件到服务器 /www/wwwroot/nylg/
2. 安装Python依赖: pip install -r requirements.txt
3. 配置Python项目: 端口5000, 启动文件app.py
4. 配置Nginx: 静态文件指向dist目录, API代理到5000端口
5. 启动服务并测试

📖 详细说明请参考: 宝塔部署详细指南.md
""")
    print(f"  ✅ 部署说明.txt")
    
    # 创建ZIP压缩包
    print("\n📦 创建压缩包:")
    zip_name = f"nylg-deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"
    zip_path = os.path.join(project_root, zip_name)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, deploy_dir)
                zipf.write(file_path, arc_name)
    
    print(f"  ✅ {zip_name}")
    
    # 计算文件大小
    def get_size(path):
        if os.path.isfile(path):
            return os.path.getsize(path)
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                total += os.path.getsize(os.path.join(dirpath, filename))
        return total
    
    deploy_size = get_size(deploy_dir)
    zip_size = get_size(zip_path)
    
    print(f"\n📊 文件大小统计:")
    print(f"  📁 部署文件夹: {deploy_size / 1024 / 1024:.1f} MB")
    print(f"  📦 压缩包: {zip_size / 1024 / 1024:.1f} MB")
    
    print(f"\n🎉 部署文件准备完成!")
    print(f"\n📂 部署文件夹: {deploy_dir}")
    print(f"📦 压缩包: {zip_path}")
    print(f"\n💡 建议:")
    print(f"  1. 上传压缩包到宝塔面板")
    print(f"  2. 解压到 /www/wwwroot/nylg/")
    print(f"  3. 按照'宝塔部署详细指南.md'进行配置")
    
    return zip_path

def check_prerequisites():
    """
    检查部署前置条件
    """
    print("🔍 检查部署前置条件...")
    
    issues = []
    
    # 检查必需文件
    required_files = ['app.py', '测试/baidu.py', '测试/bilibili.py', '测试/csdn.py', '测试/url.py']
    for file in required_files:
        if not os.path.exists(file):
            issues.append(f"缺少文件: {file}")
    
    # 检查前端构建
    if not os.path.exists('frontend/vue/dist/index.html'):
        issues.append("前端未构建，请运行: cd frontend/vue && npm run build")
    
    # 检查requirements.txt
    if not os.path.exists('requirements.txt'):
        issues.append("缺少requirements.txt文件")
    
    if issues:
        print("\n❌ 发现以下问题:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n请解决上述问题后重新运行脚本。")
        return False
    else:
        print("✅ 所有前置条件满足")
        return True

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 NYLG爬虫系统 - 宝塔部署文件准备工具")
    print("=" * 60)
    
    if check_prerequisites():
        try:
            zip_path = create_deployment_package()
            print("\n" + "=" * 60)
            print("🎉 部署文件准备成功!")
            print("=" * 60)
        except Exception as e:
            print(f"\n❌ 准备部署文件时出错: {e}")
    else:
        print("\n❌ 部署文件准备失败")
    
    input("\n按回车键退出...")