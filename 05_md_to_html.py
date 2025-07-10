#!/usr/bin/env python3
"""
05_md_to_html.py - Markdown转HTML

功能：
- 使用pandoc将markdown转换为HTML
- 应用中文电子书模板
- 处理图片资源嵌入
- 支持响应式设计
- 优化中文字体显示
"""

import json
import os
import sys
import shutil
from pathlib import Path
import subprocess


def load_config(temp_dir: str) -> dict:
    """加载配置文件"""
    config_path = os.path.join(temp_dir, "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_template_file() -> str:
    """查找HTML模板文件"""
    # 在当前目录查找模板
    current_dir = Path(__file__).parent
    template_path = current_dir / "template.html"
    
    if template_path.exists():
        return str(template_path)
    
    # 如果没有找到，使用默认模板
    return create_default_template()


def create_default_template() -> str:
    """创建默认HTML模板"""
    template_content = """<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$title$</title>
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
        
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        blockquote {
            border-left: 4px solid #3498db;
            margin: 1em 0;
            padding: 0.5em 1em;
            background-color: #f8f9fa;
            font-style: italic;
        }
        
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "Consolas", "Monaco", monospace;
        }
        
        pre {
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
        }
        
        hr {
            border: none;
            border-top: 2px solid #eee;
            margin: 3em 0;
        }
        
        @media (max-width: 600px) {
            body {
                padding: 10px;
                font-size: 16px;
            }
            
            h1 { font-size: 1.8em; }
            h2 { font-size: 1.5em; }
            h3 { font-size: 1.3em; }
        }
        
        @media (prefers-color-scheme: dark) {
            body {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
            
            h1, h2, h3, h4, h5, h6 {
                color: #4fc3f7;
            }
            
            blockquote {
                background-color: #2d2d2d;
                border-left-color: #4fc3f7;
            }
            
            code {
                background-color: #333;
                color: #f8f8f2;
            }
            
            pre {
                background-color: #2d2d2d;
                border-color: #555;
            }
        }
    </style>
</head>
<body>
$body$
</body>
</html>"""
    
    template_path = "default_template.html"
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    return template_path


def copy_images_to_output(temp_dir: str, output_dir: str) -> None:
    """复制图片文件到输出目录"""
    images_dir = os.path.join(temp_dir, "images")
    output_images_dir = os.path.join(output_dir, "images")
    
    if os.path.exists(images_dir):
        if os.path.exists(output_images_dir):
            shutil.rmtree(output_images_dir)
        shutil.copytree(images_dir, output_images_dir)
        print(f"📸 复制图片文件到: {output_images_dir}")


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
    print(f"🎨 模板: {template_file}")
    print(f"📤 输出: {output_file}")
    
    try:
        # 使用pandoc转换
        cmd = [
            'pandoc',
            '-f', 'markdown',
            '-t', 'html',
            '--template', template_file,
            '--standalone',
            '--toc',  # 生成目录
            '--toc-depth=3',
            '--section-divs',
            md_file,
            '-o', output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print(f"✅ HTML转换完成: {output_file}")
        return output_file
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Pandoc转换失败: {e}")
        print(f"错误输出: {e.stderr}")
        raise RuntimeError(f"HTML转换失败: {e}")


def enhance_html_file(html_file: str) -> None:
    """增强HTML文件的功能"""
    
    # 读取HTML内容
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 添加JavaScript功能
    js_code = """
<script>
// 图片点击放大功能
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.style.cursor = 'pointer';
        img.addEventListener('click', function() {
            if (this.style.transform === 'scale(1.5)') {
                this.style.transform = 'scale(1)';
                this.style.zIndex = '1';
            } else {
                this.style.transform = 'scale(1.5)';
                this.style.zIndex = '1000';
                this.style.transition = 'transform 0.3s ease';
            }
        });
    });
    
    // 平滑滚动
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});
</script>
"""
    
    # 在</body>之前插入JavaScript
    html_content = html_content.replace('</body>', js_code + '\n</body>')
    
    # 写回文件
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✨ HTML功能增强完成")


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python 05_md_to_html.py <temp_dir>")
        return 1
    
    temp_dir = sys.argv[1]
    
    try:
        # 加载配置
        config = load_config(temp_dir)
        
        if 'merged_file' not in config:
            print("❌ 错误: 未找到合并的markdown文件，请先运行 04_merge_md.py")
            return 1
        
        # 查找模板文件
        template_file = find_template_file()
        
        # 转换为HTML
        output_file = os.path.join(temp_dir, "book.html")
        html_file = convert_md_to_html(
            config['merged_file'],
            template_file,
            output_file
        )
        
        # 复制图片文件
        copy_images_to_output(temp_dir, temp_dir)
        
        # 增强HTML功能
        enhance_html_file(html_file)
        
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