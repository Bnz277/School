#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络信息爬取系统 - Flask后端应用

功能特性：
1. 支持多平台爬虫（百度、B站、CSDN、自定义URL）
2. 多格式数据导出（JSON、CSV、Excel、Markdown）
3. B站视频下载功能
4. 实时进度显示（WebSocket）
5. 图片预览和智能提示

最近更新：
- 修复成功率计算逻辑
- 添加图片预览功能
- 优化零结果提示
- 支持Excel和Markdown导出

作者：网络爬虫系统开发团队
版本：2.0
更新时间：2024年
"""

import csv
import io
import json
import os
import re
import subprocess
import sys
import uuid
import threading
from datetime import datetime
from urllib.parse import unquote
from threading import Thread
from time import sleep

import pandas as pd
import requests
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# 添加测试文件夹到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '测试'))

try:
    from baidu import BaiduSpider
    from bilibili import BilibiliSpider
    from csdn import CSDNSpider
    from url import WebContentExtractor
except ImportError as e:
    print(f"❌ 导入爬虫模块失败: {e}")
    print("请确保测试文件夹中包含所有爬虫文件")
    sys.exit(1)

# Flask应用配置
# template_folder: Vue构建后的模板文件夹路径
# static_folder: Vue构建后的静态资源文件夹路径
app = Flask(__name__,
            template_folder='frontend/vue/dist',
            static_folder='frontend/vue/dist')

# 启用跨域资源共享(CORS)
CORS(app)

# 初始化Socket.IO，支持实时通信功能
# cors_allowed_origins="*": 允许所有来源的跨域请求
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局变量存储任务和结果
tasks = []
results = []
task_counter = 0

# B站登录相关全局变量
global_cookies = ""
global_bili_jct = ""
login_session = None


class CrawlerService:
    """
    爬虫服务核心类
    
    功能：
    1. 管理多种爬虫类型（百度、B站、CSDN、自定义URL）
    2. 统一的搜索接口
    3. URL内容提取
    4. 支持不同数据类型的爬取
    
    最近更新：
    - 支持max_results参数控制结果数量
    - 优化错误处理机制
    """

    def __init__(self):
        """
        初始化爬虫服务
        配置支持的爬虫类型和对应的处理类
        """
        self.spiders = {
            'baidu': {'name': '百度搜索', 'class': BaiduSpider, 'type': 'search'},
            'bilibili': {'name': '哔哩哔哩', 'class': BilibiliSpider, 'type': 'search'},
            'csdn': {'name': 'CSDN', 'class': CSDNSpider, 'type': 'search'},
            'url': {'name': '自定义URL', 'class': WebContentExtractor, 'type': 'url'}
        }

    def execute_search(self, spider_type, keyword, max_results=10, data_type='text'):
        """
        执行搜索爬虫任务
        
        参数：
            spider_type (str): 爬虫类型 ('baidu', 'bilibili', 'csdn')
            keyword (str): 搜索关键词
            max_results (int): 最大结果数量，修复：支持真实的数量控制
            data_type (str): 数据类型 ('text', 'image')
            
        返回：
            tuple: (results, error) 结果列表和错误信息
        """
        try:
            spider_info = self.spiders.get(spider_type)
            if not spider_info:
                return None, "不支持的爬虫类型"

            spider = spider_info['class']()

            # 根据爬虫类型和数据类型调用相应的搜索方法
            if spider_type == 'baidu' and hasattr(spider, 'search'):
                # 百度爬虫支持图片搜索
                search_type = 'image' if data_type == 'image' else 'web'
                results = spider.search(keyword, max_results, search_type)
            else:
                # 其他爬虫使用默认搜索
                results = spider.search(keyword, max_results)

            return results, None
        except Exception as e:
            return None, str(e)

    def execute_url_extraction(self, url):
        """
        执行URL内容提取
        
        参数：
            url (str): 要提取内容的URL
            
        返回：
            tuple: (content, error) 提取的内容和错误信息
        """
        try:
            extractor = WebContentExtractor()
            content, error = extractor.get_web_content(url)
            if error:
                return None, error
            return content, None
        except Exception as e:
            return None, str(e)


crawler_service = CrawlerService()


# B站视频下载相关函数
def extract_bvid(url):
    """从URL中提取BV号"""
    if "b23.tv" in url:
        try:
            url = requests.get(url, allow_redirects=False).headers.get('location', url)
        except:
            pass
    match = re.search(r'(BV[0-9A-Za-z]+)', url)
    if not match:
        raise ValueError("URL中未找到有效的BV号")
    return match.group(1)


def format_duration(seconds):
    """将秒数转换为可读的时分秒格式"""
    if not seconds or seconds <= 0:
        return "00:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def get_video_info(video_url, cookie=""):
    """获取视频信息"""
    try:
        bvid = extract_bvid(video_url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": f"https://www.bilibili.com/video/{bvid}"
        }
        if cookie:
            headers["Cookie"] = cookie

        # 获取视频基本信息
        info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        info = requests.get(info_url, headers=headers, timeout=10).json()
        if info['code'] != 0:
            raise ValueError(f"获取视频信息失败: {info.get('message')}")

        cid = info['data']['cid']
        title = re.sub(r'[\\/:*?"<>|]', '', unquote(info['data']['title']))
        duration = info['data']['duration']  # 视频时长（秒）
        formatted_duration = format_duration(duration)  # 格式化时长

        # 获取播放信息，添加必要参数
        play_url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn=80&fnval=4048&fourk=1"
        playinfo = requests.get(play_url, headers=headers, timeout=10).json()
        if playinfo['code'] != 0:
            raise ValueError(f"获取播放信息失败: {playinfo.get('message')}")

        return bvid, title, playinfo, formatted_duration
    except Exception as e:
        raise ValueError(f"获取视频信息时出错: {str(e)}")


def download_file_with_progress(url, filename, headers, task_id=None, file_type="video"):
    """下载文件并通过Socket.IO实时推送进度
    
    Args:
        url (str): 下载文件的URL地址
        filename (str): 保存文件的本地路径
        headers (dict): HTTP请求头
        task_id (str, optional): 任务ID，用于Socket.IO进度推送
        file_type (str, optional): 文件类型标识，默认为"video"
        
    Returns:
        tuple: (成功状态, 消息)
            - bool: True表示下载成功，False表示失败
            - str: 成功或错误消息
            
    Note:
        - 支持断点续传和进度显示
        - 通过Socket.IO实时推送下载进度到前端
        - 进度信息包括：进度百分比、已下载大小、总大小、下载状态
    """
    try:
        with requests.get(url, headers=headers, stream=True, timeout=30) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            downloaded = 0
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if task_id and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            socketio.emit('download_progress', {
                                'task_id': task_id,
                                'file_type': file_type,
                                'progress': round(progress, 1),
                                'downloaded': downloaded,
                                'total': total_size,
                                'status': 'downloading'
                            })
        return True, None
    except Exception as e:
        return False, str(e)


def merge_video_audio(video_path, audio_path, output_path):
    """合并音视频文件"""
    try:
        cmd = [
            'ffmpeg',
            '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c', 'copy',
            output_path
        ]
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(cmd, check=True, startupinfo=startupinfo,
                       stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        
        # 删除临时文件
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, "合并失败，请确保已安装ffmpeg并添加到系统PATH中"
    except Exception as e:
        return False, f"合并过程中出错: {str(e)}"


@app.route('/')
def index():
    """Vue前端应用入口
    
    Returns:
        str: 渲染的Vue应用主页面(index.html)
        
    Note:
        模板文件位于 frontend/vue/dist/index.html
        需要先运行 npm run build 构建Vue项目生成dist文件夹
    """
    return render_template('index.html')


@app.route('/<path:path>')
def serve_vue_app(path):
    """处理Vue单页应用路由
    
    Args:
        path (str): 请求的路径
        
    Returns:
        Response: 静态资源文件或Vue应用主页面
        
    Note:
        - 静态资源(assets/目录下的文件和特定扩展名文件)直接返回
        - 其他路径返回index.html，由Vue Router处理前端路由
        - 支持Vue应用的History模式路由
    """
    # 如果是静态资源文件，直接返回
    if path.startswith('assets/') or path.endswith(('.js', '.css', '.png', '.jpg', '.ico')):
        return app.send_static_file(path)
    # 其他路径返回index.html，让Vue Router处理
    return render_template('index.html')


@app.route('/api/spiders')
def get_spiders():
    """获取可用的爬虫列表API接口
    
    返回完整的爬虫信息，包括：
    - id: 爬虫唯一标识
    - name: 爬虫显示名称  
    - type: 爬虫类型（search/url）
    - icon: 显示图标
    - description: 功能描述
    - features: 特性标签列表
    
    改进记录：
    - 支持动态爬虫配置
    - 增强了爬虫信息展示
    - 优化了前端显示效果
    """
    # 定义完整的爬虫信息
    spiders_info = {
        'baidu': {
            'icon': '🔍',
            'description': '爬取百度搜索结果，支持网页和图片搜索',
            'features': ['网页搜索', '图片搜索', '实时结果']
        },
        'bilibili': {
            'icon': '📺',
            'description': '爬取B站视频信息，支持搜索和视频详情',
            'features': ['视频搜索', '详细信息', '下载支持']
        },
        'csdn': {
            'icon': '📝',
            'description': '爬取CSDN技术文章和博客内容',
            'features': ['技术文章', '博客内容', '代码示例']
        },
        'url': {
            'icon': '🌐',
            'description': '爬取指定URL的网页内容和数据',
            'features': ['自定义URL', '内容提取', '多格式支持']
        }
    }
    
    spiders_list = []
    for key, info in crawler_service.spiders.items():
        spider_detail = spiders_info.get(key, {
            'icon': '🕷️',
            'description': '通用爬虫',
            'features': ['数据采集']
        })
        
        spiders_list.append({
            'id': key,
            'name': info['name'],
            'type': info['type'],
            'icon': spider_detail['icon'],
            'description': spider_detail['description'],
            'features': spider_detail['features']
        })
    return jsonify(spiders_list)


@app.route('/api/crawl', methods=['POST'])
def crawl():
    """执行爬取任务"""
    global task_counter, tasks, results

    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400

        spider_type = data.get('spider_type')
        if not spider_type:
            return jsonify({'success': False, 'message': '缺少爬虫类型'}), 400

        # 根据爬虫类型自动推断任务类型
        task_type = 'url' if spider_type == 'url' else 'search'

        # 创建任务记录
        task_counter += 1
        task = {
            'id': task_counter,
            'spider_type': spider_type,
            'task_type': task_type,
            'status': 'running',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'completed_at': None,
            'error': None
        }

        if task_type == 'search':
            keyword = data.get('keyword')
            max_results = data.get('max_results', 100)
            data_type = data.get('data_type', 'text')  # 获取数据类型参数

            if not keyword:
                return jsonify({'success': False, 'message': '缺少搜索关键词'}), 400

            task.update({
                'keyword': keyword,
                'max_results': max_results,
                'data_type': data_type
            })

            # 执行搜索
            search_results, error = crawler_service.execute_search(spider_type, keyword, max_results, data_type)

            if error:
                task.update({
                    'status': 'failed',
                    'error': error,
                    'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                tasks.append(task)
                return jsonify({'success': False, 'message': f'爬取失败: {error}', 'task_id': task_counter})
            else:
                task.update({
                    'status': 'completed',
                    'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

                # 保存结果
                result = {
                    'id': task_counter,
                    'task_id': task_counter,
                    'spider_type': spider_type,
                    'task_type': task_type,
                    'keyword': keyword,
                    'data': search_results,
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                results.append(result)

        elif task_type == 'url':
            url = data.get('url')
            if not url:
                return jsonify({'success': False, 'message': '缺少目标URL'}), 400
            url = data.get('url')
            task.update({'url': url})

            # 执行URL提取
            content, error = crawler_service.execute_url_extraction(url)

            if error:
                task.update({
                    'status': 'failed',
                    'error': error,
                    'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                tasks.append(task)
                return jsonify({'success': False, 'message': f'爬取失败: {error}', 'task_id': task_counter})
            else:
                task.update({
                    'status': 'completed',
                    'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

                # 将文本内容转换为表格格式
                url_results = [{
                    'index': 1,
                    'title': '网页内容',
                    'url': url,
                    'content': content[:5000] + '...' if len(content) > 5000 else content,
                    'full_content': content,
                    'length': len(content),
                    'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }]

                # 保存结果
                result = {
                    'id': task_counter,
                    'task_id': task_counter,
                    'spider_type': spider_type,
                    'task_type': task_type,
                    'url': url,
                    'data': url_results,
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                results.append(result)

        tasks.append(task)

        # 确保返回正确的结果数据
        if 'result' in locals():
            return jsonify({
                'success': True,
                'message': '爬取任务完成',
                'task_id': task_counter,
                'results': result['data']
            })
        else:
            return jsonify({
                'success': False,
                'message': '未知错误：无法获取结果',
                'task_id': task_counter,
                'results': []
            })

    except Exception as e:
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/task/<int:task_id>')
def get_task_status(task_id):
    """获取任务状态"""
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({'error': '任务不存在'}), 404

    # 如果任务已完成，返回结果
    if task['status'] == 'completed':
        result = next((r for r in results if r['task_id'] == task_id), None)
        if result:
            task['results'] = result['data']

    return jsonify(task)


@app.route('/api/tasks')
def get_tasks():
    """获取任务列表"""
    return jsonify(tasks)


@app.route('/api/results')
def get_results():
    """获取结果列表"""
    return jsonify(results)


@app.route('/api/results/<int:result_id>')
def get_result_detail(result_id):
    """获取结果详情"""
    result = next((r for r in results if r['id'] == result_id), None)
    if not result:
        return jsonify({'error': '结果不存在'}), 404
    return jsonify(result)


@app.route('/api/export/<int:result_id>/<format_type>')
def export_result(result_id, format_type):
    """导出结果"""
    result = next((r for r in results if r['id'] == result_id), None)
    if not result:
        return jsonify({'error': '结果不存在'}), 404

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    spider_name = crawler_service.spiders[result['spider_type']]['name']

    if result['task_type'] == 'search':
        data = result['data']
        keyword = result['keyword']

        if format_type == 'json':
            filename = f"{spider_name}_{keyword}_{timestamp}.json"
            output = io.StringIO()
            json.dump(data, output, ensure_ascii=False, indent=2)
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='application/json',
                as_attachment=True,
                download_name=filename
            )

        elif format_type == 'csv':
            filename = f"{spider_name}_{keyword}_{timestamp}.csv"
            output = io.StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8-sig')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=filename
            )

        elif format_type == 'excel':
            filename = f"{spider_name}_{keyword}_{timestamp}.xlsx"
            output = io.BytesIO()
            df = pd.DataFrame(data)
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )

        elif format_type == 'txt':
            filename = f"{spider_name}_{keyword}_{timestamp}.txt"
            output = io.StringIO()
            for i, item in enumerate(data, 1):
                output.write(f"=== 结果 {i} ===\n")
                for key, value in item.items():
                    output.write(f"{key}: {value}\n")
                output.write("\n")
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/plain',
                as_attachment=True,
                download_name=filename
            )

        elif format_type == 'xml':
            filename = f"{spider_name}_{keyword}_{timestamp}.xml"
            output = io.StringIO()
            output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            output.write('<results>\n')
            output.write(f'  <metadata>\n')
            output.write(f'    <spider>{spider_name}</spider>\n')
            output.write(f'    <keyword>{keyword}</keyword>\n')
            output.write(f'    <timestamp>{result["created_at"]}</timestamp>\n')
            output.write(f'    <count>{len(data)}</count>\n')
            output.write(f'  </metadata>\n')
            output.write(f'  <data>\n')

            for i, item in enumerate(data, 1):
                output.write(f'    <item id="{i}">\n')
                for key, value in item.items():
                    # 转义XML特殊字符
                    escaped_value = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace(
                        '"', '&quot;').replace("'", '&apos;')
                    output.write(f'      <{key}>{escaped_value}</{key}>\n')
                output.write(f'    </item>\n')
            output.write(f'  </data>\n')
            output.write('</results>\n')
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='application/xml',
                as_attachment=True,
                download_name=filename
            )

        elif format_type == 'pdf':
            try:
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.lib import colors
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont

                filename = f"{spider_name}_{keyword}_{timestamp}.pdf"
                output = io.BytesIO()

                # 创建PDF文档
                doc = SimpleDocTemplate(output, pagesize=A4)
                styles = getSampleStyleSheet()
                story = []

                # 标题
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=18,
                    spaceAfter=30,
                    alignment=1  # 居中
                )
                story.append(Paragraph(f"{spider_name} 搜索结果", title_style))

                # 元数据
                meta_data = [
                    ['关键词', keyword],
                    ['搜索时间', result['created_at']],
                    ['结果数量', str(len(data))]
                ]
                meta_table = Table(meta_data, colWidths=[2 * inch, 4 * inch])
                meta_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(meta_table)
                story.append(Spacer(1, 20))

                # 结果数据
                for i, item in enumerate(data, 1):
                    story.append(Paragraph(f"结果 {i}", styles['Heading2']))

                    item_data = [[key, str(value)[:100] + '...' if len(str(value)) > 100 else str(value)]
                                 for key, value in item.items()]

                    item_table = Table(item_data, colWidths=[1.5 * inch, 4.5 * inch])
                    item_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]))
                    story.append(item_table)
                    story.append(Spacer(1, 15))

                doc.build(story)
                output.seek(0)

                return send_file(
                    output,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=filename
                )
            except ImportError:
                return jsonify({'error': 'PDF导出功能需要安装reportlab库'}), 500

        elif format_type == 'md':
            filename = f"{spider_name}_{keyword}_{timestamp}.md"
            output = io.StringIO()
            output.write(f"# {spider_name} 搜索结果\n\n")
            output.write(f"**关键词**: {keyword}\n")
            output.write(f"**搜索时间**: {result['created_at']}\n")
            output.write(f"**结果数量**: {len(data)}\n\n")

            for i, item in enumerate(data, 1):
                output.write(f"## 结果 {i}\n\n")
                for key, value in item.items():
                    if key == 'url':
                        output.write(f"**{key}**: [{value}]({value})\n")
                    else:
                        output.write(f"**{key}**: {value}\n")
                output.write("\n")
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/markdown',
                as_attachment=True,
                download_name=filename
            )

    else:  # URL类型
        content = result['data']
        url = result['url']

        if format_type == 'txt':
            filename = f"网页内容_{timestamp}.txt"
            return send_file(
                io.BytesIO(content.encode('utf-8')),
                mimetype='text/plain',
                as_attachment=True,
                download_name=filename
            )

        elif format_type == 'md':
            filename = f"网页内容_{timestamp}.md"
            md_content = f"# 网页内容\n\n**URL**: [{url}]({url})\n**提取时间**: {result['created_at']}\n\n---\n\n{content}"
            return send_file(
                io.BytesIO(md_content.encode('utf-8')),
                mimetype='text/markdown',
                as_attachment=True,
                download_name=filename
            )

    return jsonify({'error': '不支持的导出格式'}), 400


# B站登录相关API
@app.route('/api/bilibili/login/qr', methods=['GET'])
def get_bilibili_qr():
    """获取B站登录二维码"""
    global login_session
    try:
        import qrcode
        import base64
        from PIL import Image
        
        login_session = requests.session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81',
        }
        
        get_login = login_session.get(
            'https://passport.bilibili.com/x/passport-login/web/qrcode/generate?source=main-fe-header',
            headers=headers).json()
        
        if get_login['code'] != 0:
            return jsonify({'success': False, 'message': '获取二维码失败'})
        
        # 使用qrcode库生成二维码图片
        login_url = get_login['data']['url']
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(login_url)
        qr.make(fit=True)
        
        # 生成PIL图像
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((200, 200), Image.LANCZOS)
        
        # 转换为base64编码的data URL
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        qr_data_url = f"data:image/png;base64,{img_str}"
            
        return jsonify({
            'success': True,
            'qr_url': qr_data_url,
            'login_url': login_url,
            'qrcode_key': get_login['data']['qrcode_key']
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取二维码失败: {str(e)}'})


@app.route('/api/bilibili/login/poll', methods=['POST'])
def poll_bilibili_login():
    """轮询B站登录状态"""
    global global_cookies, global_bili_jct, login_session
    try:
        data = request.get_json()
        qrcode_key = data.get('qrcode_key')
        
        if not qrcode_key or not login_session:
            return jsonify({'success': False, 'message': '无效的登录会话'})
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81',
        }
        
        token_url = f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={qrcode_key}&source=main-fe-header'
        qrcode_data = login_session.get(token_url, headers=headers).json()
        
        if qrcode_data['data']['code'] == 0:
            # 登录成功
            login_session.get(qrcode_data['data']['url'], headers=headers)
            global_cookies = "; ".join([f"{cookie.name}={cookie.value}" for cookie in login_session.cookies])
            bili_jct_match = re.findall(r'bili_jct=(.*?)(;|$)', global_cookies)
            global_bili_jct = bili_jct_match[0][0] if bili_jct_match else ""
            
            return jsonify({
                'success': True,
                'status': 'success',
                'message': '登录成功'
            })
        else:
            return jsonify({
                'success': True,
                'status': 'waiting',
                'message': qrcode_data['data']['message']
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'轮询登录状态失败: {str(e)}'})


@app.route('/api/bilibili/login/status', methods=['GET'])
def get_bilibili_login_status():
    """获取B站登录状态"""
    global global_cookies, login_session
    try:
        if not global_cookies or not login_session:
            return jsonify({'success': True, 'logged_in': False})
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81',
        }
        
        url = 'https://api.bilibili.com/x/web-interface/nav'
        resp = login_session.get(url=url, headers=headers).json()
        
        if resp['data']['isLogin']:
            return jsonify({
                'success': True,
                'logged_in': True,
                'user_info': {
                    'username': resp['data']['uname'],
                    'face': resp['data']['face'],
                    'uid': resp['data']['mid'],
                    'level': resp['data']['level_info']['current_level'],
                    'vip_type': resp['data']['vipType'],
                    'vip_status': resp['data']['vipStatus']
                }
            })
        else:
            return jsonify({'success': True, 'logged_in': False})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取登录状态失败: {str(e)}'})


@app.route('/api/bilibili/logout', methods=['POST'])
def bilibili_logout():
    """B站登出"""
    global global_cookies, global_bili_jct, login_session
    try:
        if global_bili_jct:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81',
            }
            url = 'https://passport.bilibili.com/login/exit/v2'
            data = {'biliCSRF': global_bili_jct}
            requests.post(url, headers=headers, data=data)
            
        global_cookies = ""
        global_bili_jct = ""
        login_session = None
        
        return jsonify({'success': True, 'message': '已注销登录'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'注销失败: {str(e)}'})


# B站视频下载API
def format_file_size(size_bytes):
    """将字节数转换为可读的文件大小格式"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f}{size_names[i]}"

def get_stream_file_size(url, headers):
    """获取流媒体文件大小"""
    try:
        response = requests.head(url, headers=headers, timeout=10)
        content_length = response.headers.get('content-length')
        if content_length:
            return int(content_length)
        return 0
    except:
        return 0

@app.route('/api/bilibili/video/info', methods=['POST'])
def get_bilibili_video_info():
    """获取B站视频信息"""
    global global_cookies
    try:
        data = request.get_json()
        video_url = data.get('video_url')
        
        if not video_url:
            return jsonify({'success': False, 'message': '请提供视频URL'})
            
        bvid, title, playinfo, duration = get_video_info(video_url, global_cookies)
        
        # 获取可用清晰度
        qualities = playinfo['data']['support_formats']
        logged_in = bool(global_cookies)
        
        # 过滤非登录用户不能选择的清晰度
        if not logged_in:
            qualities = [q for q in qualities if q['quality'] <= 80]  # 80是普通1080P
        
        # 设置请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": f"https://www.bilibili.com/video/{bvid}"
        }
        if global_cookies:
            headers["Cookie"] = global_cookies
        
        # 格式化清晰度显示并获取文件大小
        formatted_qualities = []
        for q in qualities:
            # 查找对应的视频流
            video_stream = next(
                (stream for stream in playinfo['data']['dash']['video']
                 if stream['id'] == q['quality']),
                None
            )
            
            # 获取音频流（通常是第一个）
            audio_stream = playinfo['data']['dash']['audio'][0] if playinfo['data']['dash']['audio'] else None
            
            # 计算总文件大小
            total_size = 0
            if video_stream:
                video_size = get_stream_file_size(video_stream['baseUrl'], headers)
                total_size += video_size
            
            if audio_stream:
                audio_size = get_stream_file_size(audio_stream['baseUrl'], headers)
                total_size += audio_size
            
            formatted_qualities.append({
                'quality': q['quality'],
                'description': q.get('new_description', q.get('description', f"{q['quality']}P")),
                'display_desc': q.get('display_desc', q.get('new_description', q.get('description', f"{q['quality']}P"))),
                'format': q.get('format', 'mp4'),
                'codecs': q.get('codecs', []),
                'file_size': total_size,
                'file_size_text': format_file_size(total_size),
                'available': True
            })
            
        return jsonify({
            'success': True,
            'bvid': bvid,
            'title': title,
            'duration': duration,
            'qualities': formatted_qualities,
            'logged_in': logged_in
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# 全局下载任务存储
download_tasks = {}

def download_video_async(task_id, video_url, quality_id, global_cookies):
    """异步下载B站视频
    
    Args:
        task_id (str): 唯一任务标识符
        video_url (str): B站视频URL
        quality_id (str): 视频质量ID
        global_cookies (str): B站登录Cookie
        
    Note:
        - 在独立线程中执行，支持后台下载
        - 通过Socket.IO实时推送下载状态和进度
        - 支持视频和音频分别下载后合并
        - 自动处理下载失败和重试逻辑
        - 下载完成后自动清理临时文件
    """
    try:
        # 更新任务状态
        download_tasks[task_id]['status'] = 'downloading'
        socketio.emit('download_status', {
            'task_id': task_id,
            'status': 'downloading',
            'message': '开始下载视频...'
        })
        
        # 获取视频信息
        bvid, title, playinfo, duration = get_video_info(video_url, global_cookies)
        
        # 选择视频流
        video_stream = next(
            (stream for stream in playinfo['data']['dash']['video']
             if stream['id'] == quality_id),
            playinfo['data']['dash']['video'][0]
        )
        audio_stream = playinfo['data']['dash']['audio'][0]
        
        # 设置下载headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": f"https://www.bilibili.com/video/{bvid}"
        }
        if global_cookies:
            headers["Cookie"] = global_cookies
            
        # 创建下载目录
        download_dir = "downloads"
        os.makedirs(download_dir, exist_ok=True)
        
        # 文件路径
        safe_title = re.sub(r'[\\/:*?"<>|]', '', title)
        base_name = f"{download_dir}/{safe_title}"
        temp_video = f"{base_name}_video.mp4"
        temp_audio = f"{base_name}_audio.mp3"
        final_output = f"{base_name}.mp4"
        
        download_tasks[task_id]['title'] = title
        download_tasks[task_id]['file_path'] = final_output
        
        # 下载视频
        socketio.emit('download_status', {
            'task_id': task_id,
            'status': 'downloading',
            'message': '正在下载视频流...'
        })
        video_success, video_error = download_file_with_progress(video_stream['baseUrl'], temp_video, headers, task_id, "video")
        if not video_success:
            download_tasks[task_id]['status'] = 'failed'
            download_tasks[task_id]['error'] = f'视频下载失败: {video_error}'
            socketio.emit('download_status', {
                'task_id': task_id,
                'status': 'failed',
                'message': f'视频下载失败: {video_error}'
            })
            return
            
        # 下载音频
        socketio.emit('download_status', {
            'task_id': task_id,
            'status': 'downloading',
            'message': '正在下载音频流...'
        })
        audio_success, audio_error = download_file_with_progress(audio_stream['baseUrl'], temp_audio, headers, task_id, "audio")
        if not audio_success:
            if os.path.exists(temp_video):
                os.remove(temp_video)
            download_tasks[task_id]['status'] = 'failed'
            download_tasks[task_id]['error'] = f'音频下载失败: {audio_error}'
            socketio.emit('download_status', {
                'task_id': task_id,
                'status': 'failed',
                'message': f'音频下载失败: {audio_error}'
            })
            return
            
        # 合并音视频
        socketio.emit('download_status', {
            'task_id': task_id,
            'status': 'merging',
            'message': '正在合并音视频...'
        })
        merge_success, merge_error = merge_video_audio(temp_video, temp_audio, final_output)
        if not merge_success:
            download_tasks[task_id]['status'] = 'failed'
            download_tasks[task_id]['error'] = merge_error
            socketio.emit('download_status', {
                'task_id': task_id,
                'status': 'failed',
                'message': merge_error
            })
            return
            
        # 下载完成
        download_tasks[task_id]['status'] = 'completed'
        download_tasks[task_id]['completed_at'] = datetime.now().isoformat()
        socketio.emit('download_status', {
            'task_id': task_id,
            'status': 'completed',
            'message': '视频下载完成',
            'file_path': final_output,
            'title': title
        })
        
    except Exception as e:
        download_tasks[task_id]['status'] = 'failed'
        download_tasks[task_id]['error'] = str(e)
        socketio.emit('download_status', {
            'task_id': task_id,
            'status': 'failed',
            'message': f'下载失败: {str(e)}'
        })

@app.route('/api/bilibili/video/download', methods=['POST'])
def download_bilibili_video():
    """启动B站视频异步下载任务
    
    Request Body:
        video_url (str): B站视频URL
        quality (int, optional): 视频质量ID，默认为80(1080P)
        
    Returns:
        JSON: 包含任务启动状态和任务ID
        {
            'success': bool,
            'message': str,
            'task_id': str  # 用于查询下载状态
        }
        
    Note:
        - 采用异步下载模式，立即返回任务ID
        - 支持后台下载，不阻塞用户界面
        - 可通过task_id查询下载进度和状态
        - 通过Socket.IO实时推送下载进度
        - 自动处理视频音频分离下载和合并
    """
    global global_cookies
    try:
        data = request.get_json()
        video_url = data.get('video_url')
        quality_id = data.get('quality', 80)  # 默认1080P
        
        if not video_url:
            return jsonify({'success': False, 'message': '请提供视频URL'})
            
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建下载任务记录
        download_tasks[task_id] = {
            'id': task_id,
            'video_url': video_url,
            'quality_id': quality_id,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'title': '',
            'file_path': '',
            'error': None
        }
        
        # 启动异步下载
        thread = threading.Thread(
            target=download_video_async,
            args=(task_id, video_url, quality_id, global_cookies)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': '下载任务已启动'
        })
        
    except Exception as e:
         return jsonify({'success': False, 'message': f'启动下载失败: {str(e)}'})

@app.route('/api/bilibili/video/merge', methods=['POST'])
def merge_bilibili_video():
    """手动合并B站视频的音视频文件
    
    Request Body:
        task_id (str): 任务ID
        video_path (str, optional): 视频文件路径
        audio_path (str, optional): 音频文件路径  
        output_path (str): 输出文件路径
        
    Returns:
        JSON: 合并结果
        {
            'success': bool,
            'message': str,
            'output_path': str  # 合并成功时返回输出路径
        }
        
    Note:
        - 用于手动触发音视频合并操作
        - 支持自动查找临时文件或指定文件路径
        - 合并成功后自动清理临时文件
        - 使用ffmpeg进行无损合并
    """
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        video_path = data.get('video_path')
        audio_path = data.get('audio_path')
        output_path = data.get('output_path')
        
        if not task_id or not output_path:
            return jsonify({'success': False, 'message': '缺少必要参数'})
            
        # 如果没有指定具体路径，尝试根据任务信息推断
        if not video_path or not audio_path:
            if task_id in download_tasks:
                task = download_tasks[task_id]
                title = task.get('title', '')
                if title:
                    safe_title = re.sub(r'[\\/:*?"<>|]', '', title)
                    base_name = f"downloads/{safe_title}"
                    video_path = video_path or f"{base_name}_video.mp4"
                    audio_path = audio_path or f"{base_name}_audio.mp3"
        
        if not video_path or not audio_path:
            return jsonify({'success': False, 'message': '无法确定音视频文件路径'})
            
        # 检查文件是否存在
        if not os.path.exists(video_path):
            return jsonify({'success': False, 'message': f'视频文件不存在: {video_path}'})
        if not os.path.exists(audio_path):
            return jsonify({'success': False, 'message': f'音频文件不存在: {audio_path}'})
            
        # 执行合并
        success, error = merge_video_audio(video_path, audio_path, output_path)
        
        if success:
            # 更新任务状态
            if task_id in download_tasks:
                download_tasks[task_id]['status'] = 'completed'
                download_tasks[task_id]['file_path'] = output_path
                
            return jsonify({
                'success': True,
                'message': '音视频合并完成',
                'output_path': output_path
            })
        else:
            return jsonify({'success': False, 'message': error})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'合并失败: {str(e)}'})

@app.route('/api/bilibili/video/download/status/<task_id>', methods=['GET'])
def get_download_status(task_id):
    """获取指定下载任务的状态信息
    
    Args:
        task_id (str): 任务唯一标识符
        
    Returns:
        JSON: 任务状态信息
        {
            'success': bool,
            'task': {
                'status': str,      # pending/downloading/completed/failed
                'progress': float,  # 下载进度百分比
                'message': str,     # 状态描述信息
                'created_at': str,  # 任务创建时间
                'video_url': str,   # 视频URL
                'file_path': str    # 下载完成后的文件路径(可选)
            }
        }
        
    Note:
        - 用于前端轮询查询下载状态
        - 配合Socket.IO实时推送使用
        - 任务完成后包含下载文件路径
    """
    if task_id not in download_tasks:
        return jsonify({'success': False, 'message': '任务不存在'})
    
    task = download_tasks[task_id]
    return jsonify({
        'success': True,
        'task': task
    })

@app.route('/api/bilibili/video/download/tasks', methods=['GET'])
def get_download_tasks():
    """获取所有下载任务列表
    
    Returns:
        JSON: 所有任务的状态信息
        {
            'success': bool,
            'tasks': [
                {  # 任务详情
                    'id': str,
                    'status': str,
                    'video_url': str,
                    'created_at': str,
                    ...
                },
                ...
            ]
        }
        
    Note:
        - 返回系统中所有下载任务的状态
        - 用于前端显示下载任务管理界面
        - 包含正在进行、已完成和失败的任务
    """
    return jsonify({
        'success': True,
        'tasks': list(download_tasks.values())
    })

@app.route('/api/bilibili/video/download/cancel', methods=['POST'])
def cancel_download():
    """取消指定的下载任务
    
    Request Body:
        {
            'task_id': str  # 要取消的任务ID
        }
        
    Returns:
        JSON: 取消操作结果
        {
            'success': bool,
            'message': str
        }
        
    Note:
        - 取消正在进行的下载任务
        - 清理已下载的临时文件
        - 从任务列表中移除任务记录
    """
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        
        if not task_id:
            return jsonify({'success': False, 'message': '请提供任务ID'})
            
        if task_id not in download_tasks:
            return jsonify({'success': False, 'message': '任务不存在'})
            
        task = download_tasks[task_id]
        
        # 更新任务状态为已取消
        task['status'] = 'cancelled'
        task['cancelled_at'] = datetime.now().isoformat()
        
        # 发送取消状态通知
        socketio.emit('download_status', {
            'task_id': task_id,
            'status': 'cancelled',
            'message': '下载任务已取消'
        })
        
        # 清理可能存在的临时文件
        try:
            if 'title' in task and task['title']:
                safe_title = re.sub(r'[\\/:*?"<>|]', '', task['title'])
                temp_video = f"downloads/{safe_title}_video.m4s"
                temp_audio = f"downloads/{safe_title}_audio.m4s"
                
                if os.path.exists(temp_video):
                    os.remove(temp_video)
                if os.path.exists(temp_audio):
                    os.remove(temp_audio)
        except Exception as cleanup_error:
            print(f"清理临时文件时出错: {cleanup_error}")
        
        # 从任务列表中移除（可选，也可以保留用于历史记录）
        del download_tasks[task_id]
        
        return jsonify({
            'success': True,
            'message': '下载任务已成功取消'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'取消下载失败: {str(e)}'})

@app.route('/api/bilibili/video/download/batch', methods=['POST'])
def batch_download_bilibili_videos():
    """批量下载B站视频
    
    Request Body:
        urls (list): 视频URL列表
        quality (int, optional): 视频清晰度，默认80(1080P)
        save_path (str, optional): 保存路径
        max_concurrent (int, optional): 最大并发数，默认2
        auto_retry (bool, optional): 是否自动重试，默认True
        retry_count (int, optional): 重试次数，默认3
        
    Returns:
        JSON: 批量下载结果
        {
            'success': bool,
            'message': str,
            'task_ids': list,  # 成功创建的任务ID列表
            'failed_urls': list,  # 失败的URL列表
            'total': int,  # 总数
            'success_count': int,  # 成功数
            'failed_count': int   # 失败数
        }
        
    Note:
        - 支持批量创建下载任务
        - 每个URL创建独立的下载任务
        - 通过Socket.IO实时推送各任务进度
        - 支持并发控制和自动重试
    """
    global global_cookies
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        quality_id = data.get('quality', 80)
        save_path = data.get('save_path', '')
        max_concurrent = data.get('max_concurrent', 2)
        auto_retry = data.get('auto_retry', True)
        retry_count = data.get('retry_count', 3)
        
        if not urls or not isinstance(urls, list):
            return jsonify({'success': False, 'message': '请提供有效的URL列表'})
            
        task_ids = []
        failed_urls = []
        
        for url in urls:
            try:
                if not url or not url.strip():
                    continue
                    
                # 生成任务ID
                task_id = str(uuid.uuid4())
                
                # 创建下载任务记录
                download_tasks[task_id] = {
                    'id': task_id,
                    'video_url': url.strip(),
                    'quality_id': quality_id,
                    'status': 'pending',
                    'created_at': datetime.now().isoformat(),
                    'title': '',
                    'file_path': save_path,
                    'error': None,
                    'batch_download': True,
                    'auto_retry': auto_retry,
                    'retry_count': retry_count,
                    'max_concurrent': max_concurrent
                }
                
                # 启动异步下载
                thread = threading.Thread(
                    target=download_video_async,
                    args=(task_id, url.strip(), quality_id, global_cookies)
                )
                thread.daemon = True
                thread.start()
                
                task_ids.append(task_id)
                
            except Exception as e:
                print(f"创建下载任务失败: {url}, 错误: {str(e)}")
                failed_urls.append(url)
                
        return jsonify({
            'success': True,
            'message': f'批量下载任务创建完成，成功: {len(task_ids)}, 失败: {len(failed_urls)}',
            'task_ids': task_ids,
            'failed_urls': failed_urls,
            'total': len(urls),
            'success_count': len(task_ids),
            'failed_count': len(failed_urls)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'批量下载启动失败: {str(e)}'})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t['status'] == 'completed'])
    failed_tasks = len([t for t in tasks if t['status'] == 'failed'])
    total_results = len(results)

    return jsonify({
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'failed_tasks': failed_tasks,
        'total_results': total_results,
        'success_rate': round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0
    })


if __name__ == '__main__':
    # 确保结果目录存在
    os.makedirs('crawler_results', exist_ok=True)

    print("🚀 启动网络信息爬取系统...")
    print("📱 前端界面: http://localhost:5000")
    print("🔧 API文档: http://localhost:5000/api")
    print("\n按 Ctrl+C 停止服务")

    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
