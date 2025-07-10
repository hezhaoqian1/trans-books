# 📚 电子书自动翻译系统 (Trans-Books)

一个基于 Claude AI 的高质量电子书翻译工具，支持 PDF、DOCX、EPUB 格式，生成美观的中文电子书。

## ✨ 主要功能

- 🔄 支持多种格式：PDF、DOCX、EPUB
- 🎯 高质量翻译：使用 Claude 4 模型
- 📖 智能拆分：按页面拆分文档保持结构
- 🌟 断点续传：支持中断后继续翻译
- 📱 响应式设计：生成适合各种设备的 HTML
- 🎨 美观模板：专为中文阅读优化的界面
- 📑 自动目录：智能生成书籍目录

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 翻译电子书
./translatebook.sh your_book.pdf

# 带自定义提示翻译
./translatebook.sh your_book.pdf -p "专业术语保留原文"
```

## 📦 项目结构

```
trans-books/
├── 01_prepare_env.py      # 环境准备与参数解析
├── 02_split_to_md.py      # 文档拆分为 Markdown
├── 03_translate_md.py     # Claude 翻译模块
├── 04_merge_md.py         # 合并翻译结果
├── 05_md_to_html.py       # 转换为 HTML
├── 06_add_toc.py          # 生成目录
├── translatebook.sh       # 主执行脚本
├── template.html          # HTML 模板
├── requirements.txt       # Python 依赖
└── tests/                 # 单元测试
```

## 🔧 技术栈

- **Python 3.8+** - 主要开发语言
- **Claude API** - AI 翻译引擎
- **Pandoc** - 文档格式转换
- **PyMuPDF** - PDF 处理
- **python-docx** - Word 文档处理
- **ebooklib** - EPUB 处理

## 📄 许可证

MIT License

---

🤖 **Powered by Claude Code & UltraThink**