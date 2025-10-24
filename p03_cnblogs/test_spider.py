import requests
from bs4 import BeautifulSoup
import re

def test_cnblogs_spider():
    """测试cnblogs爬虫功能"""
    print("开始测试cnblogs爬虫...")
    
    # 测试第一页的爬取
    url = 'https://www.cnblogs.com/pinard'
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print('页面标题:', soup.title.text if soup.title else '无标题')
        
        # 查找博客文章
        post_items = soup.find_all('div', class_='post-item')
        print(f'找到 {len(post_items)} 篇博客文章')
        
        if post_items:
            # 显示第一篇文章的信息
            first_item = post_items[0]
            print('\n第一篇文章信息:')
            
            # 标题
            title_elem = first_item.find('a', class_='post-item-title')
            if title_elem:
                print('标题:', title_elem.text.strip())
            
            # 摘要
            summary_elem = first_item.find('p', class_='post-item-summary')
            if summary_elem:
                summary_text = summary_elem.text.strip()
                print('摘要:', summary_text[:100] + '...' if len(summary_text) > 100 else summary_text)
            
            # 元信息
            meta_elem = first_item.find('div', class_='post-item-foot')
            if meta_elem:
                meta_text = meta_elem.text
                print('元信息:', meta_text.strip())
                
                # 测试正则表达式提取
                time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', meta_text)
                read_match = re.search(r'阅读\((\d+)\)', meta_text)
                comment_match = re.search(r'评论\((\d+)\)', meta_text)
                recommend_match = re.search(r'推荐\((\d+)\)', meta_text)
                
                print('提取结果:')
                print(f'  时间: {time_match.group(1) if time_match else "未找到"}')
                print(f'  阅读量: {read_match.group(1) if read_match else "未找到"}')
                print(f'  评论数: {comment_match.group(1) if comment_match else "未找到"}')
                print(f'  推荐数: {recommend_match.group(1) if recommend_match else "未找到"}')
        else:
            print('未找到博客文章，尝试其他选择器...')
            # 尝试其他可能的类名
            all_divs = soup.find_all('div')
            post_divs = []
            for div in all_divs:
                classes = div.get('class', [])
                if classes and any('post' in cls for cls in classes):
                    post_divs.append(div)
            
            print(f'找到 {len(post_divs)} 个可能的文章div')
            if post_divs:
                print('第一个可能的文章div类名:', post_divs[0].get('class'))
                
    except Exception as e:
        print(f'测试失败: {e}')

if __name__ == "__main__":
    test_cnblogs_spider()
