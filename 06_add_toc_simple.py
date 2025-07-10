#!/usr/bin/env python3
"""
06_add_toc_simple.py - 简化版目录生成（用于测试）

功能：
- 解析HTML中的标题标签（无需BeautifulSoup）
- 生成简单的目录结构
- 添加到HTML最前面
"""

import json
import os
import re
import sys


def load_config(temp_dir: str) -> dict:
    """加载配置文件"""
    config_path = os.path.join(temp_dir, "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_headings_simple(html_content: str) -> list:
    """简单解析HTML中的标题"""
    headings = []
    
    # 查找所有标题标签
    heading_pattern = r'<(h[1-6]).*?>(.*?)</\1>'
    matches = re.finditer(heading_pattern, html_content, re.IGNORECASE | re.DOTALL)
    
    for i, match in enumerate(matches):
        tag = match.group(1).lower()
        text = match.group(2).strip()
        level = int(tag[1])
        
        # 生成ID
        heading_id = f"heading-{i+1}"
        
        headings.append({
            'level': level,
            'text': text,
            'id': heading_id,
            'original': match.group(0)
        })
    
    return headings


def generate_simple_toc_html(headings: list) -> str:
    """生成简单的目录HTML"""
    if not headings:
        return ""
    
    toc_html = """
<div class="table-of-contents">
    <h2>📚 目录</h2>
    <ul class="toc-list">
"""
    
    for heading in headings:
        indent = "  " * (heading['level'] - 1)
        toc_html += f'{indent}<li><a href="#{heading["id"]}">{heading["text"]}</a></li>\n'
    
    toc_html += """
    </ul>
</div>

<style>
.table-of-contents {
    background-color: #f8f9fa;
    border: 2px solid #e9ecef;
    border-radius: 10px;
    padding: 20px;
    margin: 30px 0;
}

.table-of-contents h2 {
    margin-top: 0;
    color: #495057;
    border-bottom: 1px solid #dee2e6;
    padding-bottom: 10px;
}

.toc-list {
    list-style: none;
    padding: 0;
    margin: 15px 0 0 0;
}

.toc-list li {
    margin: 8px 0;
    padding-left: 20px;
}

.toc-list a {
    color: #495057;
    text-decoration: none;
    display: block;
    padding: 5px 8px;
    border-radius: 4px;
    transition: all 0.2s;
}

.toc-list a:hover {
    background-color: #e9ecef;
    color: #007bff;
}

@media (prefers-color-scheme: dark) {
    .table-of-contents {
        background-color: #2d3748;
        border-color: #4a5568;
    }
    
    .table-of-contents h2 {
        color: #e2e8f0;
        border-bottom-color: #4a5568;
    }
    
    .toc-list a {
        color: #e2e8f0;
    }
    
    .toc-list a:hover {
        background-color: #4a5568;
        color: #63b3ed;
    }
}
</style>

"""
    
    return toc_html


def add_simple_toc(html_file: str, output_file: str = None) -> str:
    """为HTML文件添加简单目录"""
    if output_file is None:
        output_file = html_file
    
    print(f"📑 为HTML文件添加目录: {html_file}")
    
    # 读取HTML文件
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 解析标题
    headings = parse_headings_simple(html_content)
    
    if not headings:
        print("⚠️  未找到任何标题，跳过目录生成")
        return html_file
    
    print(f"📋 找到 {len(headings)} 个标题")
    
    # 为标题添加ID
    updated_html = html_content
    for heading in headings:
        # 在原始标题标签中添加ID
        original_tag = heading['original']
        tag_name = re.match(r'<(h[1-6])', original_tag, re.IGNORECASE).group(1)
        new_tag = original_tag.replace(
            f'<{tag_name}',
            f'<{tag_name} id="{heading["id"]}"',
            1
        )
        updated_html = updated_html.replace(original_tag, new_tag)
    
    # 生成目录HTML
    toc_html = generate_simple_toc_html(headings)
    
    # 在<body>标签后插入目录
    body_pattern = r'(<body[^>]*>)'
    if re.search(body_pattern, updated_html):
        updated_html = re.sub(
            body_pattern,
            r'\1' + toc_html,
            updated_html
        )
    else:
        # 如果没有找到body标签，在开头插入
        updated_html = toc_html + updated_html
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print(f"✅ 目录添加完成: {output_file}")
    return output_file


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python 06_add_toc_simple.py <temp_dir>")
        return 1
    
    temp_dir = sys.argv[1]
    
    try:
        # 加载配置
        config = load_config(temp_dir)
        
        if 'html_file' not in config:
            print("❌ 错误: 未找到HTML文件，请先运行 05_md_to_html.py")
            return 1
        
        # 添加目录
        final_html = add_simple_toc(config['html_file'])
        
        # 更新配置
        config['final_html'] = final_html
        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"🎯 目录生成完成: {final_html}")
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())