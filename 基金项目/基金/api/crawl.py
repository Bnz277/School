import csv
import io
import json
from datetime import datetime

import pandas as pd
from flask import Blueprint, jsonify, request, send_file

from services.crawler_service import CrawlerService
from core.state import tasks, results
from services.crawler_service import CrawlerService

api_bp = Blueprint('api_common', __name__)

crawler_service = CrawlerService()


@api_bp.route('/api/spiders')
def get_spiders():
    spiders_info = {
        'baidu': {'icon': '🔍', 'description': '爬取百度搜索结果，支持网页和图片搜索', 'features': ['网页搜索', '图片搜索', '实时结果']},
        'bilibili': {'icon': '📺', 'description': '爬取B站视频信息，支持搜索和视频详情', 'features': ['视频搜索', '详细信息', '下载支持']},
        'csdn': {'icon': '📝', 'description': '爬取CSDN技术文章和博客内容', 'features': ['技术文章', '博客内容', '代码示例']},
        'url': {'icon': '🌐', 'description': '爬取指定URL的网页内容和数据', 'features': ['自定义URL', '内容提取', '多格式支持']}
    }
    spiders_list = []
    for key, info in crawler_service.spiders.items():
        detail = spiders_info.get(key, {'icon': '🕷️', 'description': '通用爬虫', 'features': ['数据采集']})
        spiders_list.append({
            'id': key, 'name': info['name'], 'type': info['type'],
            'icon': detail['icon'], 'description': detail['description'], 'features': detail['features']
        })
    return jsonify(spiders_list)


@api_bp.route('/api/crawl', methods=['POST'])
def crawl():
    from core.state import task_counter as counter_ref  # 引用后再更新回去
    global task_counter
    task_counter = counter_ref
    try:
        data = request.get_json() or {}
        spider_type = data.get('spider_type')
        if not spider_type:
            return jsonify({'success': False, 'message': '缺少爬虫类型'}), 400

        task_type = 'url' if spider_type == 'url' else 'search'
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
            data_type = data.get('data_type', 'text')
            if not keyword:
                return jsonify({'success': False, 'message': '缺少搜索关键词'}), 400
            task.update({'keyword': keyword, 'max_results': max_results, 'data_type': data_type})
            search_results, error = crawler_service.execute_search(spider_type, keyword, max_results, data_type)
            if error:
                task.update({'status': 'failed', 'error': error, 'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                tasks.append(task)
                return jsonify({'success': False, 'message': f'爬取失败: {error}', 'task_id': task_counter})
            else:
                task.update({'status': 'completed', 'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                result = {'id': task_counter, 'task_id': task_counter, 'spider_type': spider_type, 'task_type': task_type,
                          'keyword': keyword, 'data': search_results, 'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                results.append(result)
        else:
            url = data.get('url')
            if not url:
                return jsonify({'success': False, 'message': '缺少目标URL'}), 400
            task.update({'url': url})
            
            # 修复：适配增强版URL提取器的返回格式
            content_data, error = crawler_service.execute_url_extraction(url)
            if error:
                task.update({'status': 'failed', 'error': error, 'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                tasks.append(task)
                return jsonify({'success': False, 'message': f'爬取失败: {error}', 'task_id': task_counter})
            else:
                task.update({'status': 'completed', 'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                
                # 构建标准化的结果格式
                url_results = [{
                    'index': 1,
                    'title': content_data.get('title', '网页内容'),
                    'url': url,
                    'content': content_data.get('preview', ''),
                    'full_content': content_data.get('full_content', ''),
                    'text_length': content_data.get('text_length', 0),
                    'images_count': content_data.get('images_count', 0),
                    'images': content_data.get('images', []),
                    'metadata': content_data.get('metadata', {}),
                    'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }]
                
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
        if 'result' in locals():
            return jsonify({'success': True, 'message': '爬取任务完成', 'task_id': task_counter, 'results': result['data']})
        else:
            return jsonify({'success': False, 'message': '未知错误：无法获取结果', 'task_id': task_counter, 'results': []})
    finally:
        # 写回全局计数
        from core import state as st
        st.task_counter = task_counter


@api_bp.route('/api/task/<int:task_id>')
def get_task_status(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    if task['status'] == 'completed':
        result = next((r for r in results if r['task_id'] == task_id), None)
        if result:
            task['results'] = result['data']
    return jsonify(task)


@api_bp.route('/api/tasks')
def get_tasks():
    return jsonify(tasks)


@api_bp.route('/api/results')
def get_results():
    return jsonify(results)


@api_bp.route('/api/results/<int:result_id>')
def get_result_detail(result_id):
    result = next((r for r in results if r['id'] == result_id), None)
    if not result:
        return jsonify({'error': '结果不存在'}), 404
    return jsonify(result)


@api_bp.route('/api/export/<int:result_id>/<format_type>')
def export_result(result_id, format_type):
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
            output = io.StringIO(); json.dump(data, output, ensure_ascii=False, indent=2); output.seek(0)
            return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='application/json', as_attachment=True, download_name=filename)

        elif format_type == 'csv':
            filename = f"{spider_name}_{keyword}_{timestamp}.csv"
            output = io.StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            output.seek(0)
            return send_file(io.BytesIO(output.getvalue().encode('utf-8-sig')), mimetype='text/csv', as_attachment=True, download_name=filename)

        elif format_type == 'excel':
            filename = f"{spider_name}_{keyword}_{timestamp}.xlsx"
            output = io.BytesIO()
            pd.DataFrame(data).to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=filename)

        elif format_type == 'txt':
            filename = f"{spider_name}_{keyword}_{timestamp}.txt"
            output = io.StringIO()
            for i, item in enumerate(data, 1):
                output.write(f"=== 结果 {i} ===\n")
                for key, value in item.items():
                    output.write(f"{key}: {value}\n")
                output.write("\n")
            output.seek(0)
            return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='text/plain', as_attachment=True, download_name=filename)

        elif format_type == 'xml':
            filename = f"{spider_name}_{keyword}_{timestamp}.xml"
            output = io.StringIO()
            output.write('<?xml version="1.0" encoding="UTF-8"?>\n<results>\n  <metadata>\n')
            output.write(f'    <spider>{spider_name}</spider>\n')
            output.write(f'    <keyword>{keyword}</keyword>\n')
            output.write(f'    <timestamp>{result["created_at"]}</timestamp>\n')
            output.write(f'    <count>{len(data)}</count>\n  </metadata>\n  <data>\n')
            for i, item in enumerate(data, 1):
                output.write(f'    <item id="{i}">\n')
                for key, value in item.items():
                    escaped_value = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
                    output.write(f'      <{key}>{escaped_value}</{key}>\n')
                output.write(f'    </item>\n')
            output.write('  </data>\n</results>\n'); output.seek(0)
            return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='application/xml', as_attachment=True, download_name=filename)

        elif format_type == 'pdf':
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.lib import colors

                filename = f"{spider_name}_{keyword}_{timestamp}.pdf"
                output = io.BytesIO()
                doc = SimpleDocTemplate(output, pagesize=A4)
                styles = getSampleStyleSheet()
                story = []
                title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30, alignment=1)
                story.append(Paragraph(f"{spider_name} 搜索结果", title_style))
                meta_data = [['关键词', keyword], ['搜索时间', result['created_at']], ['结果数量', str(len(data))]]
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
                story.append(meta_table); story.append(Spacer(1, 20))
                for i, item in enumerate(data, 1):
                    story.append(Paragraph(f"结果 {i}", styles['Heading2']))
                    item_data = [[key, str(value)[:100] + '...' if len(str(value)) > 100 else str(value)] for key, value in item.items()]
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
                    story.append(item_table); story.append(Spacer(1, 15))
                doc.build(story); output.seek(0)
                return send_file(output, mimetype='application/pdf', as_attachment=True, download_name=filename)
            except ImportError:
                return jsonify({'error': 'PDF导出功能需要安装reportlab库'}), 500

        elif format_type == 'md':
            filename = f"{spider_name}_{keyword}_{timestamp}.md"
            output = io.StringIO()
            output.write(f"# {spider_name} 搜索结果\n\n")
            output.write(f"**关键词**: {keyword}\n")
            output.write(f"**搜索时间**: {result['created_at']}\n")
            output.write(f"**结果数量**: {len(data)}\n\n")
            output.write("---\n\n")
            
            for i, item in enumerate(data, 1):
                output.write(f"## 结果 {i}\n\n")
                for key, value in item.items():
                    if key == 'url':
                        output.write(f"**{key}**: [{value}]({value})\n")
                    elif key == 'title':
                        output.write(f"**{key}**: {value}\n")
                    elif key == 'description' or key == 'content':
                        # 处理长文本内容
                        content_text = str(value)[:500] + '...' if len(str(value)) > 500 else str(value)
                        output.write(f"**{key}**: {content_text}\n")
                    else:
                        output.write(f"**{key}**: {value}\n")
                output.write("\n")
            output.seek(0)
            return send_file(io.BytesIO(output.getvalue().encode('utf-8')), 
                           mimetype='text/markdown', 
                           as_attachment=True, 
                           download_name=filename)

    else:
        # URL提取结果的MD导出
        data = result['data']
        url = result['url']

        if format_type == 'md':
            filename = f"网页内容_{timestamp}.md"
            output = io.StringIO()
            
            # 如果是新的结构化数据格式
            if data and isinstance(data, list) and len(data) > 0:
                url_result = data[0]  # 取第一个结果
                
                output.write(f"# 网页内容\n\n")
                output.write(f"**URL**: [{url}]({url})\n")
                output.write(f"**标题**: {url_result.get('title', '无标题')}\n")
                output.write(f"**提取时间**: {result['created_at']}\n")
                output.write(f"**文本长度**: {url_result.get('text_length', 0)} 字符\n")
                output.write(f"**图片数量**: {url_result.get('images_count', 0)} 张\n\n")
                output.write("---\n\n")
                
                # 完整文本内容
                if url_result.get('full_content'):
                    output.write("## 📝 完整文本内容\n\n")
                    output.write(f"{url_result['full_content']}\n\n")
                
                # 图片列表
                if url_result.get('images') and len(url_result['images']) > 0:
                    output.write("## 🖼️ 网页图片\n\n")
                    for i, img_url in enumerate(url_result['images'], 1):
                        output.write(f"{i}. ![图片{i}]({img_url})\n")
                    output.write("\n")
                
                # 技术信息
                if url_result.get('metadata'):
                    metadata = url_result['metadata']
                    output.write("## 🔧 技术信息\n\n")
                    if metadata.get('content_type'):
                        output.write(f"- **内容类型**: {metadata['content_type']}\n")
                    if metadata.get('status_code'):
                        output.write(f"- **状态码**: {metadata['status_code']}\n")
                    if metadata.get('charset'):
                        output.write(f"- **字符编码**: {metadata['charset']}\n")
                    if metadata.get('final_url') and metadata['final_url'] != url:
                        output.write(f"- **最终URL**: {metadata['final_url']}\n")
                    output.write("\n")
            else:
                # 兼容旧格式
                output.write(f"# 网页内容\n\n")
                output.write(f"**URL**: [{url}]({url})\n")
                output.write(f"**提取时间**: {result['created_at']}\n\n")
                output.write("---\n\n")
                if isinstance(data, str):
                    output.write(data)
                else:
                    output.write("无法获取内容")
            
            output.seek(0)
            return send_file(io.BytesIO(output.getvalue().encode('utf-8')), 
                           mimetype='text/markdown', 
                           as_attachment=True, 
                           download_name=filename)

    return jsonify({'error': '不支持的导出格式'}), 400