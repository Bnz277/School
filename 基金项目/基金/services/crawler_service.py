from datetime import datetime
from typing import Tuple, Optional, List, Dict

from spiders.baidu_spider import BaiduSpider
from spiders.bilibili_spider import BilibiliSpider
from spiders.csdn_spider import CSDNSpider
from spiders.url_extractor import WebContentExtractor


class CrawlerService:
    """
    爬虫服务核心类（与原逻辑一致）
    - 管理爬虫类型
    - 统一搜索接口
    - URL 内容提取
    """

    def __init__(self):
        self.spiders = {
            'baidu': {'name': '百度搜索', 'class': BaiduSpider, 'type': 'search'},
            'bilibili': {'name': '哔哩哔哩', 'class': BilibiliSpider, 'type': 'search'},
            'csdn': {'name': 'CSDN', 'class': CSDNSpider, 'type': 'search'},
            'url': {'name': '自定义URL', 'class': WebContentExtractor, 'type': 'url'}
        }

    def execute_search(self, spider_type: str, keyword: str, max_results: int = 10, data_type: str = 'text') -> Tuple[Optional[List[Dict]], Optional[str]]:
        try:
            spider_info = self.spiders.get(spider_type)
            if not spider_info:
                return None, "不支持的爬虫类型"

            spider = spider_info['class']()

            if spider_type == 'baidu' and hasattr(spider, 'search'):
                search_type = 'image' if data_type == 'image' else 'web'
                results = spider.search(keyword, max_results, search_type)
            else:
                results = spider.search(keyword, max_results)

            return results, None
        except Exception as e:
            return None, str(e)

    def execute_url_extraction(self, url: str) -> Tuple[Optional[dict], Optional[str]]:
        """
        执行URL内容提取（修复：返回结构化数据）
        参数:
            url: 目标URL
        返回:
            (content_data, error): content_data为结构化内容字典，error为错误信息
        """
        try:
            extractor = WebContentExtractor()
            content_data, error = extractor.get_web_content(url)
            if error:
                return None, error
            return content_data, None
        except Exception as e:
            return None, str(e)