# -*- coding: utf-8 -*-
"""
模块说明:
    BilibiliSpider - B站搜索爬虫，保持与原测试版本接口一致:
    - class BilibiliSpider
        - search(keyword: str, max_results: int = 10) -> list[dict]
"""

import random
import time
from urllib.parse import quote

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

    def _get_soup(self, url: str):
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
            title_elem = item.find('a', {'title': True}) or item.find('h3', {'title': True})
            title = title_elem['title'] if title_elem else '无标题'

            link_elem = item.find('a', href=True)
            video_url = 'https:' + link_elem['href'] if link_elem and link_elem['href'].startswith('//') else ''

            img_elem = item.find('img') or item.find('picture img')
            thumbnail = ''
            if img_elem:
                thumbnail = img_elem.get('data-src') or img_elem.get('src') or ''
                if thumbnail and thumbnail.startswith('//'):
                    thumbnail = 'https:' + thumbnail

            up_elem = item.find(class_='up-name') or item.find(class_='bili-video-card__info--author')
            up_name = up_elem.text.strip() if up_elem else '未知UP主'

            play_elem = item.find(title='观看') or item.find(class_='play') or item.find(
                class_='bili-video-card__stats--item')
            play_count = play_elem.text.strip() if play_elem else '0'

            duration_elem = item.find(class_='length') or item.find(class_='bili-video-card__stats__duration')
            duration = duration_elem.text.strip() if duration_elem else ''

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
                'type': 'video'
            }
        except Exception as e:
            print(f"解析视频失败: {e}")
            return None

    def search(self, keyword: str, max_results: int = 10):
        """
        执行B站视频搜索
        返回 list[dict]，包含 index/title/url/thumbnail/up/play/duration/publish_time
        """
        base_url = f'https://search.bilibili.com/all?keyword={quote(keyword)}'
        soup = self._get_soup(base_url)
        if not soup:
            return []

        video_items = soup.select('li.video-item, div.bili-video-card, div.video-list__item')
        if not video_items:
            print("⚠️ 未找到视频元素，可能页面结构已更新")
            return []

        results = []
        for i, item in enumerate(video_items[:max_results], 1):
            info = self._parse_video_item(item)
            if info:
                results.append({'index': i, **info})
        return results