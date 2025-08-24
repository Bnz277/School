# -*- coding: utf-8 -*-
import sys
import urllib.request
import urllib.error
import socket
from urllib.parse import urlparse
import ssl
import chardet
from bs4 import BeautifulSoup
import re

# 禁用SSL证书验证 (仅用于测试，生产环境应使用有效证书)
ssl._create_default_https_context = ssl._create_unverified_context


class WebContentExtractor:
    def __init__(self):
        # 设置默认请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        }

        # 设置超时时间(秒)
        self.timeout = 10

        # 支持的协议
        self.supported_schemes = ['http', 'https']

    def get_web_content(self, url):
        """获取网页主要内容(文本和图片)"""
        if not self._validate_url(url):
            return None, "无效的URL"

        try:
            # 创建请求对象
            req = urllib.request.Request(url, headers=self.headers)

            # 发送请求
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                # 自动检测编码
                raw_data = response.read()
                encoding = self._detect_encoding(raw_data, response.headers)

                try:
                    html_content = raw_data.decode(encoding, errors='replace')
                except UnicodeDecodeError:
                    # 如果检测的编码无效，尝试常见编码
                    for enc in ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']:
                        try:
                            html_content = raw_data.decode(enc)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        html_content = raw_data.decode('utf-8', errors='replace')

                # 使用BeautifulSoup提取主要内容
                return self._extract_main_content(html_content, url), None

        except urllib.error.HTTPError as e:
            return None, f"HTTP错误: {e.code} {e.reason}"
        except urllib.error.URLError as e:
            return None, f"URL错误: {str(e)}"
        except socket.timeout:
            return None, "连接超时"
        except Exception as e:
            return None, f"未知错误: {str(e)}"

    def _extract_main_content(self, html, base_url):
        """提取网页主要内容"""
        soup = BeautifulSoup(html, 'html.parser')

        # 移除不需要的标签
        for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'noscript']):
            element.decompose()

        # 提取标题
        title = soup.title.string if soup.title else "无标题"

        # 提取正文内容 - 尝试找到最可能包含正文的标签
        main_content = ""

        # 尝试常见的正文容器
        for tag in ['article', 'main', '.content', '.post', '.article']:
            elements = soup.select(tag)
            if elements:
                main_content = "\n\n".join([e.get_text(separator="\n", strip=True) for e in elements])
                break

        # 如果没有找到特定标签，尝试获取body内容
        if not main_content:
            main_content = soup.body.get_text(separator="\n", strip=True) if soup.body else ""

        # 清理多余的空行和空格
        main_content = re.sub(r'\n\s*\n', '\n\n', main_content).strip()

        # 提取图片
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                if not src.startswith(('http://', 'https://')):
                    src = urllib.parse.urljoin(base_url, src)
                alt = img.get('alt', '无描述')
                images.append(f"[图片: {alt} - {src}]")

        # 组合结果
        result = f"标题: {title}\n\n{main_content}"
        if images:
            result += "\n\n网页包含以下图片:\n" + "\n".join(images)

        return result

    def _validate_url(self, url):
        """验证URL是否有效"""
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False
            if result.scheme.lower() not in self.supported_schemes:
                return False
            return True
        except:
            return False

    def _detect_encoding(self, content, headers):
        """检测内容的编码"""
        # 1. 首先检查HTTP头中的Content-Type
        content_type = headers.get('Content-Type', '')
        if 'charset=' in content_type:
            return content_type.split('charset=')[-1].strip()

        # 2. 使用chardet检测
        detected = chardet.detect(content)
        if detected['confidence'] > 0.9:
            return detected['encoding']

        # 3. 默认返回utf-8
        return 'utf-8'

    def save_to_file(self, content, filename):
        """保存内容到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, None
        except Exception as e:
            return False, str(e)


def main():
    print("=== 网页内容提取器 ===")
    print("支持HTTP/HTTPS协议，输入exit退出程序")

    extractor = WebContentExtractor()

    while True:
        url = input("\n请输入要提取内容的URL: ").strip()

        if url.lower() in ['exit', 'quit']:
            break

        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        print(f"\n正在获取: {url}")

        content, error = extractor.get_web_content(url)

        if error:
            print(f"❌ 获取内容失败: {error}")
            continue

        print("\n=== 获取成功 ===")
        print(f"内容长度: {len(content)} 字符")
        print("\n前200字符预览:")
        print(content[:200] + ("..." if len(content) > 200 else ""))

        save = input("\n是否保存到文件? (y/n): ").lower()
        if save == 'y':
            filename = input("输入文件名(默认: content.txt): ").strip() or "content.txt"
            success, error = extractor.save_to_file(content, filename)
            if success:
                print(f"✅ 内容已保存到 {filename}")
            else:
                print(f"❌ 保存失败: {error}")


if __name__ == "__main__":
    # 设置系统默认编码
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"程序异常: {str(e)}")