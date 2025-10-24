#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
猫眼电影经典影片爬虫
爬取 https://www.maoyan.com/board/4 网站上的前 100 名经典影片
"""

import requests
import json
import os
import time
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin


class MaoyanSpider:
    def __init__(self):
        self.base_url = "https://www.maoyan.com/board/4"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 创建保存目录
        self.data_dir = "maoyan_data"
        self.images_dir = os.path.join(self.data_dir, "images")
        os.makedirs(self.images_dir, exist_ok=True)
        
        self.movies_data = []

    def get_page_content(self, offset=0):
        """获取页面内容"""
        url = f"{self.base_url}?offset={offset}"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            print(f"请求页面失败: {e}")
            return None

    def parse_movie_info(self, html_content):
        """解析电影信息"""
        soup = BeautifulSoup(html_content, 'html.parser')
        movies = []
        
        # 查找电影列表
        movie_items = soup.find_all('dd')
        
        for item in movie_items:
            try:
                # 电影名
                name_elem = item.find('p', class_='name')
                movie_name = name_elem.get_text(strip=True) if name_elem else "未知"
                
                # 主演
                star_elem = item.find('p', class_='star')
                stars = star_elem.get_text(strip=True).replace('主演：', '') if star_elem else "未知"
                
                # 上映时间
                time_elem = item.find('p', class_='releasetime')
                release_time = time_elem.get_text(strip=True).replace('上映时间：', '') if time_elem else "未知"
                
                # 评分
                score_elem = item.find('p', class_='score')
                score = score_elem.get_text(strip=True) if score_elem else "暂无评分"
                
                # 图片URL
                img_elem = item.find('img', class_='board-img')
                if img_elem and img_elem.get('data-src'):
                    img_url = img_elem['data-src']
                elif img_elem and img_elem.get('src'):
                    img_url = img_elem['src']
                else:
                    img_url = ""
                
                movie_info = {
                    'name': movie_name,
                    'stars': stars,
                    'release_time': release_time,
                    'score': score,
                    'image_url': img_url
                }
                
                movies.append(movie_info)
                print(f"解析到电影: {movie_name}")
                
            except Exception as e:
                print(f"解析电影信息时出错: {e}")
                continue
        
        return movies

    def download_image(self, img_url, movie_name):
        """下载电影图片"""
        if not img_url:
            return None
            
        try:
            # 清理文件名中的非法字符
            safe_name = re.sub(r'[<>:"/\\|?*]', '_', movie_name)
            file_extension = os.path.splitext(img_url)[1]
            if not file_extension:
                file_extension = '.jpg'
            
            filename = f"{safe_name}{file_extension}"
            filepath = os.path.join(self.images_dir, filename)
            
            # 如果文件已存在，跳过下载
            if os.path.exists(filepath):
                print(f"图片已存在: {filename}")
                return filepath
            
            response = self.session.get(img_url, timeout=10)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"下载图片成功: {filename}")
            return filepath
            
        except Exception as e:
            print(f"下载图片失败 {movie_name}: {e}")
            return None

    def save_to_json(self, data):
        """保存数据到JSON文件"""
        filepath = os.path.join(self.data_dir, "maoyan_movies.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到: {filepath}")

    def save_to_csv(self, data):
        """保存数据到CSV文件"""
        import csv
        
        filepath = os.path.join(self.data_dir, "maoyan_movies.csv")
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow(['电影名', '主演', '上映时间', '评分', '图片URL', '本地图片路径'])
            
            for movie in data:
                writer.writerow([
                    movie['name'],
                    movie['stars'],
                    movie['release_time'],
                    movie['score'],
                    movie['image_url'],
                    movie.get('local_image_path', '')
                ])
        
        print(f"数据已保存到: {filepath}")

    def crawl(self):
        """主爬取函数"""
        print("开始爬取猫眼电影经典影片...")
        
        total_movies = 0
        page_offset = 0
        
        while total_movies < 100:
            print(f"正在爬取第 {page_offset//10 + 1} 页...")
            
            html_content = self.get_page_content(page_offset)
            if not html_content:
                print(f"获取第 {page_offset//10 + 1} 页失败")
                break
            
            movies = self.parse_movie_info(html_content)
            if not movies:
                print(f"第 {page_offset//10 + 1} 页没有解析到电影信息")
                break
            
            # 下载图片并更新数据
            for movie in movies:
                if total_movies >= 100:
                    break
                    
                local_image_path = self.download_image(movie['image_url'], movie['name'])
                movie['local_image_path'] = local_image_path
                self.movies_data.append(movie)
                total_movies += 1
                
                # 添加延迟，避免请求过快
                time.sleep(1)
            
            print(f"已爬取 {total_movies} 部电影")
            
            # 翻页
            page_offset += 10
            
            # 添加页面间延迟
            time.sleep(2)
        
        # 保存数据
        if self.movies_data:
            self.save_to_json(self.movies_data)
            self.save_to_csv(self.movies_data)
            print(f"\n爬取完成！共获取 {len(self.movies_data)} 部电影信息")
            print(f"数据保存在: {self.data_dir} 目录")
        else:
            print("没有获取到任何电影数据")


def main():
    """主函数"""
    spider = MaoyanSpider()
    spider.crawl()


if __name__ == "__main__":
    main()
