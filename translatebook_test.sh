#!/bin/bash

# translatebook_test.sh - 电子书翻译测试脚本
# 使用简化版模块进行完整流程测试（不依赖外部工具）

set -euo pipefail

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
CUSTOM_PROMPT=""
TEMP_DIR=""
USE_SIMPLE_MODE=false

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${PURPLE}[STEP]${NC} $1"; }

# 帮助信息
show_help() {
    cat << EOF
📚 电子书翻译测试系统 v1.0
使用简化模块进行完整流程演示

用法:
    $0 <input_file> [选项]

参数:
    input_file          输入文件（任意格式）

选项:
    -p, --prompt        自定义翻译提示
    --temp-dir          指定临时目录
    --simple            使用简化模式（无外部依赖）
    -h, --help          显示此帮助信息

示例:
    # 基本测试
    $0 test.pdf --simple

    # 带自定义提示
    $0 paper.pdf -p "专业术语保留原文" --simple

🤖 Powered by Claude AI & UltraThink (Test Mode)
EOF
}

# 解析参数
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
            -p|--prompt)
                CUSTOM_PROMPT="$2"
                shift 2
                ;;
            --temp-dir)
                TEMP_DIR="$2"
                shift 2
                ;;
            --simple)
                USE_SIMPLE_MODE=true
                shift
                ;;
            -*)
                log_error "未知选项: $1"
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
        exit 1
    fi
}

# 创建测试PDF文件（如果不存在）
create_test_file() {
    if [ ! -f "$INPUT_FILE" ]; then
        log_warning "文件不存在，创建测试文件: $INPUT_FILE"
        
        # 创建简单的PDF内容
        cat > "$INPUT_FILE" << 'EOF'
%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
  /Font <<
    /F1 5 0 R
  >>
>>
>>
endobj
4 0 obj
<<
/Length 200
>>
stream
BT
/F1 18 Tf
100 700 Td
(Test Research Paper) Tj
0 -40 Td
/F1 12 Tf
(Abstract: This is a test document for) Tj
0 -20 Td
(the translation system demonstration.) Tj
0 -40 Td
(Introduction: Machine learning has) Tj
0 -20 Td
(revolutionized many fields...) Tj
ET
endstream
endobj
5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000270 00000 n 
0000000522 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
599
%%EOF
EOF
        log_success "测试文件创建完成"
    fi
}

# 运行翻译流程
run_translation_pipeline() {
    local start_time=$(date +%s)
    
    # 显示横幅
    echo -e "${BLUE}"
    cat << "EOF"
 _____ ____      _    _   _ ____       ____   ___   ___  _  ______
|_   _|  _ \    / \  | \ | / ___|     | __ ) / _ \ / _ \| |/ / ___|
  | | | |_) |  / _ \ |  \| \___ \ ____| __ \| | | | | | | ' /\___ \
  | | |  _ <  / ___ \| |\  |___) |_____| |_) | |_| | |_| | . \ ___) |
  |_| |_| \_\/_/   \_\_| \_|____/      |____/ \___/ \___/|_|\_\____/

EOF
    echo -e "${NC}"
    echo "🧪 电子书翻译系统 - 测试模式"
    echo ""
    
    # 步骤1: 环境准备
    log_step "步骤 1/6: 环境准备与参数解析"
    
    local prepare_args=(
        "$INPUT_FILE"
        "--olang" "zh"
        "--input-lang" "auto"
    )
    
    if [ -n "$CUSTOM_PROMPT" ]; then
        prepare_args+=("--prompt" "$CUSTOM_PROMPT")
    fi
    
    if [ -n "$TEMP_DIR" ]; then
        prepare_args+=("--temp-dir" "$TEMP_DIR")
    fi
    
    if ! python3 "$SCRIPT_DIR/01_prepare_env.py" "${prepare_args[@]}"; then
        log_error "环境准备失败"
        return 1
    fi
    
    # 获取临时目录
    if [ -z "$TEMP_DIR" ]; then
        local base_name=$(basename "$INPUT_FILE" | sed 's/\.[^.]*$//')
        TEMP_DIR="${base_name}_temp"
    fi
    
    log_success "环境准备完成，临时目录: $TEMP_DIR"
    
    # 选择脚本版本
    local split_script="02_split_to_md.py"
    local translate_script="03_translate_md.py"
    local html_script="05_md_to_html.py"
    local toc_script="06_add_toc.py"
    
    if [ "$USE_SIMPLE_MODE" = true ]; then
        split_script="02_split_to_md_simple.py"
        translate_script="03_translate_md_mock.py"
        html_script="05_md_to_html_simple.py"
        toc_script="06_add_toc_simple.py"
        log_info "使用简化模式（无外部依赖）"
    fi
    
    # 步骤2-6: 运行处理脚本
    local scripts=(
        "$split_script:文档拆分"
        "$translate_script:AI翻译"
        "04_merge_md.py:内容合并"
        "$html_script:HTML转换"
        "$toc_script:目录生成"
    )
    
    local step=2
    for script_info in "${scripts[@]}"; do
        local script_name="${script_info%%:*}"
        local script_desc="${script_info##*:}"
        
        log_step "步骤 $step/6: $script_desc"
        
        if ! python3 "$SCRIPT_DIR/$script_name" "$TEMP_DIR"; then
            log_error "第 $step 步失败: $script_name"
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
        local size=$(du -h "$html_file" | cut -f1)
        echo "     文件大小: $size"
        
        # 统计字符数
        if [ -f "$md_file" ]; then
            local chars=$(wc -m < "$md_file" 2>/dev/null || echo "未知")
            echo "     字符数量: $chars"
        fi
    fi
    
    if [ -f "$md_file" ]; then
        echo "  📝 Markdown文件: $md_file"
    fi
    
    # 显示配置信息
    local config_file="$TEMP_DIR/config.json"
    if [ -f "$config_file" ]; then
        echo "  ⚙️  配置文件: $config_file"
    fi
    
    echo ""
    if [ -f "$html_file" ]; then
        log_info "在浏览器中打开: file://$PWD/$html_file"
        
        # 显示HTML文件的前几行（预览）
        echo ""
        log_info "HTML预览（前10行）:"
        head -10 "$html_file" | sed 's/^/  /'
        echo "  ..."
    fi
}

# 错误处理
handle_error() {
    local exit_code=$1
    log_error "测试过程中发生错误 (退出码: $exit_code)"
    
    if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
        log_info "临时文件保留在: $TEMP_DIR"
        log_info "可以查看中间结果或排查问题"
    fi
    
    exit $exit_code
}

# 信号处理
trap 'handle_error $?' ERR
trap 'log_warning "用户中断测试"; exit 130' INT TERM

# 主函数
main() {
    # 解析参数
    parse_arguments "$@"
    
    log_info "开始电子书翻译测试..."
    echo "📄 输入文件: $INPUT_FILE"
    echo "💬 自定义提示: ${CUSTOM_PROMPT:-'无'}"
    echo "🧪 测试模式: $([ "$USE_SIMPLE_MODE" = true ] && echo "简化模式" || echo "标准模式")"
    echo ""
    
    # 创建测试文件（如果需要）
    create_test_file
    
    # 运行翻译流程
    run_translation_pipeline
    
    # 显示结果
    show_results
    
    log_success "🎉 测试完成!"
    echo ""
    echo "💡 提示："
    echo "  - 这是测试模式，使用了模拟翻译"
    echo "  - 实际使用请运行: ./translatebook.sh"
    echo "  - 需要安装Claude CLI进行真实翻译"
}

# 运行主函数
main "$@"