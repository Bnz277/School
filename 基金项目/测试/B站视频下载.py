import os
import re
import subprocess
from urllib.parse import unquote

import requests


def extract_bvid(url):
    """从URL中提取BV号（兼容更多格式）"""
    # 处理可能的短链接
    if "b23.tv" in url:
        try:
            url = requests.get(url, allow_redirects=False).headers.get('location', url)
        except:
            pass

    # 提取BV号
    match = re.search(r'(BV[0-9A-Za-z]+)', url)
    if not match:
        raise ValueError("URL中未找到有效的BV号")
    return match.group(1)


def get_video_info(video_url, cookie):
    try:
        bvid = extract_bvid(video_url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Cookie": cookie,
            "Referer": f"https://www.bilibili.com/video/{bvid}"
        }

        # 获取视频基本信息
        info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        info = requests.get(info_url, headers=headers, timeout=10).json()
        if info['code'] != 0:
            raise ValueError(f"获取视频信息失败: {info.get('message')}")

        cid = info['data']['cid']
        title = re.sub(r'[\\/:*?"<>|]', '', unquote(info['data']['title']))

        # 获取播放信息
        play_url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&fnval=4048"
        playinfo = requests.get(play_url, headers=headers, timeout=10).json()
        if playinfo['code'] != 0:
            raise ValueError(f"获取播放信息失败: {playinfo.get('message')}")

        return bvid, title, playinfo
    except Exception as e:
        raise ValueError(f"获取视频信息时出错: {str(e)}")


def select_quality(playinfo):
    print("\n可选清晰度:")
    qualities = playinfo['data']['support_formats']
    for i, q in enumerate(qualities):
        print(f"{i + 1}. {q['new_description']} (id={q['quality']})")

    while True:
        try:
            choice = int(input("请选择清晰度(输入序号): ")) - 1
            if 0 <= choice < len(qualities):
                return qualities[choice]['quality']
            print("序号无效，请重新输入")
        except ValueError:
            print("请输入有效数字")


def download_file(url, filename, headers):
    print(f"\n正在下载: {filename}")
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
                        if total_size > 0:
                            percent = downloaded / total_size * 100
                            print(f"\r进度: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='')
        print("\n下载完成!")
        return True
    except Exception as e:
        print(f"\n下载失败: {str(e)}")
        return False


def merge_video_audio(video_path, audio_path, output_path):
    """使用ffmpeg合并音视频"""
    print("\n开始合并音视频...")
    try:
        cmd = [
            'ffmpeg',
            '-y',  # 自动覆盖已存在文件
            '-i', video_path,
            '-i', audio_path,
            '-c', 'copy',  # 直接流拷贝，不重新编码
            output_path
        ]

        # 隐藏ffmpeg的输出（在Windows和Linux/macOS上方式不同）
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        subprocess.run(cmd, check=True, startupinfo=startupinfo,
                       stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

        print("合并完成!")

        # 删除临时文件
        os.remove(video_path)
        os.remove(audio_path)
        print("已删除临时音视频文件")

        return True
    except subprocess.CalledProcessError as e:
        print(f"合并失败: {str(e)}")
        print("请确保已安装ffmpeg并添加到系统PATH中")
        return False
    except Exception as e:
        print(f"合并过程中出错: {str(e)}")
        return False


def main():
    print("B站视频下载器 (支持清晰度选择和自动合并)")
    print("=" * 50)

    # 输入参数
    video_url = input("请输入B站视频URL: ").strip()
    cookie = "DedeUserID=473335461; DedeUserID__ckMd5=b8e4cab3e48f5f59; SESSDATA=fe246000%2C1770705837%2C6e5bd%2A82CjDQl-uYIqiFNwTWJWxnZbE3-Q_eA5c7og56zQkzJt8L0X_KV7RPOZfQXNXb52SHZH8SVlhfcDVXMzFNMkJJS3N4S0NrVGRLOEp5MGl1SXRqU2xzSG91aS1GOGZhSzNiUGktR3JkVmNhaHdNYjdQcVc2NXgyTkNLY3d6ZjFKLXZpc05kODZLQWpRIIEC; bili_jct=0bf2a10ac76986617f37b15a667ef17e; sid=88hqonbi; DedeUserID=473335461; DedeUserID__ckMd5=b8e4cab3e48f5f59; SESSDATA=fe246000%2C1770705837%2C6e5bd%2A82CjDQl-uYIqiFNwTWJWxnZbE3-Q_eA5c7og56zQkzJt8L0X_KV7RPOZfQXNXb52SHZH8SVlhfcDVXMzFNMkJJS3N4S0NrVGRLOEp5MGl1SXRqU2xzSG91aS1GOGZhSzNiUGktR3JkVmNhaHdNYjdQcVc2NXgyTkNLY3d6ZjFKLXZpc05kODZLQWpRIIEC; b_nut=1755153837; bili_jct=0bf2a10ac76986617f37b15a667ef17e; buvid3=75F22688-716E-95AA-C1AC-3DF47E9361BB37797infoc; sid=p92b6h12; DedeUserID=473335461; DedeUserID__ckMd5=b8e4cab3e48f5f59; SESSDATA=fe246000%2C1770705837%2C6e5bd%2A82CjDQl-uYIqiFNwTWJWxnZbE3-Q_eA5c7og56zQkzJt8L0X_KV7RPOZfQXNXb52SHZH8SVlhfcDVXMzFNMkJJS3N4S0NrVGRLOEp5MGl1SXRqU2xzSG91aS1GOGZhSzNiUGktR3JkVmNhaHdNYjdQcVc2NXgyTkNLY3d6ZjFKLXZpc05kODZLQWpRIIEC; bili_jct=0bf2a10ac76986617f37b15a667ef17e; sid=n0gy8lf2; DedeUserID=473335461; DedeUserID__ckMd5=b8e4cab3e48f5f59; SESSDATA=fe246000%2C1770705837%2C6e5bd%2A82CjDQl-uYIqiFNwTWJWxnZbE3-Q_eA5c7og56zQkzJt8L0X_KV7RPOZfQXNXb52SHZH8SVlhfcDVXMzFNMkJJS3N4S0NrVGRLOEp5MGl1SXRqU2xzSG91aS1GOGZhSzNiUGktR3JkVmNhaHdNYjdQcVc2NXgyTkNLY3d6ZjFKLXZpc05kODZLQWpRIIEC; bili_jct=0bf2a10ac76986617f37b15a667ef17e; sid=8e5vnjj9; DedeUserID=473335461; DedeUserID__ckMd5=b8e4cab3e48f5f59; SESSDATA=fe246000%2C1770705837%2C6e5bd%2A82CjDQl-uYIqiFNwTWJWxnZbE3-Q_eA5c7og56zQkzJt8L0X_KV7RPOZfQXNXb52SHZH8SVlhfcDVXMzFNMkJJS3N4S0NrVGRLOEp5MGl1SXRqU2xzSG91aS1GOGZhSzNiUGktR3JkVmNhaHdNYjdQcVc2NXgyTkNLY3d6ZjFKLXZpc05kODZLQWpRIIEC; bili_jct=0bf2a10ac76986617f37b15a667ef17e; sid=e5rllm5p"

    try:
        # 1. 获取视频信息
        print("\n正在获取视频信息...")
        bvid, title, playinfo = get_video_info(video_url, cookie)
        print(f"视频标题: {title}")

        # 2. 选择清晰度
        quality_id = select_quality(playinfo)

        # 3. 获取流地址
        print("\n正在获取视频流地址...")
        video_stream = next(
            (stream for stream in playinfo['data']['dash']['video']
             if stream['id'] == quality_id),
            playinfo['data']['dash']['video'][0]
        )
        audio_stream = playinfo['data']['dash']['audio'][0]

        # 4. 下载设置
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": f"https://www.bilibili.com/video/{bvid}",
            "Cookie": cookie
        }

        # 5. 创建下载目录
        os.makedirs("downloads", exist_ok=True)
        base_name = f"downloads/{title}"
        temp_video = f"{base_name}_video.mp4"
        temp_audio = f"{base_name}_audio.mp3"
        final_output = f"{base_name}.mp4"

        # 6. 下载视频和音频
        if download_file(video_stream['baseUrl'], temp_video, headers):
            if download_file(audio_stream['baseUrl'], temp_audio, headers):
                # 7. 自动合并
                if merge_video_audio(temp_video, temp_audio, final_output):
                    print(f"\n最终视频已保存为: {final_output}")
                else:
                    print("\n自动合并失败，请手动使用以下命令合并:")
                    print(f'ffmpeg -i "{temp_video}" -i "{temp_audio}" -c copy "{final_output}"')

    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        print("可能的原因：")
        print("- Cookie已过期或无效（特别是SESSDATA和bili_jct）")
        print("- 视频需要大会员权限（当前清晰度）")
        print("- 网络连接问题（尝试更换网络）")
        print("- 视频URL格式不正确（请确认是B站视频链接）")
        print("- B站API限制（稍后再试）")
        print("- 未安装ffmpeg（合并功能需要ffmpeg）")


if __name__ == "__main__":
    main()
