#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试爬虫功能
验证分页检测和内容提取
"""

from school_policy_crawler import SchoolPolicyCrawler
import requests
from bs4 import BeautifulSoup


def test_page_detection():
    """测试分页检测功能"""
    print("=== 测试分页检测 ===")
    
    crawler = SchoolPolicyCrawler()
    
    # 获取第一页内容
    html_content = crawler.get_page_content(1)
    if html_content:
        total_pages = crawler.get_total_pages(html_content)
        print(f"检测到的总页数: {total_pages}")
        
        # 手动检查分页信息
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找所有可能的分页元素
        print("\n=== 分页元素分析 ===")
        
        # 查找所有链接
        all_links = soup.find_all('a')
        page_links = []
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # 检查是否是页码链接
            if 'list_17_727_' in href and '.htm' in href:
                page_links.append({
                    'text': text,
                    'href': href,
                    'class': link.get('class', [])
                })
            elif text.isdigit() and 1 <= int(text) <= 100:  # 合理的页码范围
                page_links.append({
                    'text': text,
                    'href': href,
                    'class': link.get('class', [])
                })
        
        print(f"找到 {len(page_links)} 个可能的页码链接:")
        for link in page_links[:10]:  # 只显示前10个
            print(f"  文本: '{link['text']}', 链接: {link['href']}, 类: {link['class']}")
        
        return total_pages
    else:
        print("无法获取页面内容")
        return 1


def test_single_page_parsing():
    """测试单页内容解析"""
    print("\n=== 测试单页内容解析 ===")
    
    crawler = SchoolPolicyCrawler()
    html_content = crawler.get_page_content(1)
    
    if html_content:
        articles = crawler.parse_page(html_content, 1)
        print(f"解析到 {len(articles)} 篇文章")
        
        # 显示前3篇文章的详细信息
        for i, article in enumerate(articles[:3], 1):
            print(f"\n文章 {i}:")
            print(f"  标题: {article['title']}")
            print(f"  URL: {article['url']}")
            print(f"  摘要: {article['summary'][:100]}..." if article['summary'] else "  摘要: 无")
            print(f"  发布时间: {article['publish_time']}")
        
        return len(articles)
    else:
        print("无法获取页面内容")
        return 0


def test_multiple_pages():
    """测试多页爬取"""
    print("\n=== 测试多页爬取 ===")
    
    crawler = SchoolPolicyCrawler()
    
    # 只爬取前2页进行测试
    crawler.crawl_all_pages(max_pages=2)
    
    print(f"总共爬取到 {len(crawler.all_data)} 篇文章")
    
    # 按页面分组统计
    from collections import defaultdict
    page_stats = defaultdict(int)
    for article in crawler.all_data:
        page_stats[article['page']] += 1
    
    for page, count in sorted(page_stats.items()):
        print(f"第 {page} 页: {count} 篇文章")
    
    return len(crawler.all_data)


def main():
    """主测试函数"""
    print("开始测试爬虫功能...\n")
    
    # 测试分页检测
    total_pages = test_page_detection()
    
    # 测试单页解析
    articles_count = test_single_page_parsing()
    
    # 测试多页爬取
    if total_pages > 1:
        total_articles = test_multiple_pages()
    else:
        print("\n只有一页内容，跳过多页测试")
        total_articles = articles_count
    
    print(f"\n=== 测试结果汇总 ===")
    print(f"检测到总页数: {total_pages}")
    print(f"单页解析文章数: {articles_count}")
    print(f"多页爬取总文章数: {total_articles}")
    
    if total_articles > 0:
        print("爬虫功能测试成功！")
    else:
        print("爬虫功能测试失败！")


if __name__ == "__main__":
    main()
