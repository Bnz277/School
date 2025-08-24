import random
import time
from tkinter.messagebox import RETRY
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
from scrapy.settings.default_settings import RETRY_TIMES


class BaiduSearchSpider:

    def __init__(self):
        self.delay_range = (1.5, 4)
        self.headers = {
            'User-Agent': self._get_random_ua(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()

    def _get_random_ua(self):
        uas = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/129.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
        ]
        return random.choice(uas)

    def _get_soup(self, url, params=None):
        try:
            time.sleep(random.uniform(*self.delay_range))
            self.headers['User-Agent'] = self._get_random_ua()
            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            if response.status_code != 200:
                print(f"❌ HTTP {response.status_code}")
                return None

            # 检查是否被反爬
            suspicious = ["验证码", "安全验证", "请在浏览器中打开", "加载中", "人机识别"]
            if any(s in response.text for s in suspicious):
                print("⚠️ 可能触发反爬机制")
                return None

            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"⚠️ 请求失败: {url} | 错误: {e}")
            return None

    def _extract_real_url(self, link):
        if link.startswith('/link?url='):
            try:
                return unquote(link.split('/link?url=')[1].split('&')[0])
            except:
                return link
        elif link.startswith('http'):
            return link
        else:
            return f"https://www.baidu.com{link}"

    def _find_all_title_links(self, soup):
        selectors = [
            'h3 a[href]',
            '.c-container h3 a',
            'div[data-click] h3 a',
            '.title-content a',
            '.result a[href]',
            '.t a'
        ]
        links = []
        for sel in selectors:
            links.extend(soup.select(sel))
        seen = set()
        unique = []
        for a in links:
            href = a.get('href')
            if href and href not in seen:
                unique.append(a)
                seen.add(href)
        return unique

    def search(self, keyword, max_results=10, max_pages=3, retry_times=3):
        results = []
        base_url = "https://www.baidu.com/s"
        params = {'wd': keyword}

        # 预热：访问百度首页
        try:
            self.session.get("https://www.baidu.com", headers=self.headers, timeout=10)
        except:
            pass

        for attempt in range(retry_times):
            print(f"🔍 第 {attempt + 1} 次尝试获取 '{keyword}' 的搜索结果...")
            results.clear()

            for page in range(max_pages):
                pn = page * 10
                params['pn'] = pn
                print(f"  📄 正在获取第 {page + 1} 页 (pn={pn})...")

                soup = self._get_soup(base_url, params=params)
                if not soup:
                    break

                a_tags = self._find_all_title_links(soup)
                print(f"    ➕ 本页找到 {len(a_tags)} 个标题链接")

                for a in a_tags:
                    title = a.get_text(strip=True)
                    href = a.get('href')
                    if not title or not href or len(title) < 2:
                        continue
                    real_url = self._extract_real_url(href)

                    # 过滤无效链接
                    if any(x in real_url.lower() for x in ['javascript:', 'baidu.com/ss?', 'tieba.baidu.com']):
                        continue

                    if real_url not in [r['real_url'] for r in results]:
                        results.append({
                            'index': len(results) + 1,
                            'title': title,
                            'real_url': real_url,
                        })

                    if len(results) >= max_results:
                        print(f"✅ 已获取到 {len(results)} 条结果，满足要求！")
                        return results

            if len(results) < max_results:
                print(f"⚠️ 当前仅获取 {len(results)} 条，不足 {max_results}，准备重试...")
                time.sleep(random.uniform(3, 6))
                continue

            break  # 成功获取足够结果，退出

        return results[:max_results]


if __name__ == "__main__":
    spider = BaiduSearchSpider()
    SEARCH_KEYWORD = "python"
    MAX_RESULTS = 35
    MAX_PAGES = 10
    RETRY_TIMES = 3

    print(f"🚀 开始搜索: '{SEARCH_KEYWORD}'，目标 {MAX_RESULTS} 条结果\n")
    results = spider.search(SEARCH_KEYWORD, max_results=MAX_RESULTS, max_pages=MAX_PAGES, retry_times=RETRY_TIMES)

    print("\n" + "=" * 60)
    print(f"✅ 搜索完成！共获取 {len(results)} 条结果")
    print("=" * 60)

    if results:
        for r in results:
            print(f"\n【{r['index']}】{r['title']}")
            print(f"🔗 {r['real_url']}")
    else:
        print("❌ 未获取到任何结果，请检查网络或是否被反爬")

    print("\n🔚 程序结束。")
