#!/usr/bin/env python3
"""
05_md_to_html_simple.py - 简化版Markdown转HTML（用于测试）

功能：
- 基础的markdown到HTML转换（无需pandoc）
- 应用中文电子书模板
- 处理图片资源
"""

import json
import os
import re
import sys
import shutil
from pathlib import Path


def load_config(temp_dir: str) -> dict:
    """加载配置文件"""
    config_path = os.path.join(temp_dir, "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def simple_markdown_to_html(markdown_content: str) -> str:
    """简单的markdown到HTML转换"""
    html_content = markdown_content
    
    # 转换标题
    html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)
    
    # 转换段落（简单版本）
    lines = html_content.split('\n')
    converted_lines = []
    in_paragraph = False
    
    for line in lines:
        line = line.strip()
        
        # 跳过空行
        if not line:
            if in_paragraph:
                converted_lines.append('</p>')
                in_paragraph = False
            converted_lines.append('')
            continue
        
        # 检查是否是标题或其他块级元素
        if (line.startswith('<h') or line.startswith('<div') or 
            line.startswith('<ul') or line.startswith('<ol') or
            line.startswith('<blockquote') or line.startswith('---')):
            if in_paragraph:
                converted_lines.append('</p>')
                in_paragraph = False
            converted_lines.append(line)
            continue
        
        # 处理分隔符
        if line == '---':
            if in_paragraph:
                converted_lines.append('</p>')
                in_paragraph = False
            converted_lines.append('<hr>')
            continue
        
        # 处理列表项
        if line.startswith('- '):
            if in_paragraph:
                converted_lines.append('</p>')
                in_paragraph = False
            if not converted_lines or not converted_lines[-1].startswith('<li>'):
                converted_lines.append('<ul>')
            converted_lines.append(f'<li>{line[2:]}</li>')
            continue
        
        # 处理普通段落
        if not in_paragraph:
            converted_lines.append('<p>')
            in_paragraph = True
        
        # 转换内联元素
        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)  # 粗体
        line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)  # 斜体
        line = re.sub(r'`(.+?)`', r'<code>\1</code>', line)  # 内联代码
        
        converted_lines.append(line)
    
    # 关闭未关闭的段落
    if in_paragraph:
        converted_lines.append('</p>')
    
    # 关闭未关闭的列表
    if converted_lines and converted_lines[-1].startswith('<li>'):
        converted_lines.append('</ul>')
    
    return '\n'.join(converted_lines)


def load_template() -> str:
    """加载HTML模板"""
    template_path = "template.html"
    
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # 如果模板不存在，使用简化版模板
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>翻译电子书</title>
    <style>
        body {
            font-family: "仿宋", "FangSong", "STFangSong", serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fefefe;
            color: #333;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 2em;
            margin-bottom: 1em;
        }
        
        h1 { font-size: 2.2em; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { font-size: 1.8em; border-bottom: 2px solid #3498db; padding-bottom: 8px; }
        h3 { font-size: 1.5em; }
        
        p { margin: 1em 0; text-align: justify; }
        
        hr {
            border: none;
            border-top: 2px solid #eee;
            margin: 3em 0;
        }
        
        @media (max-width: 600px) {
            body { padding: 10px; font-size: 16px; }
            h1 { font-size: 1.8em; }
            h2 { font-size: 1.5em; }
        }
    </style>
</head>
<body>
$body$
</body>
</html>"""


def copy_images_to_output(temp_dir: str, output_dir: str) -> None:
    """复制图片文件到输出目录"""
    images_dir = os.path.join(temp_dir, "images")
    output_images_dir = os.path.join(output_dir, "images")
    
    if os.path.exists(images_dir) and os.listdir(images_dir):
        if os.path.exists(output_images_dir):
            shutil.rmtree(output_images_dir)
        shutil.copytree(images_dir, output_images_dir)
        print(f"📸 复制图片文件到: {output_images_dir}")
    else:
        print("📸 没有图片文件需要复制")


def convert_md_to_html(md_file: str, template_file: str, 
                      output_file: str = "book.html") -> str:
    """转换markdown为HTML"""
    
    if not os.path.exists(md_file):
        raise FileNotFoundError(f"Markdown文件不存在: {md_file}")
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file) if os.path.dirname(output_file) else "."
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🔄 转换 Markdown 为 HTML...")
    print(f"📄 输入: {md_file}")
    print(f"📤 输出: {output_file}")
    
    # 读取markdown内容
    with open(md_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # 转换为HTML
    html_body = simple_markdown_to_html(markdown_content)
    
    # 加载模板
    template = load_template()
    
    # 应用模板
    html_content = template.replace('$body$', html_body)
    
    # 如果有title placeholder，设置默认标题
    if '$title$' in html_content:
        html_content = html_content.replace('$title$', '翻译电子书')
    
    # 写入HTML文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML转换完成: {output_file}")
    return output_file


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python 05_md_to_html_simple.py <temp_dir>")
        return 1
    
    temp_dir = sys.argv[1]
    
    try:
        # 加载配置
        config = load_config(temp_dir)
        
        if 'merged_file' not in config:
            print("❌ 错误: 未找到合并的markdown文件，请先运行 04_merge_md.py")
            return 1
        
        # 转换为HTML
        output_file = os.path.join(temp_dir, "book.html")
        html_file = convert_md_to_html(
            config['merged_file'],
            "template.html",  # 模板文件
            output_file
        )
        
        # 复制图片文件
        copy_images_to_output(temp_dir, temp_dir)
        
        # 更新配置
        config['html_file'] = html_file
        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"🎯 HTML转换完成: {html_file}")
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())