# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import time
import random
import os
from urllib.parse import unquote, urlparse

# ========================
# 配置区
# ========================
SEARCH_KEYWORD = "Python"  # 修改为你想搜的关键词
MAX_RESULTS = 40                     # 最多返回几条
MAX_PAGES = 10                       # 最多翻几页（每页约10条）
RETRY_TIMES = 3                      # 失败重试次数
SAVE_DEBUG_PAGE = True               # 是否保存失败页面用于调试


# ========================
# 工具函数
# ========================
def extract_real_url(link):
    """解析百度跳转链接，获取真实URL"""
    if link.startswith('/link?url='):
        try:
            return unquote(link.split('/link?url=')[1].split('&')[0])
        except:
            return link
    elif link.startswith('http'):
        return link
    else:
        return f"https://www.baidu.com{link}"


def get_random_ua():
    """返回随机User-Agent"""
    uas = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/129.0.0.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    ]
    return random.choice(uas)


def find_all_title_links(soup):
    """使用多种选择器查找所有标题链接"""
    selectors = [
        'h3 a[href]',                    # 主流
        '.c-container h3 a',             # 容器内
        'div[data-click] h3 a',          # 带点击数据
        '.title-content a',              # 新版内容
        '.result a[href]',               # 旧版
        '.t a',                          # 老版本
    ]
    links = []
    for sel in selectors:
        links.extend(soup.select(sel))
    # 去重
    seen = set()
    unique = []
    for a in links:
        href = a.get('href')
        if href and href not in seen:
            unique.append(a)
            seen.add(href)
    return unique


def save_debug_page(html, keyword, reason="unknown"):
    """保存页面用于调试"""
    filename = f"baidu_debug_{keyword}_{int(time.time())}_{reason}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ 调试页面已保存: {filename}")


# ========================
# 主搜索函数
# ========================
def baidu_search(keyword, max_results=10, max_pages=3, retry_times=3):
    session = requests.Session()
    results = []
    headers = {'User-Agent': get_random_ua()}

    for attempt in range(retry_times):
        print(f"🔍 第 {attempt + 1} 次尝试获取 '{keyword}' 的搜索结果...")

        try:
            # Step 1: 先访问百度首页，建立“正常用户”印象
            print("🌐 正在预访问百度首页...")
            session.get("https://www.baidu.com", headers=headers, timeout=10, allow_redirects=True)
            time.sleep(random.uniform(1.5, 3))

            # Step 2: 循环翻页
            for page in range(max_pages):
                pn = page * 10
                params = {'wd': keyword, 'pn': pn}
                headers['User-Agent'] = get_random_ua()  # 每页换UA

                print(f"  📄 正在获取第 {page + 1} 页 (pn={pn})...")
                response = session.get(
                    "https://www.baidu.com/s",
                    params=params,
                    headers=headers,
                    timeout=10
                )

                if response.status_code != 200:
                    print(f"    ❌ HTTP {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # 检查是否被反爬
                if any(s in response.text for s in ["验证码", "安全验证", "请在浏览器中打开", "加载中"]):
                    print(f"    ⚠️  被反爬拦截！尝试下一次...")
                    break  # 跳出翻页，进入下一次重试

                # 提取链接
                a_tags = find_all_title_links(soup)
                print(f"    ➕ 本页找到 {len(a_tags)} 个标题链接")

                for a in a_tags:
                    title = a.get_text(strip=True)
                    href = a.get('href')
                    if not title or not href or len(title) < 2:
                        continue
                    real_url = extract_real_url(href)
                    domain = urlparse(real_url).netloc

                    # 过滤无效链接
                    if any(x in real_url.lower() for x in ['javascript:', 'baidu.com/ss?', 'tieba.baidu.com']):
                        continue

                    # 去重
                    if real_url not in [r['real_url'] for r in results]:
                        results.append({
                            'index': len(results) + 1,
                            'title': title,
                            'real_url': real_url,
                            'domain': domain
                        })

                    if len(results) >= max_results:
                        print(f"✅ 已获取到 {len(results)} 条结果，满足要求！")
                        return results

                # 翻页延迟
                time.sleep(random.uniform(2, 4))

            # 如果本次尝试没满足要求，重试
            if len(results) < max_results:
                print(f"⚠️  当前仅获取 {len(results)} 条，不足 {max_results}，准备重试...")
                time.sleep(random.uniform(3, 6))
                continue

        except Exception as e:
            print(f"❌ 第 {attempt + 1} 次尝试出错: {e}")
            if SAVE_DEBUG_PAGE and 'response' in locals():
                save_debug_page(response.text, keyword, "error")
            time.sleep(3)

    # 最终返回（即使不足）
    return results[:max_results]


# ========================
# 主程序入口
# ========================
if __name__ == "__main__":
    print(f"🚀 开始搜索: '{SEARCH_KEYWORD}'，目标 {MAX_RESULTS} 条结果\n")

    results = baidu_search(
        keyword=SEARCH_KEYWORD,
        max_results=MAX_RESULTS,
        max_pages=MAX_PAGES,
        retry_times=RETRY_TIMES
    )

    # 输出结果
    print("\n" + "=" * 60)
    print(f"✅ 搜索完成！共获取 {len(results)} 条结果")
    print("=" * 60)

    if results:
        for r in results:
            print(f"\n【{r['index']}】{r['title']}")
            print(f"🔗 {r['real_url']}")
            print(f"🌐 {r['domain']}")
    else:
        print("❌ 未获取到任何结果，请检查：")
        print("   - 是否被反爬（建议换手机热点）")
        print("   - 网络是否正常")
        print("   - 关键词是否太冷门")
        if 'response' in locals():
            save_debug_page(response.text, SEARCH_KEYWORD, "no_results")

    print("\n🔚 程序结束。")