import random
import time
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


class BaiduSpider:
    """百度搜索引擎爬虫"""

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
    ]

    def __init__(self):
        self.delay_range = (1, 3)  # 随机延迟范围(秒)
        self.headers = {
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.baidu.com/'
        }

    def _get_soup(self, url):
        """获取BeautifulSoup对象"""
        try:
            time.sleep(random.uniform(*self.delay_range))
            headers = {**self.headers, 'User-Agent': random.choice(self.USER_AGENTS)}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"请求失败: {url} | 错误: {e}")
            return None

    def search(self, keyword, max_results=10, search_type='web'):
        """
        执行百度搜索

        参数:
            keyword (str): 搜索关键词
            max_results (int): 最大结果数量，默认为10
            search_type (str): 搜索类型，'web'为网页搜索，'image'为图片搜索

        返回:
            list: 搜索结果列表，每个元素是包含title和url的字典
        """
        encoded_keyword = quote(keyword)
        
        if search_type == 'image':
            url = f"https://image.baidu.com/search/index?tn=baiduimage&word={encoded_keyword}"
            print(f"🖼️ 正在百度图片搜索: {keyword} (最多{max_results}条)")
            return self._search_images(url, max_results)
        else:
            url = f"https://www.baidu.com/s?wd={encoded_keyword}"
            print(f"🔍 正在百度搜索: {keyword} (最多{max_results}条)")
            return self._search_web(url, max_results)

    def _search_web(self, url, max_results):
        """执行网页搜索"""
        soup = self._get_soup(url)
        if not soup:
            return []

        results = []
        for i, result in enumerate(soup.find_all("div", class_="result")[:max_results], 1):
            try:
                title = result.find("h3").get_text(strip=True)
                link = result.find("a")["href"]

                if not link.startswith(('http://', 'https://')):
                    continue

                results.append({
                    'index': i,
                    'title': title,
                    'url': link,
                    'type': 'web'  # 标识数据类型
                })

            except Exception as e:
                print(f"解析第{i}条结果时出错: {str(e)}")
                continue

        return results

    def _search_images(self, url, max_results):
        """执行图片搜索"""
        soup = self._get_soup(url)
        if not soup:
            return []

        results = []
        # 查找图片元素
        img_items = soup.find_all('img', src=True)[:max_results]
        
        for i, img in enumerate(img_items, 1):
            try:
                img_url = img.get('src') or img.get('data-src')
                if not img_url or not img_url.startswith(('http://', 'https://')):
                    continue
                    
                # 获取图片标题或alt文本
                title = img.get('alt') or img.get('title') or f'图片{i}'
                
                # 获取原图链接（如果有）
                parent_link = img.find_parent('a')
                original_url = parent_link.get('href') if parent_link else img_url
                
                results.append({
                    'index': i,
                    'title': title,
                    'url': original_url,
                    'thumbnail': img_url,
                    'type': 'image'  # 标识数据类型
                })

            except Exception as e:
                print(f"解析第{i}张图片时出错: {str(e)}")
                continue

        return results


if __name__ == "__main__":
    spider = BaiduSpider()
    search_term = "人工智能"
    results = spider.search(search_term, max_results=10)

    print("\n=== 百度搜索结果 ===")
    for item in results:
        print(f"\n【{item['index']}】{item['title']}")
        print(f"🔗 {item['url']}")
    print(f"\n✅ 共找到 {len(results)} 条结果")
