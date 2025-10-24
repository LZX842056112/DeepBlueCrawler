import requests
from bs4 import BeautifulSoup
import time
import json
import csv
from datetime import datetime
import re


class CnblogsSpider:
    def __init__(self):
        self.base_url = "https://www.cnblogs.com/pinard"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.blog_data = []
    
    def get_page_content(self, page_num):
        """获取指定页面的内容"""
        if page_num == 1:
            url = self.base_url
        else:
            url = f"{self.base_url}/default.html?page={page_num}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            print(f"获取第{page_num}页失败: {e}")
            return None
    
    def parse_blog_list(self, html_content):
        """解析博客列表页面，提取博客信息"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        blog_items = []
        
        # 根据实际网站结构，博客文章在div.day中
        day_divs = soup.find_all('div', class_='day')
        
        print(f"找到 {len(day_divs)} 个博客日期分组")
        
        for day_div in day_divs:
            try:
                blog_info = self.extract_blog_info(day_div)
                if blog_info:
                    blog_items.append(blog_info)
            except Exception as e:
                print(f"解析博客项时出错: {e}")
                continue
        
        return blog_items
    
    def extract_blog_info(self, day_div):
        """从单个博客项中提取信息"""
        blog = {}
        
        # 提取标题和链接 - 在postTitle div中
        title_div = day_div.find('div', class_='postTitle')
        if title_div:
            title_link = title_div.find('a')
            if title_link:
                blog['title'] = title_link.get_text().strip()
                blog['url'] = title_link.get('href', '')
            else:
                return None
        else:
            return None
        
        # 提取摘要 - 在postCon或c_b_p_desc div中
        summary_div = day_div.find('div', class_='postCon') or day_div.find('div', class_='c_b_p_desc')
        if summary_div:
            blog['summary'] = summary_div.get_text().strip()
        else:
            blog['summary'] = ''
        
        # 提取元信息（时间、阅读量、评论数、推荐数）- 在postDesc div中
        meta_div = day_div.find('div', class_='postDesc')
        if meta_div:
            meta_text = meta_div.get_text()
            
            # 提取时间
            time_match = re.search(r'posted @ (\d{4}-\d{2}-\d{2} \d{2}:\d{2})', meta_text)
            if time_match:
                blog['publish_time'] = time_match.group(1)
            else:
                blog['publish_time'] = ''
            
            # 提取阅读量
            read_match = re.search(r'阅读\((\d+)\)', meta_text)
            if read_match:
                blog['read_count'] = int(read_match.group(1))
            else:
                blog['read_count'] = 0
            
            # 提取评论数
            comment_match = re.search(r'评论\((\d+)\)', meta_text)
            if comment_match:
                blog['comment_count'] = int(comment_match.group(1))
            else:
                blog['comment_count'] = 0
            
            # 提取推荐数
            recommend_match = re.search(r'推荐\((\d+)\)', meta_text)
            if recommend_match:
                blog['recommend_count'] = int(recommend_match.group(1))
            else:
                blog['recommend_count'] = 0
        else:
            blog['publish_time'] = ''
            blog['read_count'] = 0
            blog['comment_count'] = 0
            blog['recommend_count'] = 0
        
        return blog
    
    def crawl_all_pages(self, total_pages=14):
        """爬取所有页面"""
        print(f"开始爬取 {total_pages} 页博客数据...")
        
        for page in range(1, total_pages + 1):
            print(f"正在爬取第 {page} 页...")
            
            html_content = self.get_page_content(page)
            if html_content:
                blog_items = self.parse_blog_list(html_content)
                self.blog_data.extend(blog_items)
                print(f"第 {page} 页爬取完成，获取到 {len(blog_items)} 篇博客")
            else:
                print(f"第 {page} 页爬取失败")
            
            # 添加延时，避免请求过于频繁
            time.sleep(2)
        
        print(f"爬取完成，总共获取到 {len(self.blog_data)} 篇博客")
    
    def save_to_json(self, filename=None):
        """保存数据到JSON文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cnblogs_pinard_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.blog_data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已保存到 {filename}")
        return filename
    
    def save_to_csv(self, filename=None):
        """保存数据到CSV文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cnblogs_pinard_data_{timestamp}.csv"
        
        if not self.blog_data:
            print("没有数据可保存")
            return
        
        fieldnames = ['title', 'publish_time', 'read_count', 'comment_count', 'recommend_count', 'summary', 'url']
        
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.blog_data)
        
        print(f"数据已保存到 {filename}")
        return filename
    
    def display_summary(self):
        """显示数据摘要"""
        if not self.blog_data:
            print("没有数据")
            return
        
        total_reads = sum(blog['read_count'] for blog in self.blog_data)
        total_comments = sum(blog['comment_count'] for blog in self.blog_data)
        total_recommends = sum(blog['recommend_count'] for blog in self.blog_data)
        
        print(f"\n数据摘要:")
        print(f"总博客数: {len(self.blog_data)}")
        print(f"总阅读量: {total_reads}")
        print(f"总评论数: {total_comments}")
        print(f"总推荐数: {total_recommends}")
        
        # 显示前5篇博客
        print(f"\n前5篇博客:")
        for i, blog in enumerate(self.blog_data[:5], 1):
            print(f"{i}. {blog['title']}")
            print(f"   时间: {blog['publish_time']}")
            print(f"   阅读: {blog['read_count']}, 评论: {blog['comment_count']}, 推荐: {blog['recommend_count']}")
            print(f"   摘要: {blog['summary'][:100]}..." if len(blog['summary']) > 100 else f"   摘要: {blog['summary']}")
            print()


def main():
    """主函数"""
    spider = CnblogsSpider()
    
    # 爬取所有14页数据
    spider.crawl_all_pages(total_pages=14)
    
    # 显示数据摘要
    spider.display_summary()
    
    # 保存数据
    json_file = spider.save_to_json()
    csv_file = spider.save_to_csv()
    
    print(f"\n爬取完成!")
    print(f"JSON文件: {json_file}")
    print(f"CSV文件: {csv_file}")


if __name__ == "__main__":
    main()
