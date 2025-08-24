from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import random


def create_driver():
    options = Options()
    options.add_argument("--headless=new")  # 无头模式运行（后台静默）
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => false
            });
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
        """
    })
    return driver


def get_baidu_results(keyword, target_count=50, max_pages=10):
    """
    爬取百度搜索结果，直到达到目标数量
    :param keyword: 搜索关键词
    :param target_count: 目标结果数量
    :param max_pages: 最大翻页数（防止无限翻页）
    :return: 结果列表
    """
    driver = create_driver()
    results = []
    page = 0

    try:
        while len(results) < target_count and page < max_pages:
            pn = page * 10
            url = f"https://www.baidu.com/s?wd={keyword}&pn={pn}"
            print(f"📄 正在打开第 {page + 1} 页 (pn={pn}): {url}")

            driver.get(url)

            # 等待搜索结果容器加载
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "content_left"))
                )
            except TimeoutException:
                print("⚠️ 页面加载超时，可能是反爬或网络问题")
                time.sleep(5)
                page += 1
                continue

            # 模拟人类浏览
            time.sleep(random.uniform(2.0, 4.0))

            # 提取链接
            try:
                items = driver.find_elements(By.CSS_SELECTOR, "#content_left .c-container h3 a, #content_left h3 a")
                print(f"✅ 本页找到 {len(items)} 个结果")

                for item in items:
                    try:
                        title = item.text.strip()
                        href = item.get_attribute("href")
                        if title and href and len(title) > 2:
                            # 去重：避免重复添加
                            if href not in [r['链接'] for r in results]:
                                results.append({
                                    "序号": len(results) + 1,
                                    "标题": title,
                                    "链接": href
                                })
                    except StaleElementReferenceException:
                        continue

                print(f"📊 当前累计已获取 {len(results)} 条结果")

            except Exception as e:
                print(f"❌ 提取元素失败: {e}")

            page += 1

            # 如果连续两页都没新结果，提前退出
            if page >= 2 and len(results) < page * 8:  # 平均每页少于8条，可能到底了
                print("⚠️ 连续页面结果稀少，可能已到底部，提前结束")
                break

            # 随机延迟，更像人类
            time.sleep(random.uniform(1.5, 3.0))

    finally:
        driver.quit()

    return results[:target_count]  # 确保不多于目标数量


if __name__ == "__main__":
    keyword = "南阳理工学院"
    TARGET_COUNT = 89  # 目标爬取结果数
    MAX_PAGES = 20     # 最大翻页数

    print(f"🚀 开始搜索: '{keyword}'，目标获取 {TARGET_COUNT} 条结果")
    data = get_baidu_results(keyword, target_count=TARGET_COUNT, max_pages=MAX_PAGES)

    print(f"\n{'='*60}")
    if data:
        print(f"✅ 成功获取 {len(data)} 条结果，内容如下：\n")
        for item in data:
            print(f"{item['序号']:>2}、{item['标题']}")
            print(f"     🔗 {item['链接']}\n")
    else:
        print("❌ 未获取到任何结果，请检查网络、关键词或反爬机制。")
    print(f"{'='*60}")