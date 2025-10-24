import requests
from bs4 import BeautifulSoup
import re

def deep_analysis_cnblogs():
    """深度分析cnblogs网站结构"""
    print("深度分析cnblogs网站结构...")
    
    url = 'https://www.cnblogs.com/pinard'
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print('页面标题:', soup.title.text if soup.title else '无标题')
        
        # 查找所有div，分析其结构和内容
        print("\n分析所有div的结构...")
        all_divs = soup.find_all('div')
        
        # 按类名分组
        divs_by_class = {}
        for div in all_divs:
            classes = div.get('class', [])
            if classes:
                for cls in classes:
                    if cls not in divs_by_class:
                        divs_by_class[cls] = []
                    divs_by_class[cls].append(div)
        
        # 显示最常见的类名
        print(f"\n找到 {len(divs_by_class)} 种不同的div类名")
        sorted_classes = sorted(divs_by_class.items(), key=lambda x: len(x[1]), reverse=True)
        
        for cls_name, divs in sorted_classes[:10]:  # 显示前10个最常见的类
            print(f"类名 '{cls_name}': {len(divs)} 个div")
            
            # 分析第一个div的内容
            if divs:
                first_div = divs[0]
                text = first_div.get_text().strip()
                if text:
                    print(f"  示例内容: {text[:100]}...")
        
        # 特别查找可能包含博客文章的div
        print("\n查找可能包含博客文章的div...")
        potential_blog_divs = []
        
        for div in all_divs:
            text = div.get_text().strip()
            # 如果div包含较长的文本，可能是博客文章
            if len(text) > 200:
                potential_blog_divs.append(div)
        
        print(f"找到 {len(potential_blog_divs)} 个可能包含博客文章的div")
        
        # 分析第一个可能的博客div
        if potential_blog_divs:
            first_blog_div = potential_blog_divs[0]
            print(f"\n第一个可能的博客div类名: {first_blog_div.get('class')}")
            print(f"内容预览: {first_blog_div.get_text()[:200]}...")
            
            # 查找内部的链接
            links = first_blog_div.find_all('a', href=True)
            print(f"包含 {len(links)} 个链接")
            for link in links[:3]:
                print(f"  链接: {link.get('href')}, 文本: {link.get_text().strip()[:50]}...")
        
        # 查找所有包含"阅读"、"评论"、"推荐"的文本
        print("\n查找包含统计信息的文本...")
        stats_texts = []
        for element in soup.find_all(text=re.compile(r'阅读|评论|推荐')):
            parent = element.parent
            if parent:
                stats_texts.append(parent.get_text().strip())
        
        print(f"找到 {len(stats_texts)} 个包含统计信息的文本")
        for text in stats_texts[:5]:
            print(f"  统计信息: {text}")
        
        # 查找所有文章标题链接
        print("\n查找所有文章标题链接...")
        title_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text().strip()
            # 如果链接指向博客文章且文本较长
            if '/p/' in href and len(text) > 10:
                title_links.append((text, href))
        
        print(f"找到 {len(title_links)} 个可能的文章标题链接")
        for title, href in title_links[:5]:
            print(f"  标题: {title[:50]}...")
            print(f"  链接: {href}")
            
    except Exception as e:
        print(f'深度分析失败: {e}')

if __name__ == "__main__":
    deep_analysis_cnblogs()
