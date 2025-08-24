import os
import re
import subprocess
import random
import time
from urllib.parse import unquote, quote
import requests
from bs4 import BeautifulSoup


class BilibiliSpider:
    """B站视频搜索爬虫"""

    def __init__(self):
        self.delay_range = (1, 3)  # 随机延迟范围(秒)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'DNT': '1'
        }

    def _get_soup(self, url):
        """获取BeautifulSoup对象"""
        try:
            time.sleep(random.uniform(*self.delay_range))
            response = requests.get(url, headers=self.headers, timeout=10)

            if len(response.text) < 5000 or "验证" in response.text:
                print("⚠️ 可能触发了反爬机制")
                return None

            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"请求失败: {url} | 错误: {e}")
            return None

    def _parse_video_item(self, item):
        """解析单个视频元素"""
        try:
            # 标题（兼容新旧版本）
            title_elem = item.find('a', {'title': True}) or item.find('h3', {'title': True})
            title = title_elem['title'] if title_elem else '无标题'

            # 链接（处理相对URL）
            link_elem = item.find('a', href=True)
            video_url = 'https:' + link_elem['href'] if link_elem and link_elem['href'].startswith('//') else ''

            # 缩略图（新增）
            img_elem = item.find('img') or item.find('picture img')
            thumbnail = ''
            if img_elem:
                # 获取图片URL，处理懒加载
                thumbnail = img_elem.get('data-src') or img_elem.get('src') or ''
                if thumbnail and thumbnail.startswith('//'):
                    thumbnail = 'https:' + thumbnail

            # UP主（兼容新旧版本）
            up_elem = item.find(class_='up-name') or item.find(class_='bili-video-card__info--author')
            up_name = up_elem.text.strip() if up_elem else '未知UP主'

            # 播放量（兼容新旧版本）
            play_elem = item.find(title='观看') or item.find(class_='play') or item.find(
                class_='bili-video-card__stats--item')
            play_count = play_elem.text.strip() if play_elem else '0'

            # 时长（可选）
            duration_elem = item.find(class_='length') or item.find(class_='bili-video-card__stats__duration')
            duration = duration_elem.text.strip() if duration_elem else ''

            # 发布时间（新增）
            time_elem = item.find(class_='time') or item.find(class_='bili-video-card__info--date')
            publish_time = time_elem.text.strip() if time_elem else ''

            return {
                'title': title,
                'url': video_url,
                'thumbnail': thumbnail,
                'up': up_name,
                'play': play_count,
                'duration': duration,
                'publish_time': publish_time,
                'type': 'video'  # 标识数据类型
            }
        except Exception as e:
            print(f"解析视频失败: {e}")
            return None

    def search(self, keyword, max_results=10):
        """
        执行B站视频搜索

        参数:
            keyword (str): 搜索关键词
            max_results (int): 最大结果数量

        返回:
            list: 搜索结果列表，每个元素是包含视频信息的字典
        """
        base_url = f'https://search.bilibili.com/all?keyword={quote(keyword)}'
        print(f"🔍 正在B站搜索: {keyword} (最多{max_results}条)")

        soup = self._get_soup(base_url)
        if not soup:
            return []

        video_items = soup.select('li.video-item, div.bili-video-card, div.video-list__item')
        if not video_items:
            print("⚠️ 未找到视频元素，可能页面结构已更新")
            return []

        results = []
        for i, item in enumerate(video_items[:max_results], 1):
            video_info = self._parse_video_item(item)
            if video_info:
                results.append({
                    'index': i,
                    **video_info
                })

        return results


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


def download_video(video_url, index=None):
    """下载单个视频"""
    cookie = "DedeUserID=473335461; DedeUserID__ckMd5=b8e4cab3e48f5f59; SESSDATA=fe246000%2C1770705837%2C6e5bd%2A82CjDQl-uYIqiFNwTWJWxnZbE3-Q_eA5c7og56zQkzJt8L0X_KV7RPOZfQXNXb52SHZH8SVlhfcDVXMzFNMkJJS3N4S0NrVGRLOEp5MGl1SXRqU2xzSG91aS1GOGZhSzNiUGktR3JkVmNhaHdNYjdQcVc2NXgyTkNLY3d6ZjFKLXZpc05kODZLQWpRIIEC; bili_jct=0bf2a10ac76986617f37b15a667ef17e; sid=88hqonbi; DedeUserID=473335461; DedeUserID__ckMd5=b8e4cab3e48f5f59; SESSDATA=fe246000%2C1770705837%2C6e5bd%2A82CjDQl-uYIqiFNwTWJWxnZbE3-Q_eA5c7og56zQkzJt8L0X_KV7RPOZfQXNXb52SHZH8SVlhfcDVXMzFNMkJJS3N4S0NrVGRLOEp5MGl1SXRqU2xzSG91aS1GOGZhSzNiUGktR3JkVmNhaHdNYjdQcVc2NXgyTkNLY3d6ZjFKLXZpc05kODZLQWpRIIEC; b_nut=1755153837; bili_jct=0bf2a10ac76986617f37b15a667ef17e; buvid3=75F22688-716E-95AA-C1AC-3DF47E9361BB37797infoc; sid=p92b6h12; DedeUserID=473335461; DedeUserID__ckMd5=b8e4cab3e48f5f59; SESSDATA=fe246000%2C1770705837%2C6e5bd%2A82CjDQl-uYIqiFNwTWJWxnZbE3-Q_eA5c7og56zQkzJt8L0X_KV7RPOZfQXNXb52SHZH8SVlhfcDVXMzFNMkJJS3N4S0NrVGRLOEp5MGl1SXRqU2xzSG91aS1GOGZhSzNiUGktR3JkVmNhaHdNYjdQcVc2NXgyTkNLY3d6ZjFKLXZpc05kODZLQWpRIIEC; bili_jct=0bf2a10ac76986617f37b15a667ef17e; sid=n0gy8lf2; DedeUserID=473335461; DedeUserID__ckMd5=b8e4cab3e48f5f59; SESSDATA=fe246000%2C1770705837%2C6e5bd%2A82CjDQl-uYIqiFNwTWJWxnZbE3-Q_eA5c7og56zQkzJt8L0X_KV7RPOZfQXNXb52SHZH8SVlhfcDVXMzFNMkJJS3N4S0NrVGRLOEp5MGl1SXRqU2xzSG91aS1GOGZhSzNiUGktR3JkVmNhaHdNYjdQcVc2NXgyTkNLY3d6ZjFKLXZpc05kODZLQWpRIIEC; bili_jct=0bf2a10ac76986617f37b15a667ef17e; sid=8e5vnjj9; DedeUserID=473335461; DedeUserID__ckMd5=b8e4cab3e48f5f59; SESSDATA=fe246000%2C1770705837%2C6e5bd%2A82CjDQl-uYIqiFNwTWJWxnZbE3-Q_eA5c7og56zQkzJt8L0X_KV7RPOZfQXNXb52SHZH8SVlhfcDVXMzFNMkJJS3N4S0NrVGRLOEp5MGl1SXRqU2xzSG91aS1GOGZhSzNiUGktR3JkVmNhaHdNYjdQcVc2NXgyTkNLY3d6ZjFKLXZpc05kODZLQWpRIIEC; bili_jct=0bf2a10ac76986617f37b15a667ef17e; sid=e5rllm5p"  # 这里可以替换为你的有效Cookie

    try:
        # 1. 获取视频信息
        if index is not None:
            print(f"\n[{index}] 正在获取视频信息...")
        else:
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
                    return True
                else:
                    print("\n自动合并失败，请手动使用以下命令合并:")
                    print(f'ffmpeg -i "{temp_video}" -i "{temp_audio}" -c copy "{final_output}"')
                    return False
        return False
    except Exception as e:
        print(f"\n下载过程中发生错误: {str(e)}")
        print("可能的原因：")
        print("- Cookie已过期或无效（特别是SESSDATA和bili_jct）")
        print("- 视频需要大会员权限（当前清晰度）")
        print("- 网络连接问题（尝试更换网络）")
        print("- 视频URL格式不正确（请确认是B站视频链接）")
        print("- B站API限制（稍后再试）")
        print("- 未安装ffmpeg（合并功能需要ffmpeg）")
        return False


def parse_selection(input_str, max_index):
    """解析用户的选择输入，支持单个数字、范围和组合"""
    selected_indices = set()

    # 处理逗号分隔
    parts = input_str.split(',')

    for part in parts:
        part = part.strip()
        if '-' in part:
            # 处理范围
            try:
                start, end = map(int, part.split('-'))
                for i in range(start, end + 1):
                    if 1 <= i <= max_index:
                        selected_indices.add(i)
            except ValueError:
                print(f"无效的范围: {part}")
        else:
            # 处理单个数字
            try:
                index = int(part)
                if 1 <= index <= max_index:
                    selected_indices.add(index)
                else:
                    print(f"编号 {index} 超出范围 (1-{max_index})")
            except ValueError:
                print(f"无效的数字: {part}")

    return sorted(selected_indices)


def main():
    print("B站视频搜索与下载工具")
    print("=" * 50)

    while True:
        print("\n请选择操作模式:")
        print("1. 搜索视频")
        print("2. 直接输入URL下载")
        print("3. 退出")

        choice = input("请输入选项(1/2/3): ").strip()

        if choice == "1":
            # 搜索模式
            keyword = input("请输入搜索关键词: ").strip()
            if not keyword:
                print("关键词不能为空!")
                continue

            spider = BilibiliSpider()
            results = spider.search(keyword, max_results=15)

            if not results:
                print("未找到相关视频，请尝试其他关键词")
                continue

            print("\n=== B站视频搜索结果 ===")
            for item in results:
                print(f"\n【{item['index']}】{item['title']}")
                print(f"👤 UP主: {item['up']}")
                print(f"🔗 链接: {item['url']}")
                print(f"👀 播放: {item['play']}")
                if item['duration']:
                    print(f"⏱️ 时长: {item['duration']}")
            print(f"\n✅ 共找到 {len(results)} 条结果")

            # 让用户选择下载
            while True:
                print(f"\n请选择要下载的视频 (1-{len(results)})")
                print("支持格式: 单个数字(1), 范围(1-5), 组合(1,3-5,7)")
                print("输入 0 返回主菜单 (不下载)")

                selection = input("请输入选择: ").strip()

                if selection == "0":
                    print("返回主菜单...")
                    break

                if not selection:
                    print("请输入有效选择!")
                    continue

                # 解析用户选择
                selected_indices = parse_selection(selection, len(results))

                if not selected_indices:
                    print("没有有效的选择，请重新输入")
                    continue

                print(f"\n您选择了以下视频: {', '.join(map(str, selected_indices))}")
                confirm = input("确认下载? (y/N): ").strip().lower()

                if confirm == 'y' or confirm == 'yes':
                    # 开始下载选中的视频
                    success_count = 0
                    for idx in selected_indices:
                        selected_video = results[idx - 1]
                        print(f"\n开始下载 [{idx}]: {selected_video['title']}")
                        if download_video(selected_video['url'], idx):
                            success_count += 1
                            print(f"[{idx}] 下载完成!")
                        else:
                            print(f"[{idx}] 下载失败!")

                    print(f"\n下载完成! 成功: {success_count}/{len(selected_indices)}")
                    break
                else:
                    print("取消下载，请重新选择")

        elif choice == "2":
            # 直接下载模式
            video_url = input("请输入B站视频URL: ").strip()
            if not video_url:
                print("URL不能为空!")
                continue

            success = download_video(video_url)
            if success:
                print("下载完成!")
            else:
                print("下载失败!")

        elif choice == "3":
            print("感谢使用，再见!")
            break

        else:
            print("无效选项，请重新选择!")


if __name__ == "__main__":
    main()