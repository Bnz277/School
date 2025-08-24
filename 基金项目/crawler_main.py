#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络信息爬取系统 - 命令行版本
整合百度、B站、CSDN和自定义URL爬虫功能
"""

import sys
import os
import json
import time
from datetime import datetime

# 导入各个爬虫模块
sys.path.append(os.path.join(os.path.dirname(__file__), '测试'))

try:
    from baidu import BaiduSpider
    from bilibili import BilibiliSpider
    from csdn import CSDNSpider
    from url import WebContentExtractor
except ImportError as e:
    print(f"❌ 导入爬虫模块失败: {e}")
    print("请确保测试文件夹中包含所有爬虫文件")
    sys.exit(1)


class CrawlerManager:
    """爬虫管理器"""
    
    def __init__(self):
        self.spiders = {
            '1': {'name': '百度搜索', 'class': BaiduSpider, 'type': 'search'},
            '2': {'name': 'B站视频', 'class': BilibiliSpider, 'type': 'search'},
            '3': {'name': 'CSDN文章', 'class': CSDNSpider, 'type': 'search'},
            '4': {'name': '自定义URL', 'class': WebContentExtractor, 'type': 'url'}
        }
        
    def show_banner(self):
        """显示程序横幅"""
        print("\n" + "="*60)
        print("           🕷️  网络信息爬取系统  🕷️")
        print("="*60)
        print("支持多平台数据采集，智能内容提取")
        print("版本: 1.0.0 | 开发: NYLG Team")
        print("="*60)
        
    def show_menu(self):
        """显示主菜单"""
        print("\n📋 请选择爬虫类型:")
        print("-" * 30)
        for key, spider in self.spiders.items():
            icon = "🔍" if spider['type'] == 'search' else "🌐"
            print(f"  {key}. {icon} {spider['name']}")
        print("  0. 🚪 退出程序")
        print("-" * 30)
        
    def get_search_params(self, spider_name):
        """获取搜索参数"""
        print(f"\n🔧 配置 {spider_name} 爬取参数:")
        
        keyword = input("🔍 请输入搜索关键词: ").strip()
        if not keyword:
            print("❌ 关键词不能为空")
            return None
            
        while True:
            try:
                max_results = input("📊 最大结果数量 (默认10): ").strip()
                max_results = int(max_results) if max_results else 10
                if max_results <= 0:
                    print("❌ 结果数量必须大于0")
                    continue
                break
            except ValueError:
                print("❌ 请输入有效的数字")
                
        return {'keyword': keyword, 'max_results': max_results}
        
    def get_url_params(self):
        """获取URL爬取参数"""
        print("\n🔧 配置自定义URL爬取参数:")
        
        url = input("🌐 请输入目标URL: ").strip()
        if not url:
            print("❌ URL不能为空")
            return None
            
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        return {'url': url}
        
    def execute_search_spider(self, spider_class, params):
        """执行搜索类爬虫"""
        try:
            spider = spider_class()
            print(f"\n🚀 开始爬取...")
            start_time = time.time()
            
            results = spider.search(params['keyword'], params['max_results'])
            
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            
            if results:
                print(f"\n✅ 爬取完成! 耗时: {duration}秒")
                print(f"📊 共获取 {len(results)} 条结果")
                return results
            else:
                print(f"\n⚠️ 未获取到任何结果")
                return []
                
        except Exception as e:
            print(f"\n❌ 爬取失败: {str(e)}")
            return None
            
    def execute_url_spider(self, spider_class, params):
        """执行URL爬虫"""
        try:
            spider = spider_class()
            print(f"\n🚀 开始爬取: {params['url']}")
            start_time = time.time()
            
            content, error = spider.get_web_content(params['url'])
            
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            
            if error:
                print(f"\n❌ 爬取失败: {error}")
                return None
            else:
                print(f"\n✅ 爬取完成! 耗时: {duration}秒")
                print(f"📊 内容长度: {len(content)} 字符")
                return content
                
        except Exception as e:
            print(f"\n❌ 爬取失败: {str(e)}")
            return None
            
    def display_search_results(self, results, spider_name):
        """显示搜索结果"""
        print(f"\n📋 {spider_name} 搜索结果:")
        print("=" * 50)
        
        for item in results:
            print(f"\n【{item.get('index', 'N/A')}】{item.get('title', '无标题')}")
            
            # 根据不同爬虫显示不同信息
            if 'author' in item:  # CSDN
                print(f"👤 作者: {item['author']}")
                print(f"👀 浏览: {item.get('views', 0)}")
                print(f"💬 评论: {item.get('comments', 0)}")
                print(f"👍 点赞: {item.get('likes', 0)}")
                if item.get('create_time'):
                    print(f"⏱️ 时间: {item['create_time']}")
            elif 'up' in item:  # B站
                print(f"👤 UP主: {item['up']}")
                print(f"👀 播放: {item.get('play', '0')}")
                if item.get('duration'):
                    print(f"⏱️ 时长: {item['duration']}")
                    
            print(f"🔗 链接: {item.get('url', '无链接')}")
            
        print(f"\n📊 总计: {len(results)} 条结果")
        
    def display_url_content(self, content):
        """显示URL内容"""
        print(f"\n📄 网页内容:")
        print("=" * 50)
        
        # 显示前500字符作为预览
        preview_length = 500
        if len(content) > preview_length:
            print(content[:preview_length])
            print(f"\n... (还有 {len(content) - preview_length} 字符)")
        else:
            print(content)
            
        print(f"\n📊 总长度: {len(content)} 字符")
        
    def save_results(self, data, spider_name, data_type='search'):
        """保存结果到文件"""
        save_choice = input("\n💾 是否保存结果到本地? (y/n): ").lower().strip()
        
        if save_choice != 'y':
            return
            
        # 创建保存目录
        save_dir = 'crawler_results'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if data_type == 'search':
            # 保存搜索结果为JSON
            filename = f"{save_dir}/{spider_name}_{timestamp}.json"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"✅ 搜索结果已保存到: {filename}")
            except Exception as e:
                print(f"❌ 保存失败: {str(e)}")
        else:
            # 保存网页内容为文本
            filename = f"{save_dir}/网页内容_{timestamp}.txt"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(data)
                print(f"✅ 网页内容已保存到: {filename}")
            except Exception as e:
                print(f"❌ 保存失败: {str(e)}")
                
    def run(self):
        """运行主程序"""
        self.show_banner()
        
        while True:
            self.show_menu()
            
            choice = input("\n请选择 (0-4): ").strip()
            
            if choice == '0':
                print("\n👋 感谢使用，再见!")
                break
                
            if choice not in self.spiders:
                print("\n❌ 无效选择，请重新输入")
                continue
                
            spider_info = self.spiders[choice]
            spider_name = spider_info['name']
            spider_class = spider_info['class']
            spider_type = spider_info['type']
            
            print(f"\n🎯 已选择: {spider_name}")
            
            # 获取参数
            if spider_type == 'search':
                params = self.get_search_params(spider_name)
                if not params:
                    continue
                    
                # 执行爬取
                results = self.execute_search_spider(spider_class, params)
                if results is None:
                    continue
                elif len(results) == 0:
                    print("\n💡 建议: 尝试更换关键词或检查网络连接")
                    continue
                    
                # 显示结果
                self.display_search_results(results, spider_name)
                
                # 保存结果
                self.save_results(results, spider_name, 'search')
                
            else:  # URL类型
                params = self.get_url_params()
                if not params:
                    continue
                    
                # 执行爬取
                content = self.execute_url_spider(spider_class, params)
                if content is None:
                    continue
                    
                # 显示结果
                self.display_url_content(content)
                
                # 保存结果
                self.save_results(content, spider_name, 'url')
                
            # 询问是否继续
            continue_choice = input("\n🔄 是否继续使用? (y/n): ").lower().strip()
            if continue_choice != 'y':
                print("\n👋 感谢使用，再见!")
                break


def main():
    """主函数"""
    try:
        # 设置控制台编码
        if sys.platform == 'win32':
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
            
        # 创建并运行爬虫管理器
        manager = CrawlerManager()
        manager.run()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 程序被用户中断")
    except Exception as e:
        print(f"\n\n❌ 程序异常: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()