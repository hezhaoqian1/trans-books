#!/usr/bin/env python3
"""
06_add_toc.py - 自动生成目录

功能：
- 解析HTML中的标题标签
- 生成层级化的目录结构
- 添加锚点链接
- 将目录插入HTML最前面
- 支持目录折叠/展开
"""

import json
import os
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple


def load_config(temp_dir: str) -> dict:
    """加载配置文件"""
    config_path = os.path.join(temp_dir, "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_html_headings(html_content: str) -> List[Dict]:
    """解析HTML中的标题标签"""
    soup = BeautifulSoup(html_content, 'html.parser')
    headings = []
    
    # 查找所有标题标签
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        level = int(tag.name[1])  # 获取标题级别
        text = tag.get_text().strip()
        
        # 生成唯一的ID
        heading_id = generate_heading_id(text, len(headings))
        tag['id'] = heading_id
        
        headings.append({
            'level': level,
            'text': text,
            'id': heading_id,
            'element': tag
        })
    
    return headings, str(soup)


def generate_heading_id(text: str, index: int) -> str:
    """生成标题的唯一ID"""
    # 移除特殊字符，保留中文和英文
    clean_text = re.sub(r'[^\w\u4e00-\u9fff]', '', text)
    
    # 如果文本为空，使用索引
    if not clean_text:
        return f"heading-{index}"
    
    # 限制长度
    if len(clean_text) > 20:
        clean_text = clean_text[:20]
    
    return f"heading-{index}-{clean_text}"


def generate_toc_html(headings: List[Dict]) -> str:
    """生成目录HTML"""
    if not headings:
        return ""
    
    toc_html = """
<nav class="table-of-contents">
    <div class="toc-header">
        <h2>📚 目录</h2>
        <button class="toc-toggle" onclick="toggleToc()">收起</button>
    </div>
    <div class="toc-content">
        <ul class="toc-list">
"""
    
    current_level = 1
    
    for heading in headings:
        level = heading['level']
        text = heading['text']
        heading_id = heading['id']
        
        # 处理层级变化
        if level > current_level:
            # 需要开始新的嵌套列表
            for _ in range(level - current_level):
                toc_html += '<ul class="toc-sublist">\n'
        elif level < current_level:
            # 需要关闭嵌套列表
            for _ in range(current_level - level):
                toc_html += '</ul>\n'
        
        # 添加目录项
        toc_html += f'<li class="toc-item toc-level-{level}">\n'
        toc_html += f'<a href="#{heading_id}" class="toc-link">{text}</a>\n'
        toc_html += '</li>\n'
        
        current_level = level
    
    # 关闭所有未关闭的列表
    for _ in range(current_level - 1):
        toc_html += '</ul>\n'
    
    toc_html += """
        </ul>
    </div>
</nav>
"""
    
    return toc_html


def generate_toc_css() -> str:
    """生成目录CSS样式"""
    return """
<style>
.table-of-contents {
    background-color: #f8f9fa;
    border: 2px solid #e9ecef;
    border-radius: 10px;
    padding: 20px;
    margin: 30px 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.toc-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #dee2e6;
    padding-bottom: 10px;
    margin-bottom: 15px;
}

.toc-header h2 {
    margin: 0;
    color: #495057;
    font-size: 1.3em;
}

.toc-toggle {
    background: #007bff;
    color: white;
    border: none;
    padding: 5px 15px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.9em;
    transition: background-color 0.3s;
}

.toc-toggle:hover {
    background: #0056b3;
}

.toc-content {
    max-height: 400px;
    overflow-y: auto;
    transition: max-height 0.3s ease;
}

.toc-content.collapsed {
    max-height: 0;
    overflow: hidden;
}

.toc-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.toc-sublist {
    list-style: none;
    padding-left: 20px;
    margin: 5px 0;
}

.toc-item {
    margin: 8px 0;
    line-height: 1.4;
}

.toc-link {
    color: #495057;
    text-decoration: none;
    display: block;
    padding: 5px 8px;
    border-radius: 4px;
    transition: all 0.2s;
}

.toc-link:hover {
    background-color: #e9ecef;
    color: #007bff;
    text-decoration: none;
}

.toc-level-1 .toc-link {
    font-weight: bold;
    font-size: 1.1em;
}

.toc-level-2 .toc-link {
    font-weight: 600;
    padding-left: 15px;
}

.toc-level-3 .toc-link {
    padding-left: 25px;
    font-size: 0.95em;
}

.toc-level-4 .toc-link,
.toc-level-5 .toc-link,
.toc-level-6 .toc-link {
    padding-left: 35px;
    font-size: 0.9em;
    color: #6c757d;
}

/* 移动端优化 */
@media (max-width: 768px) {
    .table-of-contents {
        margin: 20px 0;
        padding: 15px;
    }
    
    .toc-header h2 {
        font-size: 1.1em;
    }
    
    .toc-toggle {
        font-size: 0.8em;
        padding: 4px 12px;
    }
    
    .toc-content {
        max-height: 300px;
    }
}

/* 暗色模式 */
@media (prefers-color-scheme: dark) {
    .table-of-contents {
        background-color: #2d3748;
        border-color: #4a5568;
    }
    
    .toc-header {
        border-bottom-color: #4a5568;
    }
    
    .toc-header h2 {
        color: #e2e8f0;
    }
    
    .toc-link {
        color: #e2e8f0;
    }
    
    .toc-link:hover {
        background-color: #4a5568;
        color: #63b3ed;
    }
    
    .toc-level-4 .toc-link,
    .toc-level-5 .toc-link,
    .toc-level-6 .toc-link {
        color: #a0aec0;
    }
}
</style>
"""


def generate_toc_js() -> str:
    """生成目录JavaScript功能"""
    return """
<script>
function toggleToc() {
    const content = document.querySelector('.toc-content');
    const button = document.querySelector('.toc-toggle');
    
    if (content.classList.contains('collapsed')) {
        content.classList.remove('collapsed');
        button.textContent = '收起';
    } else {
        content.classList.add('collapsed');
        button.textContent = '展开';
    }
}

// 页面加载完成后初始化目录功能
document.addEventListener('DOMContentLoaded', function() {
    // 平滑滚动到目标位置
    const tocLinks = document.querySelectorAll('.toc-link');
    tocLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const target = document.getElementById(targetId);
            
            if (target) {
                // 计算偏移量，避免被固定头部遮挡
                const offset = 80;
                const elementPosition = target.offsetTop;
                const offsetPosition = elementPosition - offset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // 高亮当前阅读位置
    function highlightCurrentSection() {
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        const tocLinks = document.querySelectorAll('.toc-link');
        
        let currentHeading = null;
        const scrollPosition = window.scrollY + 100;
        
        headings.forEach(heading => {
            if (heading.offsetTop <= scrollPosition) {
                currentHeading = heading;
            }
        });
        
        // 移除所有高亮
        tocLinks.forEach(link => {
            link.classList.remove('active');
        });
        
        // 高亮当前位置
        if (currentHeading) {
            const currentLink = document.querySelector(`.toc-link[href="#${currentHeading.id}"]`);
            if (currentLink) {
                currentLink.classList.add('active');
            }
        }
    }
    
    // 滚动时更新高亮
    window.addEventListener('scroll', highlightCurrentSection);
    
    // 添加活动状态样式
    const style = document.createElement('style');
    style.textContent = `
        .toc-link.active {
            background-color: #007bff !important;
            color: white !important;
            font-weight: bold;
        }
        
        @media (prefers-color-scheme: dark) {
            .toc-link.active {
                background-color: #63b3ed !important;
                color: #1a202c !important;
            }
        }
    `;
    document.head.appendChild(style);
});
</script>
"""


def add_table_of_contents(html_file: str, output_file: str = None) -> str:
    """为HTML文件添加目录"""
    if output_file is None:
        output_file = html_file
    
    print(f"📑 为HTML文件添加目录: {html_file}")
    
    # 读取HTML文件
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 解析标题
    headings, updated_html = parse_html_headings(html_content)
    
    if not headings:
        print("⚠️  未找到任何标题，跳过目录生成")
        return html_file
    
    print(f"📋 找到 {len(headings)} 个标题")
    
    # 生成目录HTML
    toc_html = generate_toc_html(headings)
    
    # 生成CSS和JavaScript
    toc_css = generate_toc_css()
    toc_js = generate_toc_js()
    
    # 在HTML中插入目录
    # 在<body>标签后插入目录
    body_pattern = r'(<body[^>]*>)'
    if re.search(body_pattern, updated_html):
        updated_html = re.sub(
            body_pattern,
            r'\1' + toc_html,
            updated_html
        )
    
    # 在<head>中插入CSS
    head_pattern = r'(</head>)'
    if re.search(head_pattern, updated_html):
        updated_html = re.sub(
            head_pattern,
            toc_css + r'\1',
            updated_html
        )
    
    # 在</body>前插入JavaScript
    body_end_pattern = r'(</body>)'
    if re.search(body_end_pattern, updated_html):
        updated_html = re.sub(
            body_end_pattern,
            toc_js + r'\1',
            updated_html
        )
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print(f"✅ 目录添加完成: {output_file}")
    return output_file


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python 06_add_toc.py <temp_dir>")
        return 1
    
    temp_dir = sys.argv[1]
    
    try:
        # 加载配置
        config = load_config(temp_dir)
        
        if 'html_file' not in config:
            print("❌ 错误: 未找到HTML文件，请先运行 05_md_to_html.py")
            return 1
        
        # 添加目录
        final_html = add_table_of_contents(config['html_file'])
        
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