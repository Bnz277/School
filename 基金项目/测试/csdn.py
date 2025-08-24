import random
import re
import time
from urllib.parse import quote

import requests


class CSDNSpider:
    """CSDN搜索爬虫"""

    def __init__(self):
        self.delay_range = (1, 3)  # 随机延迟范围(秒)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'Referer': 'https://so.csdn.net/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1'
        }

    def _clean_html_tags(self, text):
        """清除HTML标签"""
        if not text:
            return text
        return re.sub(r'<[^>]+>', '', text)

    def _get_json(self, url):
        """获取JSON数据"""
        try:
            time.sleep(random.uniform(*self.delay_range))
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"请求失败: {url} | 错误: {e}")
            return None

    def _parse_article(self, article):
        """解析单篇文章数据"""
        try:
            return {
                'id': article.get('id', ''),
                'title': self._clean_html_tags(article.get('title', '无标题')),
                'author': self._clean_html_tags(article.get('nickname', '未知作者')),
                'url': article.get('url_location', ''),
                'views': article.get('view_num', 0),
                'comments': article.get('comment', 0),
                'likes': article.get('digg', 0),
                'create_time': article.get('created_at', '')
            }
        except Exception as e:
            print(f"解析文章失败: {e}")
            return None

    def search(self, keyword, max_results=10):
        """
        执行CSDN搜索

        参数:
            keyword (str): 搜索关键词
            max_results (int): 最大结果数量

        返回:
            list: 搜索结果列表，每个元素是包含文章信息的字典
        """
        base_url = f'https://so.csdn.net/api/v3/search?q={quote(keyword)}&t=all'
        print(f"🔍 正在CSDN搜索: {keyword} (最多{max_results}条)")

        results = []
        page = 1
        per_page = 10  # 每页默认结果数

        while len(results) < max_results:
            url = f"{base_url}&p={page}"
            data = self._get_json(url)

            if not data or 'result_vos' not in data:
                break

            for article in data['result_vos']:
                if len(results) >= max_results:
                    break

                parsed = self._parse_article(article)
                if parsed:
                    results.append({
                        'index': len(results) + 1,
                        **parsed
                    })

            # 如果没有更多结果或已经达到最大数量，停止翻页
            if not data['result_vos'] or len(results) >= max_results:
                break

            page += 1

        return results


if __name__ == "__main__":
    spider = CSDNSpider()
    search_term = "python"
    results = spider.search(search_term, max_results=15)

    print("\n=== CSDN搜索结果 ===")
    for item in results:
        print(f"\n【{item['index']}】{item['title']}")
        print(f"👤 作者: {item['author']}")
        print(f"🔗 链接: {item['url']}")
        print(f"👀 浏览量: {item['views']}")
        print(f"💬 评论: {item['comments']}")
        print(f"👍 点赞: {item['likes']}")
        print(f"⏱️ 发布时间: {item['create_time']}")
    print(f"\n✅ 共找到 {len(results)} 条结果")
