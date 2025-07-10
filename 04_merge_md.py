#!/usr/bin/env python3
"""
04_merge_md.py - 合并翻译结果

功能：
- 按页面顺序合并所有翻译后的markdown文件
- 使用分隔符分隔页面
- 保持图片引用的正确性
- 生成最终的合并文件
"""

import json
import os
import sys
from pathlib import Path
from typing import List


def load_config(temp_dir: str) -> dict:
    """加载配置文件"""
    config_path = os.path.join(temp_dir, "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def sort_translated_files(translated_files: List[str]) -> List[str]:
    """按页面顺序排序翻译后的文件"""
    def extract_page_number(file_path: str) -> int:
        """从文件名中提取页码"""
        filename = Path(file_path).stem
        # 文件名格式: output_pageXXXX
        if 'page' in filename:
            page_part = filename.split('page')[-1]
            # 提取数字部分
            page_num = ''.join(filter(str.isdigit, page_part))
            return int(page_num) if page_num else 0
        return 0
    
    return sorted(translated_files, key=extract_page_number)


def fix_image_references(content: str, temp_dir: str) -> str:
    """修正图片引用路径"""
    images_dir = os.path.join(temp_dir, "images")
    
    # 查找所有图片引用
    import re
    
    # 匹配markdown图片语法: ![alt](path)
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    
    def replace_image_path(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        
        # 如果是相对路径，转换为正确的相对路径
        if not os.path.isabs(image_path):
            # 检查图片是否存在于images目录
            image_name = os.path.basename(image_path)
            full_image_path = os.path.join(images_dir, image_name)
            
            if os.path.exists(full_image_path):
                # 使用相对于输出文件的路径
                relative_path = os.path.join("images", image_name)
                return f'![{alt_text}]({relative_path})'
        
        return match.group(0)  # 如果无法处理，保持原样
    
    return re.sub(image_pattern, replace_image_path, content)


def merge_translated_files(temp_dir: str, output_file: str = "output.md") -> str:
    """合并翻译后的markdown文件"""
    config = load_config(temp_dir)
    
    if 'translated_files' not in config:
        raise ValueError("未找到翻译文件列表")
    
    translated_files = config['translated_files']
    
    if not translated_files:
        raise ValueError("翻译文件列表为空")
    
    # 排序文件
    sorted_files = sort_translated_files(translated_files)
    
    output_path = os.path.join(temp_dir, output_file)
    
    print(f"📝 开始合并 {len(sorted_files)} 个翻译文件...")
    
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for i, file_path in enumerate(sorted_files):
            if not os.path.exists(file_path):
                print(f"⚠️  警告: 文件不存在，跳过: {file_path}")
                continue
            
            print(f"📄 合并: {Path(file_path).name}")
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as infile:
                content = infile.read().strip()
            
            # 修正图片引用
            content = fix_image_references(content, temp_dir)
            
            # 写入内容
            if content:
                outfile.write(content)
            
            # 添加页面分隔符（除了最后一个文件）
            if i < len(sorted_files) - 1:
                outfile.write('\n\n---\n\n')
    
    print(f"✅ 合并完成: {output_path}")
    return output_path


def add_book_metadata(merged_file: str, config: dict) -> None:
    """在合并文件开头添加书籍元数据"""
    
    # 生成元数据
    input_filename = Path(config['input_file']).stem
    metadata = f"""# {input_filename}

**翻译信息:**
- 原文件: {config['input_file']}
- 翻译语言: {config['input_lang']} → {config['output_lang']}
- 翻译时间: {config.get('timestamp', 'Unknown')}
- 自定义提示: {config.get('custom_prompt', '无')}

---

"""
    
    # 读取原内容
    with open(merged_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # 写入元数据和原内容
    with open(merged_file, 'w', encoding='utf-8') as f:
        f.write(metadata)
        f.write(original_content)


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python 04_merge_md.py <temp_dir>")
        return 1
    
    temp_dir = sys.argv[1]
    
    try:
        # 合并文件
        merged_file = merge_translated_files(temp_dir)
        
        # 添加元数据
        config = load_config(temp_dir)
        add_book_metadata(merged_file, config)
        
        # 更新配置
        config['merged_file'] = merged_file
        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"🎯 合并任务完成: {merged_file}")
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())