import os
import re
import io
import uuid
import threading
import subprocess
from datetime import datetime
from urllib.parse import unquote

import requests

from extensions import socketio
from core.state import download_tasks

def extract_bvid(url: str):
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
    try:
        bvid = extract_bvid(video_url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": f"https://www.bilibili.com/video/{bvid}"
        }
        if cookie:
            headers["Cookie"] = cookie

        info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        info = requests.get(info_url, headers=headers, timeout=10).json()
        if info['code'] != 0:
            raise ValueError(f"获取视频信息失败: {info.get('message')}")

        cid = info['data']['cid']
        title = re.sub(r'[\\/:*?\"<>|]', '', unquote(info['data']['title']))
        duration = info['data']['duration']
        formatted_duration = format_duration(duration)

        play_url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn=80&fnval=4048&fourk=1"
        playinfo = requests.get(play_url, headers=headers, timeout=10).json()
        if playinfo['code'] != 0:
            raise ValueError(f"获取播放信息失败: {playinfo.get('message')}")

        return bvid, title, playinfo, formatted_duration
    except Exception as e:
        raise ValueError(f"获取视频信息时出错: {str(e)}")


def download_file_with_progress(url, filename, headers, task_id=None, file_type="video"):
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

        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return True, None
    except subprocess.CalledProcessError:
        return False, "合并失败，请确保已安装ffmpeg并添加到系统PATH中"
    except Exception as e:
        return False, f"合并过程中出错: {str(e)}"


def format_file_size(size_bytes: int):
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    return f"{size:.2f}{size_names[i]}"


def get_stream_file_size(url, headers):
    try:
        response = requests.head(url, headers=headers, timeout=10)
        content_length = response.headers.get('content-length')
        if content_length:
            return int(content_length)
        return 0
    except:
        return 0


def download_video_async(task_id, video_url, quality_id, cookie):
    try:
        download_tasks[task_id]['status'] = 'downloading'
        socketio.emit('download_status', {
            'task_id': task_id,
            'status': 'downloading',
            'message': '开始下载视频...'
        })

        bvid, title, playinfo, duration = get_video_info(video_url, cookie)

        video_stream = next(
            (stream for stream in playinfo['data']['dash']['video']
             if stream['id'] == quality_id),
            playinfo['data']['dash']['video'][0]
        )
        audio_stream = playinfo['data']['dash']['audio'][0]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": f"https://www.bilibili.com/video/{bvid}"
        }
        if cookie:
            headers["Cookie"] = cookie

        download_dir = "downloads"
        os.makedirs(download_dir, exist_ok=True)

        safe_title = re.sub(r'[\\/:*?\"<>|]', '', title)
        base_name = f"{download_dir}/{safe_title}"
        temp_video = f"{base_name}_video.mp4"
        temp_audio = f"{base_name}_audio.mp3"
        final_output = f"{base_name}.mp4"

        download_tasks[task_id]['title'] = title
        download_tasks[task_id]['file_path'] = final_output

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