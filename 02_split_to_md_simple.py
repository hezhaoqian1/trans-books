#!/usr/bin/env python3
"""
02_split_to_md_simple.py - 简化版文档拆分（用于测试）

功能：
- 创建模拟的markdown文件用于测试流程
- 不依赖于外部工具（pandoc, pdftohtml）
"""

import json
import os
import sys
from pathlib import Path


def load_config(temp_dir: str) -> dict:
    """加载配置文件"""
    config_path = os.path.join(temp_dir, "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_mock_markdown_files(temp_dir: str, input_file: str) -> list:
    """创建模拟的markdown文件用于测试"""
    print(f"📄 创建模拟markdown文件用于测试...")
    
    # 创建images目录
    images_dir = os.path.join(temp_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # 根据输入文件类型创建不同的内容
    file_ext = Path(input_file).suffix.lower()
    
    if "paper" in Path(input_file).stem.lower():
        # 学术论文内容
        pages_content = [
            """# A Study of Machine Learning Applications in Natural Language Processing

## Abstract

This paper presents a comprehensive review of machine learning applications in natural language processing (NLP). We examine various techniques including transformer architectures, attention mechanisms, and their impact on modern AI systems.""",
            
            """## 1. Introduction

Natural Language Processing has evolved dramatically over the past decade. The introduction of deep learning methods has revolutionized how machines understand and generate human language.

### 1.1 Background

Machine learning, particularly deep learning, has become the cornerstone of modern NLP systems.""",
            
            """### 1.2 Scope of Study

This research focuses on three main areas:
- Transformer architectures and their variants
- Attention mechanisms in sequence-to-sequence models
- Pre-trained language models and fine-tuning approaches""",
            
            """## 2. Methodology

Our methodology consists of systematic literature review and experimental validation. We analyzed over 200 research papers published between 2017 and 2024.

### 2.1 Data Collection

The dataset includes:
- Academic papers from major conferences (ACL, EMNLP, NAACL)
- Industry research reports
- Open-source implementations and benchmarks"""
        ]
    else:
        # 通用文档内容
        pages_content = [
            """# Document Title

This is the first page of the document. It contains important information about the topic being discussed.""",
            
            """## Chapter 1: Introduction

This chapter introduces the main concepts and provides background information necessary to understand the content.""",
            
            """## Chapter 2: Main Content

Here we dive into the detailed discussion of the primary topics covered in this document.""",
            
            """## Conclusion

This section summarizes the key points and provides final thoughts on the subject matter."""
        ]
    
    md_files = []
    for i, content in enumerate(pages_content):
        page_num = f"{i+1:04d}"
        md_file = os.path.join(temp_dir, f"page{page_num}.md")
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        md_files.append(md_file)
        print(f"📝 创建: page{page_num}.md")
    
    print(f"✅ 模拟文档拆分完成，共 {len(md_files)} 个文件")
    return md_files


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python 02_split_to_md_simple.py <temp_dir>")
        return 1
    
    temp_dir = sys.argv[1]
    
    try:
        # 加载配置
        config = load_config(temp_dir)
        
        # 创建模拟markdown文件
        md_files = create_mock_markdown_files(temp_dir, config['input_file'])
        
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