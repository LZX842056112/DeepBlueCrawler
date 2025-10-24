import requests
from bs4 import BeautifulSoup
import re

def analyze_cnblogs_structure():
    """分析cnblogs网站结构"""
    print("开始分析cnblogs网站结构...")
    
    url = 'https://www.cnblogs.com/pinard'
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print('页面标题:', soup.title.text if soup.title else '无标题')
        
        # 查找所有可能的博客容器
        print("\n查找博客容器...")
        
        # 查找包含博客文章的div
        all_divs = soup.find_all('div')
        blog_containers = []
        
        for div in all_divs:
            classes = div.get('class', [])
            if classes:
                # 查找包含post、entry、blog等关键词的类
                if any(keyword in ' '.join(classes).lower() for keyword in ['post', 'entry', 'blog', 'article']):
                    blog_containers.append(div)
        
        print(f"找到 {len(blog_containers)} 个可能的博客容器")
        
        # 分析第一个博客容器的结构
        if blog_containers:
            first_container = blog_containers[0]
            print(f"\n第一个博客容器的类名: {first_container.get('class')}")
            
            # 查找标题
            print("\n查找标题元素...")
            title_elements = first_container.find_all(['a', 'h1', 'h2', 'h3', 'h4'])
            for elem in title_elements:
                if elem.get_text().strip():
                    print(f"标题元素: {elem.name}, 类名: {elem.get('class')}, 文本: {elem.get_text().strip()[:50]}...")
            
            # 查找摘要
            print("\n查找摘要元素...")
            summary_elements = first_container.find_all(['p', 'div'])
            for elem in summary_elements[:5]:  # 只检查前5个
                text = elem.get_text().strip()
                if len(text) > 50 and len(text) < 300:  # 可能是摘要
                    print(f"摘要元素: {elem.name}, 类名: {elem.get('class')}, 文本: {text[:100]}...")
            
            # 查找元信息（时间、阅读量等）
            print("\n查找元信息元素...")
            meta_elements = first_container.find_all(['div', 'span'])
            for elem in meta_elements:
                text = elem.get_text().strip()
                if any(keyword in text for keyword in ['阅读', '评论', '推荐', '发布于', 'posted']):
                    print(f"元信息元素: {elem.name}, 类名: {elem.get('class')}, 文本: {text}")
            
            # 显示完整的HTML结构（简化版）
            print(f"\n完整的HTML结构（前500字符）:")
            print(str(first_container)[:500])
        
        # 查找分页信息
        print("\n查找分页信息...")
        pagination = soup.find_all(['div', 'ul', 'nav'], class_=re.compile(r'pager|pagination|page'))
        if pagination:
            print(f"找到分页元素: {len(pagination)} 个")
            for page in pagination:
                print(f"分页类名: {page.get('class')}")
        
        # 查找所有链接，看是否有分页链接
        all_links = soup.find_all('a', href=True)
        page_links = [link for link in all_links if 'page' in link.get('href', '')]
        print(f"\n找到 {len(page_links)} 个分页链接")
        for link in page_links[:5]:
            print(f"分页链接: {link.get('href')}, 文本: {link.get_text().strip()}")
            
    except Exception as e:
        print(f'分析失败: {e}')

if __name__ == "__main__":
    analyze_cnblogs_structure()
