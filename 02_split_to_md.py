#!/usr/bin/env python3
"""
02_split_to_md.py - 文档拆分为Markdown

功能：
- 处理PDF/DOCX/EPUB文件
- 按页面拆分文档
- 提取图片资源
- 生成markdown文件
- 支持断点续传
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import subprocess


def load_config(temp_dir: str) -> Dict:
    """加载配置文件"""
    config_path = os.path.join(temp_dir, "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_file_extension(file_path: str) -> str:
    """获取文件扩展名"""
    return Path(file_path).suffix.lower()


def convert_to_pdf(input_file: str, temp_dir: str) -> str:
    """转换DOCX/EPUB为PDF"""
    file_ext = get_file_extension(input_file)
    
    if file_ext == '.pdf':
        return input_file
    
    # 对于DOCX和EPUB，先转换为PDF
    output_pdf = os.path.join(temp_dir, "converted.pdf")
    
    if os.path.exists(output_pdf):
        print(f"⏭️  跳过转换，PDF已存在: {output_pdf}")
        return output_pdf
    
    try:
        if file_ext == '.docx':
            # 使用pandoc转换DOCX为PDF
            cmd = ['pandoc', input_file, '-o', output_pdf]
            subprocess.run(cmd, check=True)
        elif file_ext == '.epub':
            # 使用pandoc转换EPUB为PDF
            cmd = ['pandoc', input_file, '-o', output_pdf]
            subprocess.run(cmd, check=True)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")
        
        print(f"✅ 转换完成: {output_pdf}")
        return output_pdf
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"转换失败: {e}")


def split_pdf_to_html(pdf_file: str, temp_dir: str) -> List[str]:
    """使用pdftohtml将PDF拆分为HTML页面"""
    html_dir = os.path.join(temp_dir, "html_pages")
    os.makedirs(html_dir, exist_ok=True)
    
    # 使用pdftohtml转换
    try:
        cmd = ['pdftohtml', '-split', pdf_file, 
               os.path.join(html_dir, "page")]
        subprocess.run(cmd, check=True)
        
        # 获取生成的HTML文件列表
        html_files = []
        for file in os.listdir(html_dir):
            if file.endswith('.html'):
                html_files.append(os.path.join(html_dir, file))
        
        html_files.sort()
        print(f"✅ PDF拆分完成，共 {len(html_files)} 页")
        return html_files
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"PDF拆分失败: {e}")


def organize_images(temp_dir: str) -> Dict[str, str]:
    """整理图片文件"""
    html_dir = os.path.join(temp_dir, "html_pages")
    images_dir = os.path.join(temp_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    image_map = {}
    
    # 查找所有图片文件
    for file in os.listdir(html_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            old_path = os.path.join(html_dir, file)
            new_path = os.path.join(images_dir, file)
            
            # 移动图片到专门的目录
            if not os.path.exists(new_path):
                os.rename(old_path, new_path)
            
            image_map[file] = new_path
    
    print(f"📸 整理图片文件: {len(image_map)} 个")
    return image_map


def html_to_markdown(html_file: str, output_file: str) -> bool:
    """将HTML转换为Markdown"""
    if os.path.exists(output_file):
        print(f"⏭️  跳过转换，文件已存在: {output_file}")
        return True
    
    try:
        cmd = ['pandoc', '-f', 'html', '-t', 'markdown', 
               html_file, '-o', output_file]
        subprocess.run(cmd, check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 转换失败: {html_file} -> {output_file}: {e}")
        return False


def split_document_to_markdown(input_file: str, temp_dir: str) -> List[str]:
    """拆分文档为markdown文件"""
    print(f"📄 开始拆分文档: {input_file}")
    
    # 转换为PDF（如果需要）
    pdf_file = convert_to_pdf(input_file, temp_dir)
    
    # 拆分PDF为HTML页面
    html_files = split_pdf_to_html(pdf_file, temp_dir)
    
    # 整理图片文件
    organize_images(temp_dir)
    
    # 转换HTML为Markdown
    md_files = []
    for i, html_file in enumerate(html_files):
        page_num = f"{i+1:04d}"
        md_file = os.path.join(temp_dir, f"page{page_num}.md")
        
        if html_to_markdown(html_file, md_file):
            md_files.append(md_file)
    
    print(f"✅ 文档拆分完成，共 {len(md_files)} 个markdown文件")
    return md_files


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python 02_split_to_md.py <temp_dir>")
        return 1
    
    temp_dir = sys.argv[1]
    
    try:
        # 加载配置
        config = load_config(temp_dir)
        
        # 拆分文档
        md_files = split_document_to_markdown(
            config['input_file'], 
            temp_dir
        )
        
        # 更新配置
        config['md_files'] = md_files
        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"🎯 拆分完成: {len(md_files)} 个文件")
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())