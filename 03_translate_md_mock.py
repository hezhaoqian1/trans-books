#!/usr/bin/env python3
"""
03_translate_md_mock.py - 模拟翻译模块（用于测试）

功能：
- 模拟Claude翻译过程，不需要实际API调用
- 生成中文翻译内容用于测试流程
- 保持与真实翻译脚本相同的接口
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict


def load_config(temp_dir: str) -> Dict:
    """加载配置文件"""
    config_path = os.path.join(temp_dir, "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_output_filename(md_file: str) -> str:
    """生成输出文件名"""
    base_name = Path(md_file).stem
    dir_name = Path(md_file).parent
    return os.path.join(dir_name, f"output_{base_name}.md")


def mock_translate_content(content: str, target_lang: str = "zh", custom_prompt: str = "") -> str:
    """模拟翻译内容"""
    
    # 简单的英中翻译映射（用于演示）
    translations = {
        "A Study of Machine Learning Applications in Natural Language Processing": "机器学习在自然语言处理中的应用研究",
        "Abstract": "摘要",
        "Introduction": "引言",
        "Methodology": "方法论", 
        "Results and Discussion": "结果与讨论",
        "Conclusion": "结论",
        "Chapter": "章节",
        "Document Title": "文档标题",
        "Main Content": "主要内容",
        "Background": "背景",
        "Scope of Study": "研究范围",
        "Data Collection": "数据收集",
        "This paper presents": "本文提出",
        "comprehensive review": "全面回顾",
        "machine learning applications": "机器学习应用",
        "natural language processing": "自然语言处理",
        "transformer architectures": "变换器架构",
        "attention mechanisms": "注意力机制",
        "modern AI systems": "现代人工智能系统",
        "deep learning methods": "深度学习方法",
        "revolutionized": "彻底改变",
        "understand and generate": "理解和生成",
        "human language": "人类语言",
        "systematic literature review": "系统文献综述",
        "experimental validation": "实验验证",
        "research papers": "研究论文",
        "academic papers": "学术论文",
        "conferences": "会议",
        "industry research reports": "行业研究报告",
        "open-source implementations": "开源实现",
        "benchmarks": "基准测试"
    }
    
    # 开始翻译过程
    translated_content = content
    
    # 应用翻译映射
    for english, chinese in translations.items():
        translated_content = translated_content.replace(english, chinese)
    
    # 处理一些常见的英文词汇
    common_replacements = {
        "and": "和",
        "the": "",
        "of": "的",
        "in": "在",
        "to": "到",
        "for": "为",
        "with": "与",
        "by": "通过",
        "from": "从",
        "that": "那",
        "this": "这",
        "is": "是",
        "are": "是",
        "we": "我们",
        "has": "已经",
        "have": "有",
        "been": "被",
        "over": "超过",
        "between": "之间",
        "includes": "包括",
        "including": "包括",
        "analysis": "分析",
        "approach": "方法",
        "techniques": "技术",
        "models": "模型",
        "systems": "系统",
        "information": "信息",
        "important": "重要",
        "necessary": "必要",
        "content": "内容",
        "discussed": "讨论",
        "provides": "提供",
        "topics": "主题",
        "detailed": "详细",
        "discussion": "讨论",
        "primary": "主要",
        "covered": "涵盖",
        "document": "文档",
        "section": "部分",
        "summarizes": "总结",
        "key points": "要点",
        "final thoughts": "最终想法",
        "subject matter": "主题内容"
    }
    
    # 应用常见词汇替换（只在单词边界处替换）
    import re
    for english, chinese in common_replacements.items():
        pattern = r'\b' + re.escape(english) + r'\b'
        translated_content = re.sub(pattern, chinese, translated_content, flags=re.IGNORECASE)
    
    # 清理多余的空格和标点
    translated_content = re.sub(r'\s+', ' ', translated_content)
    translated_content = re.sub(r'\s+([，。！？])', r'\1', translated_content)
    
    # 添加自定义提示的效果（如果有）
    if custom_prompt and "专业术语" in custom_prompt:
        # 保留一些专业术语的英文原文
        technical_terms = [
            "transformer", "attention", "BERT", "GPT", "RNN", "CNN", "API",
            "NLP", "AI", "ML", "ACL", "EMNLP", "NAACL"
        ]
        for term in technical_terms:
            pattern = f"({term})"
            translated_content = re.sub(pattern, r'\1', translated_content, flags=re.IGNORECASE)
    
    return translated_content.strip()


def mock_translate_file(md_file: str, output_file: str, target_lang: str = "zh", 
                       custom_prompt: str = "", max_retries: int = 3) -> bool:
    """模拟翻译单个markdown文件"""
    
    # 检查是否已翻译
    if os.path.exists(output_file):
        print(f"⏭️  跳过已翻译: {Path(md_file).name}")
        return True
    
    print(f"🤖 模拟翻译: {Path(md_file).name}")
    
    try:
        # 读取原文件内容
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            # 如果文件为空，创建空的输出文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("")
            return True
        
        # 模拟翻译过程（添加一点延迟使其更真实）
        time.sleep(0.5)
        
        # 执行模拟翻译
        translated_content = mock_translate_content(content, target_lang, custom_prompt)
        
        # 保存翻译结果
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(translated_content)
        
        print(f"✅ 翻译完成: {Path(md_file).name}")
        return True
        
    except Exception as e:
        print(f"❌ 翻译异常: {e}")
        return False


def translate_markdown_files(md_files: List[str], temp_dir: str, 
                           target_lang: str = "zh", custom_prompt: str = "") -> List[str]:
    """批量翻译markdown文件"""
    
    translated_files = []
    total_files = len(md_files)
    print(f"📚 开始模拟翻译 {total_files} 个文件...")
    
    for i, md_file in enumerate(md_files, 1):
        print(f"\n[{i}/{total_files}] 处理: {Path(md_file).name}")
        
        output_file = get_output_filename(md_file)
        
        if mock_translate_file(md_file, output_file, target_lang, custom_prompt):
            translated_files.append(output_file)
        else:
            print(f"⚠️  跳过失败的文件: {Path(md_file).name}")
    
    print(f"\n🎯 模拟翻译完成: {len(translated_files)}/{total_files} 个文件")
    return translated_files


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python 03_translate_md_mock.py <temp_dir>")
        return 1
    
    temp_dir = sys.argv[1]
    
    try:
        # 加载配置
        config = load_config(temp_dir)
        
        if 'md_files' not in config:
            print("❌ 错误: 未找到markdown文件列表，请先运行 02_split_to_md.py")
            return 1
        
        # 翻译文件
        translated_files = translate_markdown_files(
            config['md_files'],
            temp_dir,
            config.get('output_lang', 'zh'),
            config.get('custom_prompt', '')
        )
        
        # 更新配置
        config['translated_files'] = translated_files
        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        if translated_files:
            print(f"🎉 模拟翻译任务完成!")
            return 0
        else:
            print(f"💥 模拟翻译任务失败!")
            return 1
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())