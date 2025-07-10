#!/bin/bash

# translatebook.sh - 电子书翻译主脚本
# 功能：串联所有处理步骤，提供统一的命令行接口

set -euo pipefail  # 严格模式

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 全局变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_FILE=""
INPUT_LANG="auto"
OUTPUT_LANG="zh"
CUSTOM_PROMPT=""
TEMP_DIR=""
CLEANUP=false
VERBOSE=false

# 帮助信息
show_help() {
    cat << EOF
📚 电子书翻译系统 v1.0
使用 Claude AI 进行高质量电子书翻译

用法:
    $0 <input_file> [选项]

参数:
    input_file          输入文件 (PDF/DOCX/EPUB)

选项:
    -l, --input-lang    输入语言 (默认: auto)
    --olang             输出语言 (默认: zh)
    -p, --prompt        自定义翻译提示
    --temp-dir          指定临时目录
    --cleanup           完成后清理临时文件
    -v, --verbose       详细输出
    -h, --help          显示此帮助信息

示例:
    # 基本翻译
    $0 book.pdf

    # 带自定义提示
    $0 book.pdf -p "专业术语保留原文"

    # 指定语言
    $0 book.pdf -l en --olang zh

    # 完整选项
    $0 book.pdf -l en --olang zh -p "简洁翻译" --cleanup -v

支持的语言代码:
    auto - 自动检测
    en   - 英语
    zh   - 中文
    ja   - 日语
    ko   - 韩语
    fr   - 法语
    de   - 德语
    es   - 西班牙语

🤖 Powered by Claude AI & UltraThink
EOF
}

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 详细日志
log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${CYAN}[VERBOSE]${NC} $1"
    fi
}

# 检查依赖
check_dependencies() {
    log_step "检查系统依赖..."
    
    local missing_deps=()
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # 检查Claude CLI
    if ! command -v claude &> /dev/null; then
        missing_deps+=("claude")
    fi
    
    # 检查Pandoc
    if ! command -v pandoc &> /dev/null; then
        missing_deps+=("pandoc")
    fi
    
    # 检查pdftohtml
    if ! command -v pdftohtml &> /dev/null; then
        missing_deps+=("pdftohtml")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "缺少以下依赖:"
        for dep in "${missing_deps[@]}"; do
            echo "  - $dep"
        done
        
        echo ""
        echo "安装说明:"
        echo "  Python3: https://www.python.org/downloads/"
        echo "  Claude CLI: https://claude.ai/cli"
        echo "  Pandoc: https://pandoc.org/installing.html"
        echo "  pdftohtml: sudo apt-get install poppler-utils (Ubuntu/Debian)"
        echo "            brew install poppler (macOS)"
        
        return 1
    fi
    
    log_success "所有依赖检查通过"
}

# 检查Python包
check_python_packages() {
    log_step "检查Python包依赖..."
    
    local packages=(
        "json"
        "os" 
        "sys"
        "pathlib"
        "subprocess"
        "argparse"
        "re"
        "time"
        "shutil"
    )
    
    for package in "${packages[@]}"; do
        if ! python3 -c "import $package" 2>/dev/null; then
            log_warning "Python包 $package 可能缺失"
        fi
    done
    
    # 检查可选包
    if ! python3 -c "import bs4" 2>/dev/null; then
        log_warning "建议安装: pip install beautifulsoup4"
    fi
    
    log_success "Python包检查完成"
}

# 解析命令行参数
parse_arguments() {
    if [ $# -eq 0 ]; then
        log_error "请提供输入文件"
        show_help
        exit 1
    fi
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -l|--input-lang)
                INPUT_LANG="$2"
                shift 2
                ;;
            --olang)
                OUTPUT_LANG="$2"
                shift 2
                ;;
            -p|--prompt)
                CUSTOM_PROMPT="$2"
                shift 2
                ;;
            --temp-dir)
                TEMP_DIR="$2"
                shift 2
                ;;
            --cleanup)
                CLEANUP=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -*)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
            *)
                if [ -z "$INPUT_FILE" ]; then
                    INPUT_FILE="$1"
                else
                    log_error "只能指定一个输入文件"
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    if [ -z "$INPUT_FILE" ]; then
        log_error "请提供输入文件"
        show_help
        exit 1
    fi
    
    if [ ! -f "$INPUT_FILE" ]; then
        log_error "文件不存在: $INPUT_FILE"
        exit 1
    fi
}

# 显示配置信息
show_config() {
    log_info "翻译配置:"
    echo "  📄 输入文件: $INPUT_FILE"
    echo "  🌍 输入语言: $INPUT_LANG"
    echo "  🎯 输出语言: $OUTPUT_LANG"
    echo "  💬 自定义提示: ${CUSTOM_PROMPT:-'无'}"
    echo "  📁 临时目录: ${TEMP_DIR:-'自动生成'}"
    echo "  🧹 自动清理: $CLEANUP"
    echo "  📝 详细输出: $VERBOSE"
    echo ""
}

# 运行Python脚本
run_python_script() {
    local script_name="$1"
    local script_path="$SCRIPT_DIR/$script_name"
    
    if [ ! -f "$script_path" ]; then
        log_error "脚本不存在: $script_path"
        return 1
    fi
    
    log_step "运行 $script_name..."
    log_verbose "执行: python3 '$script_path' '$TEMP_DIR'"
    
    if [ "$VERBOSE" = true ]; then
        python3 "$script_path" "$TEMP_DIR"
    else
        python3 "$script_path" "$TEMP_DIR" 2>/dev/null || {
            log_error "$script_name 执行失败"
            return 1
        }
    fi
    
    log_success "$script_name 完成"
}

# 主要翻译流程
run_translation_pipeline() {
    local start_time=$(date +%s)
    
    # 步骤1: 环境准备
    log_step "步骤 1/6: 环境准备与参数解析"
    
    local prepare_args=(
        "$INPUT_FILE"
        "--olang" "$OUTPUT_LANG"
        "--input-lang" "$INPUT_LANG"
    )
    
    if [ -n "$CUSTOM_PROMPT" ]; then
        prepare_args+=("--prompt" "$CUSTOM_PROMPT")
    fi
    
    if [ -n "$TEMP_DIR" ]; then
        prepare_args+=("--temp-dir" "$TEMP_DIR")
    fi
    
    log_verbose "执行: python3 01_prepare_env.py ${prepare_args[*]}"
    
    if ! python3 "$SCRIPT_DIR/01_prepare_env.py" "${prepare_args[@]}"; then
        log_error "环境准备失败"
        return 1
    fi
    
    # 获取实际的临时目录路径
    if [ -z "$TEMP_DIR" ]; then
        local base_name=$(basename "$INPUT_FILE" | sed 's/\.[^.]*$//')
        TEMP_DIR="${base_name}_temp"
    fi
    
    if [ ! -d "$TEMP_DIR" ]; then
        log_error "临时目录不存在: $TEMP_DIR"
        return 1
    fi
    
    log_success "环境准备完成，临时目录: $TEMP_DIR"
    
    # 步骤2-6: 运行其他脚本
    local scripts=(
        "02_split_to_md.py"
        "03_translate_md.py"
        "04_merge_md.py"
        "05_md_to_html.py"
        "06_add_toc.py"
    )
    
    local step=2
    for script in "${scripts[@]}"; do
        log_step "步骤 $step/6: $(basename "$script" .py | sed 's/_/ /g')"
        
        if ! run_python_script "$script"; then
            log_error "翻译流程在步骤 $step 失败"
            return 1
        fi
        
        ((step++))
    done
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_success "翻译流程完成! 耗时: ${duration}秒"
}

# 显示结果
show_results() {
    log_step "翻译结果:"
    
    local html_file="$TEMP_DIR/book.html"
    local md_file="$TEMP_DIR/output.md"
    
    if [ -f "$html_file" ]; then
        echo "  📱 HTML电子书: $html_file"
        
        # 显示文件大小
        local size=$(du -h "$html_file" | cut -f1)
        echo "     文件大小: $size"
        
        # 统计字符数
        if [ -f "$md_file" ]; then
            local chars=$(wc -m < "$md_file")
            echo "     字符数量: $chars"
        fi
    fi
    
    if [ -f "$md_file" ]; then
        echo "  📝 Markdown文件: $md_file"
    fi
    
    # 显示图片数量
    local images_dir="$TEMP_DIR/images"
    if [ -d "$images_dir" ]; then
        local image_count=$(find "$images_dir" -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.gif" \) | wc -l)
        echo "  🖼️  图片数量: $image_count"
    fi
    
    echo ""
    log_info "在浏览器中打开: file://$PWD/$html_file"
}

# 清理临时文件
cleanup_temp_files() {
    if [ "$CLEANUP" = true ] && [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
        log_step "清理临时文件..."
        
        # 保留最终结果
        local output_dir="$(basename "$INPUT_FILE" .${INPUT_FILE##*.})_output"
        mkdir -p "$output_dir"
        
        if [ -f "$TEMP_DIR/book.html" ]; then
            cp "$TEMP_DIR/book.html" "$output_dir/"
        fi
        
        if [ -f "$TEMP_DIR/output.md" ]; then
            cp "$TEMP_DIR/output.md" "$output_dir/"
        fi
        
        if [ -d "$TEMP_DIR/images" ]; then
            cp -r "$TEMP_DIR/images" "$output_dir/"
        fi
        
        # 删除临时目录
        rm -rf "$TEMP_DIR"
        
        log_success "临时文件已清理，结果保存在: $output_dir"
        
        # 更新结果路径
        TEMP_DIR="$output_dir"
    fi
}

# 错误处理
handle_error() {
    local exit_code=$1
    log_error "翻译过程中发生错误 (退出码: $exit_code)"
    
    if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
        log_info "临时文件保留在: $TEMP_DIR"
        log_info "可以查看日志排查问题或手动重试"
    fi
    
    exit $exit_code
}

# 信号处理
trap 'handle_error $?' ERR
trap 'log_warning "用户中断操作"; exit 130' INT TERM

# 主函数
main() {
    echo -e "${BLUE}"
    cat << "EOF"
 _____ ____      _    _   _ ____       ____   ___   ___  _  ______
|_   _|  _ \    / \  | \ | / ___|     | __ ) / _ \ / _ \| |/ / ___|
  | | | |_) |  / _ \ |  \| \___ \ ____| __ \| | | | | | | ' /\___ \
  | | |  _ <  / ___ \| |\  |___) |_____| |_) | |_| | |_| | . \ ___) |
  |_| |_| \_\/_/   \_\_| \_|____/      |____/ \___/ \___/|_|\_\____/

EOF
    echo -e "${NC}"
    echo "🤖 AI-Powered Ebook Translation System"
    echo ""
    
    # 解析参数
    parse_arguments "$@"
    
    # 显示配置
    show_config
    
    # 检查依赖
    check_dependencies
    check_python_packages
    
    # 运行翻译流程
    run_translation_pipeline
    
    # 显示结果
    show_results
    
    # 清理文件
    cleanup_temp_files
    
    log_success "🎉 翻译任务全部完成!"
    echo ""
    echo "使用说明:"
    echo "  - 在浏览器中打开HTML文件查看结果"
    echo "  - 按 'T' 键回到顶部，按 'B' 键回到底部"
    echo "  - 点击图片可以放大查看"
    echo "  - 代码块支持一键复制"
    echo ""
    echo "如有问题，请查看: https://github.com/hezhaoqian1/trans-books"
}

# 运行主函数
main "$@"