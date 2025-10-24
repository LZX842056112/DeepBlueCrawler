#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上海本地宝学校政策信息爬虫
爬取 http://sh.bendibao.com/news/list_17_727_1.htm 网站上的学校政策信息
包括所有分页内容
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import os
from urllib.parse import urljoin
import re


class SchoolPolicyCrawler:
    def __init__(self):
        self.base_url = "http://sh.bendibao.com/news/list_17_727_{}.htm"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.all_data = []
        
    def get_page_content(self, page_num):
        """获取指定页面的内容"""
        url = self.base_url.format(page_num)
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return response.text
            else:
                print(f"页面 {page_num} 请求失败，状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"页面 {page_num} 请求异常: {e}")
            return None
    
    def parse_page(self, html_content, page_num):
        """解析页面内容，提取学校政策信息"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        # 查找文章列表，根据网站结构可能需要调整选择器
        # 常见的文章列表选择器
        article_selectors = [
            '.list-article li',
            '.news-list li',
            '.list-content li',
            '.article-list li',
            'ul.list li',
            '.list-box li',
            '.news-box li'
        ]
        
        articles_list = None
        for selector in article_selectors:
            articles_list = soup.select(selector)
            if articles_list:
                print(f"使用选择器: {selector} 找到 {len(articles_list)} 篇文章")
                break
        
        if not articles_list:
            print(f"页面 {page_num} 未找到文章列表，尝试备用选择器...")
            # 尝试其他可能的选择器
            articles_list = soup.find_all('li', class_=re.compile(r'list|article|news|box'))
            if articles_list:
                print(f"使用备用选择器找到 {len(articles_list)} 篇文章")
            else:
                # 最后尝试查找所有包含链接的li元素
                articles_list = [li for li in soup.find_all('li') if li.find('a')]
                if articles_list:
                    print(f"使用通用选择器找到 {len(articles_list)} 篇文章")
        
        for article in articles_list:
            try:
                # 提取标题和URL
                title_element = article.find('a')
                if not title_element:
                    continue
                    
                title = title_element.get_text().strip()
                if not title:  # 如果标题为空，跳过
                    continue
                    
                relative_url = title_element.get('href')
                if relative_url:
                    full_url = urljoin(self.base_url.format(1), relative_url)
                else:
                    full_url = ""
                
                # 提取摘要 - 改进摘要提取逻辑
                summary = ""
                # 尝试多种可能的摘要元素
                summary_selectors = [
                    'p',
                    '.summary',
                    '.desc',
                    '.intro',
                    '.content',
                    '.text'
                ]
                
                for selector in summary_selectors:
                    summary_element = article.select_one(selector)
                    if summary_element:
                        summary_text = summary_element.get_text().strip()
                        if summary_text and summary_text != title:
                            summary = summary_text
                            break
                
                # 如果没有找到摘要，尝试从其他文本内容中提取
                if not summary:
                    all_text = article.get_text().strip()
                    # 移除标题和时间信息，剩下的作为摘要
                    lines = all_text.split('\n')
                    summary_lines = []
                    for line in lines:
                        line = line.strip()
                        if line and line != title and not re.search(r'\d{4}-\d{2}-\d{2}', line):
                            summary_lines.append(line)
                    if summary_lines:
                        summary = ' '.join(summary_lines[:2])  # 取前两行作为摘要
                
                # 提取发布时间 - 改进时间提取逻辑
                publish_time = ""
                time_selectors = [
                    '.time',
                    '.date',
                    '.publish-time',
                    '.pub-time',
                    'span[class*="time"]',
                    'span[class*="date"]'
                ]
                
                for selector in time_selectors:
                    time_element = article.select_one(selector)
                    if time_element:
                        time_text = time_element.get_text().strip()
                        if re.search(r'\d{4}-\d{2}-\d{2}', time_text):
                            publish_time = time_text
                            break
                
                # 如果没有找到时间，尝试从其他位置查找
                if not publish_time:
                    # 查找包含时间的span或其他元素
                    time_elements = article.find_all(string=re.compile(r'\d{4}-\d{2}-\d{2}|\d{2}:\d{2}'))
                    for elem in time_elements:
                        if re.search(r'\d{4}-\d{2}-\d{2}', elem):
                            publish_time = elem.strip()
                            break
                
                article_data = {
                    'title': title,
                    'url': full_url,
                    'summary': summary,
                    'publish_time': publish_time,
                    'page': page_num
                }
                
                articles.append(article_data)
                print(f"提取文章: {title}")
                
            except Exception as e:
                print(f"解析文章时出错: {e}")
                continue
        
        return articles
    
    def get_total_pages(self, html_content):
        """获取总页数"""
        if not html_content:
            return 1
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找分页信息 - 改进分页检测逻辑
        page_selectors = [
            '.page a',
            '.pagination a',
            '.pages a',
            '.page-num a',
            '.pager a'
        ]
        
        max_page = 1
        for selector in page_selectors:
            page_links = soup.select(selector)
            for link in page_links:
                try:
                    page_text = link.get_text().strip()
                    # 匹配数字页码
                    if page_text.isdigit():
                        page_num = int(page_text)
                        if page_num > max_page:
                            max_page = page_num
                    # 匹配"下一页"等文本中的页码
                    elif '下一页' in page_text or '末页' in page_text:
                        href = link.get('href', '')
                        # 从URL中提取页码
                        page_match = re.search(r'_(\d+)\.htm', href)
                        if page_match:
                            page_num = int(page_match.group(1))
                            if page_num > max_page:
                                max_page = page_num
                except Exception as e:
                    print(f"解析页码时出错: {e}")
                    continue
        
        # 如果没找到分页信息，尝试从URL模式推断
        if max_page == 1:
            # 查找是否有"下一页"按钮
            next_page_selectors = [
                'a:contains("下一页")',
                'a[title*="下一页"]',
                'a[class*="next"]'
            ]
            for selector in next_page_selectors:
                try:
                    next_link = soup.select_one(selector)
                    if next_link:
                        # 如果有下一页，说明至少还有第2页
                        max_page = 2
                        break
                except:
                    continue
        
        print(f"检测到总页数: {max_page}")
        return max_page
    
    def crawl_all_pages(self, start_page=1, max_pages=None):
        """爬取所有页面"""
        print("开始爬取学校政策信息...")
        
        # 先获取第一页来确定总页数
        first_page_html = self.get_page_content(start_page)
        if not first_page_html:
            print("无法获取第一页内容")
            return
        
        total_pages = self.get_total_pages(first_page_html)
        if max_pages and max_pages < total_pages:
            total_pages = max_pages
        
        print(f"准备爬取 {total_pages} 页")
        
        for page_num in range(start_page, total_pages + 1):
            print(f"\n正在爬取第 {page_num} 页...")
            
            html_content = self.get_page_content(page_num)
            if not html_content:
                print(f"第 {page_num} 页获取失败，跳过")
                continue
                
            articles = self.parse_page(html_content, page_num)
            self.all_data.extend(articles)
            
            print(f"第 {page_num} 页爬取完成，找到 {len(articles)} 篇文章")
            
            # 添加延迟避免请求过快
            time.sleep(1)
        
        print(f"\n爬取完成！总共获取 {len(self.all_data)} 篇文章")
    
    def save_to_json(self, filename="school_policies.json"):
        """保存数据到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到 {filename}")
    
    def save_to_csv(self, filename="school_policies.csv"):
        """保存数据到CSV文件"""
        import csv
        
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            if self.all_data:
                fieldnames = self.all_data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.all_data)
        print(f"数据已保存到 {filename}")
    
    def display_summary(self):
        """显示爬取结果摘要"""
        if not self.all_data:
            print("没有爬取到数据")
            return
        
        print(f"\n=== 爬取结果摘要 ===")
        print(f"总文章数: {len(self.all_data)}")
        
        # 按页面统计
        pages = set(item['page'] for item in self.all_data)
        print(f"爬取页面数: {len(pages)}")
        
        # 显示前5篇文章
        print(f"\n前5篇文章:")
        for i, article in enumerate(self.all_data[:5], 1):
            print(f"{i}. {article['title']}")
            print(f"   发布时间: {article['publish_time']}")
            print(f"   摘要: {article['summary'][:50]}..." if article['summary'] else "   摘要: 无")
            print()


def main():
    """主函数"""
    crawler = SchoolPolicyCrawler()
    
    # 爬取所有页面
    crawler.crawl_all_pages()
    
    # 显示摘要
    crawler.display_summary()
    
    # 保存数据
    crawler.save_to_json()
    crawler.save_to_csv()
    
    print("爬虫任务完成！")


if __name__ == "__main__":
    main()
