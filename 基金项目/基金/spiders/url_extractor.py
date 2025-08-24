# -*- coding: utf-8 -*-
"""
模块说明:
    WebContentExtractor - 通用网页内容提取器（增强版）
    - class WebContentExtractor
        - get_web_content(url: str) -> tuple[str, str|None]
          返回 (content, error)；成功时 error 为 None
        - extract_page_title(html: str) -> str
          提取网页标题
        - extract_text_content(html: str) -> str
          提取纯文本内容（移除HTML标签）
        - extract_images(html: str, base_url: str) -> list
          提取图片链接
说明:
    - 增强内容解析能力，提供更好的结构化结果
    - 支持标题提取、图片链接提取、纯文本内容提取
    - 保持依赖最小化，仅使用 requests 和 re
"""

import requests
import re
from urllib.parse import urljoin, urlparse


class WebContentExtractor:
    """网页内容提取器（增强版）"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_web_content(self, url: str):
        """
        获取网页内容并解析结构化信息
        参数:
            url: 目标URL
        返回:
            (content, error): content为结构化内容信息，error为错误信息（无错误返回None）
        """
        try:
            resp = requests.get(url, headers=self.headers, timeout=15)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or resp.encoding or 'utf-8'
            
            html_content = resp.text
            
            # 提取结构化信息
            title = self.extract_page_title(html_content)
            text_content = self.extract_text_content(html_content)
            images = self.extract_images(html_content, url)
            
            # 构建结构化内容
            structured_content = {
                'title': title,
                'url': url,
                'text_length': len(text_content),
                'images_count': len(images),
                'preview': text_content[:500] + '...' if len(text_content) > 500 else text_content,
                'full_content': text_content,
                'images': images[:10],  # 最多返回前10张图片
                'metadata': {
                    'content_type': resp.headers.get('content-type', ''),
                    'status_code': resp.status_code,
                    'final_url': resp.url,
                    'charset': resp.encoding or 'utf-8'
                }
            }
            
            return structured_content, None
            
        except Exception as e:
            return None, f"获取网页内容失败: {e}"

    def extract_page_title(self, html: str) -> str:
        """提取网页标题"""
        try:
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            if title_match:
                title = title_match.group(1).strip()
                # 清理HTML实体
                title = re.sub(r'&\w+;', '', title)
                return title[:100]  # 限制标题长度
            return "无标题"
        except:
            return "无标题"

    def extract_text_content(self, html: str) -> str:
        """提取纯文本内容（移除HTML标签）"""
        try:
            # 移除script和style标签及其内容
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
            
            # 移除所有HTML标签
            text = re.sub(r'<[^>]+>', '', html)
            
            # 清理多余的空白字符
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        except:
            return ""

    def extract_images(self, html: str, base_url: str) -> list:
        """提取图片链接"""
        try:
            images = []
            img_pattern = r'<img[^>]*src\s*=\s*["\']([^"\']+)["\'][^>]*>'
            matches = re.findall(img_pattern, html, re.IGNORECASE)
            
            for img_src in matches:
                # 转换为绝对URL
                absolute_url = urljoin(base_url, img_src)
                
                # 过滤常见的无效图片
                if not self._is_valid_image_url(absolute_url):
                    continue
                    
                images.append(absolute_url)
                
                # 限制图片数量，避免过多
                if len(images) >= 20:
                    break
                    
            return images
        except:
            return []

    def _is_valid_image_url(self, url: str) -> bool:
        """检查是否为有效的图片URL"""
        try:
            parsed = urlparse(url)
            # 检查URL格式
            if not parsed.scheme or not parsed.netloc:
                return False
                
            # 过滤常见的无效图片
            invalid_patterns = [
                'data:image',  # Base64图片
                'placeholder',  # 占位图片
                'loading.gif',  # 加载图片
                'spacer.gif',   # 间隔图片
                '1x1.gif',      # 1像素图片
            ]
            
            url_lower = url.lower()
            for pattern in invalid_patterns:
                if pattern in url_lower:
                    return False
                    
            # 检查图片扩展名（可选）
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
            path_lower = parsed.path.lower()
            
            # 如果有明确的图片扩展名，则认为有效
            if any(path_lower.endswith(ext) for ext in image_extensions):
                return True
                
            # 如果URL包含图片相关关键词，也认为可能有效
            image_keywords = ['image', 'img', 'photo', 'pic']
            if any(keyword in url_lower for keyword in image_keywords):
                return True
                
            # 其他情况也认为可能有效（让前端判断）
            return True
            
        except:
            return False