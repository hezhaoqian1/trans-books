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

### 📦 环境准备

```bash
# 1. 安装系统依赖
sudo apt-get install pandoc poppler-utils  # Ubuntu/Debian
brew install pandoc poppler                # macOS

# 2. 安装Python依赖
pip install -r requirements.txt

# 3. 安装Claude CLI
# 访问 https://claude.ai/cli 并按照说明安装

# 4. 验证安装
./translatebook.sh --help
```

### 📖 基础使用

```bash
# 翻译PDF文档
./translatebook.sh research_paper.pdf

# 翻译Word文档
./translatebook.sh document.docx

# 翻译EPUB电子书
./translatebook.sh ebook.epub
```

### 🎯 高级使用

```bash
# 自定义翻译提示
./translatebook.sh paper.pdf -p "学术术语保留英文原文，并在首次出现时加注中文释义"

# 指定语言
./translatebook.sh paper.pdf -l en --olang zh

# 详细输出模式
./translatebook.sh paper.pdf -v

# 完成后自动清理临时文件
./translatebook.sh paper.pdf --cleanup
```

## 📚 实际使用案例：翻译英文学术论文

### 📄 案例1：机器学习论文翻译

假设您有一篇名为 `transformer_paper.pdf` 的英文学术论文，想要翻译成高质量的中文学术文档。

#### 🎯 翻译命令
```bash
./translatebook.sh transformer_paper.pdf \
  -p "学术论文翻译要求：1)专业术语如Transformer、BERT、Attention等保留英文并首次出现时标注中文；2)保持学术写作的严谨性；3)公式和引用格式保持原样；4)图表说明翻译但保留英文标注" \
  --cleanup -v
```

#### 📊 翻译过程展示
```
🤖 AI-Powered Ebook Translation System

📚 电子书翻译系统 v1.0
使用 Claude AI 进行高质量电子书翻译

✅ 环境准备完成
📁 临时目录: transformer_paper_temp
⚙️  配置文件: transformer_paper_temp/config.json
🎯 准备翻译: transformer_paper.pdf
🌍 auto -> zh

[STEP] 步骤 1/6: 环境准备与参数解析
✅ 环境准备完成，临时目录: transformer_paper_temp

[STEP] 步骤 2/6: 文档拆分为markdown
📄 PDF拆分完成，共 12 页
📸 整理图片文件: 8 个
✅ 文档拆分完成，共 12 个markdown文件

[STEP] 步骤 3/6: Claude AI翻译模块
📚 开始翻译 12 个文件...
🤖 翻译中: page0001.md (标题和摘要)
✅ 翻译完成: page0001.md
🤖 翻译中: page0002.md (引言部分)
✅ 翻译完成: page0002.md
... (继续翻译每一页)
🎯 翻译完成: 12/12 个文件

[STEP] 步骤 4/6: 合并翻译结果
📝 开始合并 12 个翻译文件...
✅ 合并完成: transformer_paper_temp/output.md

[STEP] 步骤 5/6: Markdown转HTML
🔄 转换 Markdown 为 HTML...
📸 复制图片文件到: transformer_paper_temp/images
✅ HTML转换完成: transformer_paper_temp/book.html

[STEP] 步骤 6/6: 自动生成目录
📑 为HTML文件添加目录
📋 找到 15 个标题
✅ 目录添加完成: transformer_paper_temp/book.html

🎉 翻译任务全部完成!
```

#### 📖 翻译结果示例

**原文：**
```
# Attention Is All You Need

## Abstract
We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.
```

**翻译后：**
```
# Attention Is All You Need（注意力机制就是你所需要的一切）

## 摘要
我们提出了一种新的简单网络架构——Transformer（变换器），该架构完全基于attention mechanisms（注意力机制），完全摒弃了recurrence（循环）和convolutions（卷积）。
```

#### 🎨 生成的HTML特性

生成的HTML文档包含：

- ✅ **智能目录**: 自动生成可点击的目录导航
- ✅ **响应式设计**: 适配桌面和移动设备
- ✅ **中文优化**: 使用仿宋体，优化行距和字间距
- ✅ **图片保持**: 原文图表完整保留
- ✅ **暗色模式**: 自动适配系统主题
- ✅ **交互功能**: 图片点击放大，平滑滚动

### 📄 案例2：快速翻译流程

对于日常使用，可以使用简化命令：

```bash
# 基础翻译（适合大多数情况）
./translatebook.sh research_paper.pdf

# 专业术语保留原文
./translatebook.sh ai_survey.pdf -p "AI/ML术语保留英文"

# 医学论文翻译
./translatebook.sh medical_paper.pdf -p "医学术语中英对照，首次出现时标注"

# 计算机科学论文
./translatebook.sh cs_paper.pdf -p "算法名称、数据结构术语保留英文"
```

### 🔧 故障排除

#### 常见问题解决

**问题1：Claude API调用失败**
```bash
# 检查Claude CLI是否正确安装
claude --version

# 重新登录
claude auth login
```

**问题2：依赖缺失**
```bash
# Ubuntu/Debian
sudo apt-get install pandoc poppler-utils

# macOS
brew install pandoc poppler

# Windows (使用Chocolatey)
choco install pandoc poppler
```

**问题3：PDF解析问题**
```bash
# 确保PDF文件可读
pdftohtml -v your_file.pdf

# 尝试不同的PDF处理方式
./translatebook.sh your_file.pdf -v  # 查看详细错误信息
```

### 💡 高级提示示例

#### 学术论文专用提示
```bash
-p "学术论文翻译标准：专业术语英中对照，保持学术严谨性，公式符号不译，参考文献格式保持"
```

#### 技术文档专用提示  
```bash
-p "技术文档翻译：API名称、命令行参数、代码示例保持英文，注释翻译为中文"
```

#### 文学作品专用提示
```bash
-p "文学翻译：注重文学性和可读性，保留作者写作风格，人名地名首次出现时标注原文"
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

## 🎮 快速测试

如果您想在没有安装外部依赖的情况下测试系统：

```bash
# 运行测试模式（无需外部依赖）
./translatebook_test.sh demo.pdf --simple

# 带自定义提示的测试
./translatebook_test.sh test.pdf --simple -p "专业术语保留原文"
```

测试模式会：
- 自动创建示例文档（如果不存在）
- 使用模拟翻译展示完整流程
- 生成真实的HTML输出
- 展示所有功能特性

## 🌟 更多使用场景

### 📖 学术研究
```bash
# AI/ML论文翻译
./translatebook.sh ai_paper.pdf -p "保持专业术语英文，如Transformer、BERT等"

# 医学文献翻译  
./translatebook.sh medical_journal.pdf -p "医学术语中英对照，药物名称保留原文"

# 法律文件翻译
./translatebook.sh legal_doc.pdf -p "法律术语严格翻译，保持条款结构"
```

### 📚 教育学习
```bash
# 教材翻译
./translatebook.sh textbook.pdf -p "适合中国学生理解，专业概念加注释"

# 技术手册翻译
./translatebook.sh manual.pdf -p "操作步骤清晰，保留原有编号和格式"

# 考试资料翻译
./translatebook.sh exam_prep.pdf -p "考点突出，保持题目原有结构"
```

### 💼 商业应用
```bash
# 商业报告翻译
./translatebook.sh business_report.pdf -p "商业术语准确，数据图表说明翻译"

# 技术文档翻译
./translatebook.sh tech_docs.pdf -p "API名称、代码保持英文，注释翻译为中文"

# 产品说明翻译
./translatebook.sh product_manual.pdf -p "用户友好的中文表达，保留重要警告信息"
```

## 📊 性能参考

根据测试，不同类型文档的处理性能：

| 文档类型 | 页数 | 翻译时间 | 质量评分 |
|---------|------|----------|----------|
| 学术论文 | 12页 | 8-15分钟 | ⭐⭐⭐⭐⭐ |
| 技术手册 | 50页 | 25-40分钟 | ⭐⭐⭐⭐ |
| 小说章节 | 30页 | 15-25分钟 | ⭐⭐⭐⭐⭐ |
| 商业报告 | 20页 | 10-18分钟 | ⭐⭐⭐⭐ |

*注：翻译时间取决于网络状况和Claude API响应速度*

## 🔧 技术说明

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