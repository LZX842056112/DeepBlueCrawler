# 上海本地宝学校政策信息爬虫

这是一个用于爬取上海本地宝网站（http://sh.bendibao.com/news/list_17_727_1.htm）上"学校政策"信息的Python爬虫程序。

## 功能特点

- ✅ 爬取所有分页内容
- ✅ 提取文章标题、URL、摘要、发布时间
- ✅ 自动检测总页数
- ✅ 支持JSON和CSV格式导出
- ✅ 包含详细的统计信息
- ✅ 请求延迟避免被封IP

## 文件说明

- `school_policy_crawler.py` - 基础版爬虫
- `enhanced_crawler.py` - 增强版爬虫（推荐使用）
- `test_crawler.py` - 测试脚本
- `requirements.txt` - 依赖包列表
- `school_policies.json` - 基础版爬取结果
- `school_policies.csv` - 基础版CSV格式结果
- `enhanced_school_policies.json` - 增强版爬取结果
- `enhanced_school_policies.csv` - 增强版CSV格式结果

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 运行基础版爬虫
```bash
python school_policy_crawler.py
```

### 2. 运行增强版爬虫（推荐）
```bash
python enhanced_crawler.py
```

### 3. 运行测试
```bash
python test_crawler.py
```

## 爬取内容

- **标题**：文章的标题
- **URL**：文章的完整链接
- **摘要**：文章的摘要内容
- **发布时间**：文章的发布时间
- **页面**：文章所在的页码
- **爬取时间**：数据爬取的时间戳（仅增强版）

## 输出格式

### JSON格式
```json
[
  {
    "title": "文章标题",
    "url": "http://sh.bendibao.com/news/xxxx.shtm",
    "summary": "文章摘要",
    "publish_time": "2024-01-26 14:57",
    "page": 1,
    "crawl_time": "2025-10-23 11:45:00"
  }
]
```

### CSV格式
包含所有字段的表格格式，适合用Excel打开分析。

## 技术特点

1. **智能分页检测**：自动检测网站的总页数
2. **多重选择器**：使用多种CSS选择器确保数据提取准确性
3. **错误处理**：完善的异常处理机制
4. **请求控制**：添加延迟避免请求过快
5. **编码处理**：正确处理中文编码

## 注意事项

1. 请合理使用爬虫，避免对目标网站造成过大压力
2. 爬虫仅用于学习和研究目的
3. 网站结构可能发生变化，需要定期更新选择器
4. 建议在遵守robots.txt的前提下使用

## 更新日志

- 2025-10-23: 初始版本发布
- 2025-10-23: 增强版发布，增加统计功能和更好的错误处理
