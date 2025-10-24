import requests
from bs4 import BeautifulSoup
import re

def test_updated_spider():
    """测试更新后的爬虫功能"""
    print("测试更新后的爬虫功能...")
    
    url = 'https://www.cnblogs.com/pinard'
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找博客日期分组
        day_divs = soup.find_all('div', class_='day')
        print(f"找到 {len(day_divs)} 个博客日期分组")
        
        if day_divs:
            # 测试第一个博客项
            first_day = day_divs[0]
            print("\n测试第一个博客项:")
            
            # 提取标题
            title_div = first_day.find('div', class_='postTitle')
            if title_div:
                title_link = title_div.find('a')
                if title_link:
                    print(f"标题: {title_link.get_text().strip()}")
                    print(f"链接: {title_link.get('href')}")
            
            # 提取摘要
            summary_div = first_day.find('div', class_='postCon') or first_day.find('div', class_='c_b_p_desc')
            if summary_div:
                summary_text = summary_div.get_text().strip()
                print(f"摘要: {summary_text[:100]}..." if len(summary_text) > 100 else f"摘要: {summary_text}")
            
            # 提取元信息
            meta_div = first_day.find('div', class_='postDesc')
            if meta_div:
                meta_text = meta_div.get_text()
                print(f"元信息: {meta_text.strip()}")
                
                # 测试正则表达式提取
                time_match = re.search(r'posted @ (\d{4}-\d{2}-\d{2} \d{2}:\d{2})', meta_text)
                read_match = re.search(r'阅读\((\d+)\)', meta_text)
                comment_match = re.search(r'评论\((\d+)\)', meta_text)
                recommend_match = re.search(r'推荐\((\d+)\)', meta_text)
                
                print("提取结果:")
                print(f"  时间: {time_match.group(1) if time_match else '未找到'}")
                print(f"  阅读量: {read_match.group(1) if read_match else '未找到'}")
                print(f"  评论数: {comment_match.group(1) if comment_match else '未找到'}")
                print(f"  推荐数: {recommend_match.group(1) if recommend_match else '未找到'}")
        
        # 测试分页
        print("\n测试分页链接...")
        page_links = soup.find_all('a', href=re.compile(r'page=\d+'))
        print(f"找到 {len(page_links)} 个分页链接")
        for link in page_links[:3]:
            print(f"分页链接: {link.get('href')}, 文本: {link.get_text().strip()}")
            
    except Exception as e:
        print(f'测试失败: {e}')

if __name__ == "__main__":
    test_updated_spider()
