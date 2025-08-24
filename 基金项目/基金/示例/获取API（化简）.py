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

        # 2. 获取视频流信息
        play_url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&fnval=16"
        print("\n=== 视频流信息API ===")
        print(f"请求URL: {play_url}")

        play_resp = requests.get(play_url, headers=headers, timeout=10)
        play_resp.raise_for_status()
        play_data = play_resp.json()

        print(json.dumps(play_data, indent=2, ensure_ascii=False))

        # 3. 提取关键清晰度信息
        if play_data['code'] == 0:
            print("\n=== 解析后的清晰度选项 ===")
            for q in play_data['data']['support_formats']:
                print(
                    f"标签: {q['quality']}, 清晰度: {q['new_description']}")

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


if __name__ == "__main__":
    bvid = "BV1LNtdzvEsj"
    debug_bilibili_api(bvid)