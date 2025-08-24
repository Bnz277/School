import os
import re
import uuid
import threading
from datetime import datetime

from flask import Blueprint, jsonify, request

from core.state import download_tasks
from extensions import socketio
from services import bilibili_auth as auth
from services.bilibili_download import (
    get_video_info, format_file_size, get_stream_file_size,
    download_video_async, merge_video_audio
)

bili_bp = Blueprint('api_bilibili', __name__)


@bili_bp.get('/api/bilibili/login/qr')
def get_bilibili_qr():
    ok, msg, data = auth.get_qr()
    if not ok:
        return jsonify({'success': False, 'message': msg})
    return jsonify({'success': True, **data})


@bili_bp.post('/api/bilibili/login/poll')
def poll_bilibili_login():
    data = request.get_json() or {}
    qrcode_key = data.get('qrcode_key')
    ok, msg, payload = auth.poll(qrcode_key)
    if not ok:
        return jsonify({'success': False, 'message': msg})
    return jsonify({'success': True, **payload})


@bili_bp.get('/api/bilibili/login/status')
def get_bilibili_login_status():
    ok, msg, payload = auth.status()
    if not ok:
        return jsonify({'success': False, 'message': msg})
    return jsonify({'success': True, **payload})


@bili_bp.post('/api/bilibili/logout')
def bilibili_logout():
    ok, msg = auth.logout()
    return jsonify({'success': ok, 'message': msg})


@bili_bp.post('/api/bilibili/video/info')
def get_bilibili_video_info():
    data = request.get_json() or {}
    video_url = data.get('video_url')
    if not video_url:
        return jsonify({'success': False, 'message': '请提供视频URL'})

    bvid, title, playinfo, duration = get_video_info(video_url, auth.global_cookies)

    qualities = playinfo['data']['support_formats']
    logged_in = bool(auth.global_cookies)
    if not logged_in:
        qualities = [q for q in qualities if q['quality'] <= 80]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": f"https://www.bilibili.com/video/{bvid}"
    }
    if auth.global_cookies:
        headers["Cookie"] = auth.global_cookies

    formatted_qualities = []
    for q in qualities:
        video_stream = next(
            (s for s in playinfo['data']['dash']['video'] if s['id'] == q['quality']),
            None
        )
        audio_stream = playinfo['data']['dash']['audio'][0] if playinfo['data']['dash']['audio'] else None
        total_size = 0
        if video_stream:
            total_size += get_stream_file_size(video_stream['baseUrl'], headers)
        if audio_stream:
            total_size += get_stream_file_size(audio_stream['baseUrl'], headers)

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


@bili_bp.post('/api/bilibili/video/download')
def download_bilibili_video():
    data = request.get_json() or {}
    video_url = data.get('video_url')
    quality_id = data.get('quality', 80)
    if not video_url:
        return jsonify({'success': False, 'message': '请提供视频URL'})

    task_id = str(uuid.uuid4())
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

    thread = threading.Thread(
        target=download_video_async,
        args=(task_id, video_url, quality_id, auth.global_cookies),
        daemon=True
    )
    thread.start()

    return jsonify({'success': True, 'task_id': task_id, 'message': '下载任务已启动'})


@bili_bp.post('/api/bilibili/video/merge')
def merge_bilibili_video():
    data = request.get_json() or {}
    task_id = data.get('task_id')
    video_path = data.get('video_path')
    audio_path = data.get('audio_path')
    output_path = data.get('output_path')

    if not task_id or not output_path:
        return jsonify({'success': False, 'message': '缺少必要参数'})

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

    if not os.path.exists(video_path):
        return jsonify({'success': False, 'message': f'视频文件不存在: {video_path}'})
    if not os.path.exists(audio_path):
        return jsonify({'success': False, 'message': f'音频文件不存在: {audio_path}'})

    success, error = merge_video_audio(video_path, audio_path, output_path)
    if success:
        if task_id in download_tasks:
            download_tasks[task_id]['status'] = 'completed'
            download_tasks[task_id]['file_path'] = output_path
        return jsonify({'success': True, 'message': '音视频合并完成', 'output_path': output_path})
    else:
        return jsonify({'success': False, 'message': error})


@bili_bp.get('/api/bilibili/video/download/status/<task_id>')
def get_download_status(task_id):
    if task_id not in download_tasks:
        return jsonify({'success': False, 'message': '任务不存在'})
    return jsonify({'success': True, 'task': download_tasks[task_id]})


@bili_bp.get('/api/bilibili/video/download/tasks')
def get_download_tasks():
    return jsonify({'success': True, 'tasks': list(download_tasks.values())})


@bili_bp.post('/api/bilibili/video/download/cancel')
def cancel_download():
    data = request.get_json() or {}
    task_id = data.get('task_id')
    if not task_id:
        return jsonify({'success': False, 'message': '请提供任务ID'})
    if task_id not in download_tasks:
        return jsonify({'success': False, 'message': '任务不存在'})

    task = download_tasks[task_id]
    task['status'] = 'cancelled'
    task['cancelled_at'] = datetime.now().isoformat()

    socketio.emit('download_status', {'task_id': task_id, 'status': 'cancelled', 'message': '下载任务已取消'})

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

    del download_tasks[task_id]
    return jsonify({'success': True, 'message': '下载任务已成功取消'})


@bili_bp.post('/api/bilibili/video/download/batch')
def batch_download_bilibili_videos():
    data = request.get_json() or {}
    urls = data.get('urls', [])
    quality_id = data.get('quality', 80)
    save_path = data.get('save_path', '')
    max_concurrent = data.get('max_concurrent', 2)
    auto_retry = data.get('auto_retry', True)
    retry_count = data.get('retry_count', 3)

    if not urls or not isinstance(urls, list):
        return jsonify({'success': False, 'message': '请提供有效的URL列表'})

    task_ids, failed_urls = [], []
    for url in urls:
        try:
            if not url or not url.strip():
                continue
            task_id = str(uuid.uuid4())
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
            thread = threading.Thread(target=download_video_async, args=(task_id, url.strip(), quality_id, auth.global_cookies), daemon=True)
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