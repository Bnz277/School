import requests
import json


def debug_bilibili_api(bvid):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.bilibili.com"
    }

    try:
        # 1. 获取视频基本信息
        info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        print("\n=== 视频基本信息API ===")
        print(f"请求URL: {info_url}")

        info_resp = requests.get(info_url, headers=headers, timeout=10)
        info_resp.raise_for_status()
        info_data = info_resp.json()

        print(json.dumps(info_data, indent=2, ensure_ascii=False))

        if info_data['code'] != 0:
            print("错误：无法获取视频信息")
            return

        cid = info_data['data']['pages'][0]['cid']
        aid = info_data['data']['aid']

        # 2. 获取视频流信息
        play_url = f"https://api.bilibili.com/x/player/playurl?avid={aid}&bvid={bvid}&cid={cid}&fnval=4048"
        print("\n=== 视频流信息API ===")
        print(f"请求URL: {play_url}")

        play_resp = requests.get(play_url, headers=headers, timeout=10)
        play_resp.raise_for_status()
        play_data = play_resp.json()

        print(json.dumps(play_data, indent=2, ensure_ascii=False))

        if play_data['code'] != 0:
            print("错误：无法获取视频流信息")
            return

        # 3. 解析所有清晰度下载链接
        print("\n=== 所有清晰度下载链接 ===")

        if 'dash' in play_data['data']:
            # DASH格式（多清晰度）
            dash_data = play_data['data']['dash']

            # 获取所有视频流
            video_streams = dash_data['video']
            # 获取所有音频流
            audio_streams = dash_data['audio']

            # 获取支持的清晰度列表
            quality_map = {q['quality']: q['new_description']
                           for q in play_data['data']['support_formats']}

            print("可用清晰度:")
            for stream in video_streams:
                quality_id = stream['id']
                quality_desc = quality_map.get(quality_id, f"未知清晰度({quality_id})")
                print(f"\n清晰度: {quality_desc} (id: {quality_id})")
                print(f"视频URL: {stream['baseUrl']}")
                print(f"编码格式: {stream['codecs']}")
                print(f"分辨率: {stream['width']}x{stream['height']}")
                print(f"码率: {stream['bandwidth'] // 1000}kbps")

                # 音频信息
                if audio_streams:
                    print(f"\n对应音频URL: {audio_streams[0]['baseUrl']}")
                    print(f"音频编码: {audio_streams[0]['codecs']}")

                print("\n下载示例:")
                print(
                    f"视频: curl -o video_{quality_id}.mp4 '{stream['baseUrl']}' -H 'Referer: https://www.bilibili.com'")
                if audio_streams:
                    print(
                        f"音频: curl -o audio_{quality_id}.m4a '{audio_streams[0]['baseUrl']}' -H 'Referer: https://www.bilibili.com'")
                    print(
                        f"合并: ffmpeg -i video_{quality_id}.mp4 -i audio_{quality_id}.m4a -c copy output_{quality_id}.mp4")
                print("-" * 50)

        elif 'durl' in play_data['data']:
            # 旧式FLV格式
            print("警告: 视频使用旧式FLV格式，可能只有一种清晰度")
            for i, durl in enumerate(play_data['data']['durl']):
                print(f"\n分段 {i + 1}:")
                print(f"视频URL: {durl['url']}")
                print(f"大小: {durl['size'] // 1024 // 1024}MB")
                print(f"时长: {durl['length']}ms")
                print("\n下载示例:")
                print(f"curl -o video_part{i + 1}.flv '{durl['url']}' -H 'Referer: https://www.bilibili.com'")
                print("-" * 50)
        else:
            print("错误: 无法识别的视频流格式")

    except requests.exceptions.RequestException as e:
        print(f"\n请求失败: {str(e)}")
        print("可能的原因：")
        print("- 网络连接问题")
        print("- B站服务器拒绝请求")
        print("- 需要添加Cookie（大会员视频）")
    except json.JSONDecodeError:
        print("\n错误：API返回的数据不是有效的JSON格式")
        print("原始响应内容：")
        print(info_resp.text if 'info_resp' in locals() else play_resp.text)
    except KeyError as e:
        print(f"\n错误：解析API返回数据时缺少关键字段: {str(e)}")
        print("可能是B站API结构发生了变化")


if __name__ == "__main__":
    bvid = "BV1LNtdzvEsj"
    debug_bilibili_api(bvid)