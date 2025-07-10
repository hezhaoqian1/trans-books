#!/usr/bin/env python3
"""
03_translate_md.py - Claude AI翻译模块

功能：
- 调用Claude命令行进行翻译
- 支持自定义翻译prompt
- 断点续传功能
- 错误重试机制
- 翻译进度显示
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict
import subprocess


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


def construct_translation_prompt(target_lang: str, custom_prompt: str = "") -> str:
    """构造翻译提示"""
    base_prompt = f"请翻译以下内容为{target_lang}，保持markdown格式完整性。"
    
    if custom_prompt:
        base_prompt += f" 特殊要求：{custom_prompt}"
    
    return base_prompt


def translate_with_claude(md_file: str, output_file: str, prompt: str, 
                         max_retries: int = 3) -> bool:
    """使用Claude翻译单个markdown文件"""
    
    # 检查是否已翻译
    if os.path.exists(output_file):
        print(f"⏭️  跳过已翻译: {Path(md_file).name}")
        return True
    
    print(f"🤖 翻译中: {Path(md_file).name}")
    
    for attempt in range(max_retries):
        try:
            # 读取原文件内容
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                # 如果文件为空，创建空的输出文件
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("")
                return True
            
            # 构造Claude命令
            full_prompt = f"{prompt}\n\n{content}"
            
            # 使用Claude进行翻译
            cmd = [
                'claude', 
                '--model', 'claude-sonnet-4-20250514',  # 强制使用Claude 4 Sonnet
                full_prompt
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                # 提取翻译结果
                translated_content = extract_translation_content(result.stdout)
                
                # 保存翻译结果
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(translated_content)
                
                print(f"✅ 翻译完成: {Path(md_file).name}")
                return True
            else:
                print(f"❌ 翻译失败 (尝试 {attempt + 1}/{max_retries}): {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ 翻译超时 (尝试 {attempt + 1}/{max_retries})")
        except Exception as e:
            print(f"❌ 翻译异常 (尝试 {attempt + 1}/{max_retries}): {e}")
        
        if attempt < max_retries - 1:
            print(f"⏳ 等待 {(attempt + 1) * 5} 秒后重试...")
            time.sleep((attempt + 1) * 5)
    
    print(f"💥 翻译失败，已达最大重试次数: {Path(md_file).name}")
    return False


def extract_translation_content(claude_output: str) -> str:
    """从Claude输出中提取翻译内容"""
    # Claude的输出通常直接就是翻译结果
    # 如果有特殊格式，在这里处理
    
    lines = claude_output.strip().split('\n')
    
    # 移除可能的系统消息或元数据
    content_lines = []
    skip_next = False
    
    for line in lines:
        # 跳过明显的系统消息
        if line.startswith(('模型：', 'Model:', '```', '---')):
            continue
        if 'Generated with Claude' in line:
            continue
        if skip_next:
            skip_next = False
            continue
        
        content_lines.append(line)
    
    return '\n'.join(content_lines).strip()


def translate_markdown_files(md_files: List[str], temp_dir: str, 
                           target_lang: str = "zh", custom_prompt: str = "") -> List[str]:
    """批量翻译markdown文件"""
    
    prompt = construct_translation_prompt(target_lang, custom_prompt)
    translated_files = []
    
    total_files = len(md_files)
    print(f"📚 开始翻译 {total_files} 个文件...")
    
    for i, md_file in enumerate(md_files, 1):
        print(f"\n[{i}/{total_files}] 处理: {Path(md_file).name}")
        
        output_file = get_output_filename(md_file)
        
        if translate_with_claude(md_file, output_file, prompt):
            translated_files.append(output_file)
        else:
            print(f"⚠️  跳过失败的文件: {Path(md_file).name}")
    
    print(f"\n🎯 翻译完成: {len(translated_files)}/{total_files} 个文件")
    return translated_files


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python 03_translate_md.py <temp_dir>")
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
            print(f"🎉 翻译任务完成!")
            return 0
        else:
            print(f"💥 翻译任务失败!")
            return 1
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())