#!/usr/bin/env python3
"""
01_prepare_env.py - 环境准备与参数解析

功能：
- 解析命令行参数
- 创建临时工作目录
- 验证输入文件格式
- 检查系统依赖
- 生成配置文件供后续脚本使用
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="电子书翻译系统 - 环境准备",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "input_file",
        help="输入文件路径 (PDF/DOCX/EPUB)"
    )
    
    parser.add_argument(
        "-l", "--input-lang",
        default="auto",
        help="输入语言 (默认: auto)"
    )
    
    parser.add_argument(
        "--olang",
        default="zh",
        help="输出语言 (默认: zh)"
    )
    
    parser.add_argument(
        "-p", "--prompt",
        default="",
        help="自定义翻译提示"
    )
    
    parser.add_argument(
        "--temp-dir",
        help="临时目录路径 (默认: {filename}_temp)"
    )
    
    return parser.parse_args()


def validate_input_file(file_path: str) -> bool:
    """验证输入文件格式"""
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        return False
    
    valid_extensions = ['.pdf', '.docx', '.epub']
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext not in valid_extensions:
        print(f"错误: 不支持的文件格式: {file_ext}")
        print(f"支持的格式: {', '.join(valid_extensions)}")
        return False
    
    return True


def check_dependencies() -> Dict[str, bool]:
    """检查系统依赖"""
    dependencies = {
        'claude': False,
        'pandoc': False,
        'python': True  # 已经在运行Python了
    }
    
    # 检查claude命令
    try:
        import subprocess
        result = subprocess.run(['claude', '--version'], 
                              capture_output=True, text=True)
        dependencies['claude'] = result.returncode == 0
    except FileNotFoundError:
        dependencies['claude'] = False
    
    # 检查pandoc
    try:
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, text=True)
        dependencies['pandoc'] = result.returncode == 0
    except FileNotFoundError:
        dependencies['pandoc'] = False
    
    return dependencies


def create_temp_directory(input_file: str, temp_dir: Optional[str] = None) -> str:
    """创建临时工作目录"""
    if temp_dir is None:
        base_name = Path(input_file).stem
        temp_dir = f"{base_name}_temp"
    
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


def save_config(config: Dict, temp_dir: str) -> str:
    """保存配置文件"""
    config_path = os.path.join(temp_dir, "config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return config_path


def prepare_environment(input_file: str, output_lang: str = "zh", 
                       input_lang: str = "auto", custom_prompt: str = "",
                       temp_dir: Optional[str] = None) -> Dict:
    """准备翻译环境"""
    # 验证输入文件
    if not validate_input_file(input_file):
        raise ValueError(f"无效的输入文件: {input_file}")
    
    # 检查依赖
    deps = check_dependencies()
    missing_deps = [dep for dep, available in deps.items() if not available]
    
    if missing_deps:
        print(f"警告: 缺少以下依赖: {', '.join(missing_deps)}")
        if 'claude' in missing_deps:
            print("请安装 Claude CLI: https://claude.ai/cli")
        if 'pandoc' in missing_deps:
            print("请安装 Pandoc: https://pandoc.org/installing.html")
    
    # 创建临时目录
    temp_dir = create_temp_directory(input_file, temp_dir)
    
    # 生成配置
    config = {
        "input_file": os.path.abspath(input_file),
        "output_lang": output_lang,
        "input_lang": input_lang,
        "custom_prompt": custom_prompt,
        "temp_dir": os.path.abspath(temp_dir),
        "dependencies": deps
    }
    
    # 保存配置
    config_path = save_config(config, temp_dir)
    
    print(f"✅ 环境准备完成")
    print(f"📁 临时目录: {temp_dir}")
    print(f"⚙️  配置文件: {config_path}")
    
    return config


def main():
    """主函数"""
    args = parse_arguments()
    
    try:
        config = prepare_environment(
            input_file=args.input_file,
            output_lang=args.olang,
            input_lang=args.input_lang,
            custom_prompt=args.prompt,
            temp_dir=args.temp_dir
        )
        
        print(f"🎯 准备翻译: {config['input_file']}")
        print(f"🌍 {config['input_lang']} -> {config['output_lang']}")
        
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())