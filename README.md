# MetaNovel-Engine

![Version](https://img.shields.io/badge/version-v0.0.22-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

> **AI辅助小说创作引擎** - 结构化、分阶段的长篇小说创作工具

## 💡 为什么选择 MetaNovel-Engine？

- **🎯 省钱高效**：结构化创作流程，避免重复生成，大幅节省AI费用
- **📚 多项目管理**：同时创作多部小说，数据完全独立，不会混乱
- **🎨 个性化配置**：每个项目独立的AI提示词，科幻、言情、悬疑各有专属风格
- **🔄 渐进式创作**：从一句话想法到完整小说，7步骤层层递进，思路清晰
- **🌍 完整世界观**：角色、场景、道具统一管理，保持故事连贯性
- **🤖 智能体验**：AI自动分析主题推荐作品类型，多版本生成供用户选择

## 🚀 5分钟快速开始

### 1. 安装
```bash
git clone https://github.com/hahagood/MetaNovel-Engine.git
cd MetaNovel-Engine
pip install -r requirements.txt
```

### 2. 配置API（首次使用）
将 `.env.example` 复制为 `.env`，填入你的OpenRouter API密钥：
```bash
cp .env.example .env
# 编辑 .env 文件，填入：OPENROUTER_API_KEY=your_api_key_here
```

### 3. 运行程序
```bash
python meta_novel_cli.py
```

### 4. 开始创作
运行程序后，选择"创建新项目"，按照7步流程开始你的小说创作之旅！

## 🧭 运行环境

- Python 3.8 及以上（推荐 3.11+ 获得更好的 httpx/asyncio 性能）
- 建议使用虚拟环境：`python -m venv venv && source venv/bin/activate` 或 `. bin/activate`
- 依赖通过 `pip install -r requirements.txt` 安装，涵盖 `openai`、`httpx`、`rich` 等组件
- 与 OpenRouter API 通信，确保网络和代理设置可访问 `https://openrouter.ai`
- 默认使用控制台 UI，不需要额外的浏览器或图形界面

## 📝 创作流程：7步工作流

| 步骤 | 功能 | 用途 |
|------|------|------|
| 1️⃣ | **设置主题** | 确立一句话核心创意 |
| 2️⃣ | **智能扩展主题** | AI分析推荐作品类型，生成多版本供选择 |
| 3️⃣ | **世界设定** | 创建角色、场景、道具 |
| 4️⃣ | **故事大纲** | 撰写500-800字的故事框架 |
| 5️⃣ | **分章细纲** | 分解为5-10个章节大纲 |
| 6️⃣ | **章节概要** | 每章300-500字详细概要 |
| 7️⃣ | **生成正文** | 生成2000-4000字完整章节 |

*每个步骤都可以查看、编辑和重新生成，确保创作质量*

## ⚙️ 核心功能

### 📁 项目管理
- 无限创建小说项目，数据完全隔离
- 快速切换不同项目，继续创作
- 自动备份，防止数据丢失

### 🎨 个性化AI
- 每个项目独立的提示词配置
- 针对不同题材调整AI创作风格
- 支持自定义AI模型和参数

### 🤖 智能创作体验
- **智能主题分析**：AI自动分析一句话主题，推荐最适合的作品类型（科幻、奇幻、悬疑、情感等）
- **多版本生成**：基于用户创作意图，一次生成3个不同风格的故事构想供选择
- **强制参与机制**：要求用户表达创作意图，确保AI生成内容符合用户期望
- **模块化架构**：采用独立服务模块设计，便于功能扩展和维护

### 📤 导出功能
- **多样化导出选项**：支持单章节、章节范围（如1-3章）、整本小说导出
- **规范元数据格式**：自动生成包含作品名、导出时间、章节信息、字数统计的标准头部
- **智能范围选择**：支持多种范围格式输入（1-3、1,3、1 3等）
- **精确字数统计**：导出前自动清理章节尾部的 AI 元数据（如 patch_log），再重新统计字数
- **干净的正文输出**：正文仅保留创作内容，移除 LLM 生成流程附带的调试或分析信息
- **用户友好界面**：统一的左对齐提示信息，提供清晰的操作指引

### 🔧 系统设置
- AI模型切换
- 网络代理配置
- 智能重试设置

## 🏗️ 项目结构总览

- `meta_novel_cli.py`：命令行入口，负责顶层菜单与用户导航
- `workflow_ui.py`：七步创作流程的业务逻辑与 UI 交互
- `project_manager.py` / `project_data_manager.py`：多项目管理、配置持久化与数据管理器刷新
- `data_manager.py`：封装 JSON 读写与缓存逻辑的统一数据访问层
- `llm_service.py`：与 OpenRouter API 的交互、重试策略与 JSON 解析
- `entity_manager.py`、`theme_paragraph_service.py`：实体管理及主题段落增强工作流

## 📂 配置与数据存储

- `.env` 存放 API Key、代理、默认模型等环境变量，可通过设置界面写回
- 全局配置位于系统应用数据目录（如 `~/Library/Application Support/MetaNovel`），包含 `config.json` 与项目索引
- 每个项目的数据都保存在 `<项目目录>/meta/` 下的 JSON 文件，并在 `meta_backup/` 中维护备份
- `prompts.json` 支持按项目覆盖；切换项目时会自动刷新 LLM 提示词缓存
- 导出内容默认写入 `exports/`，可在系统设置里改为自定义目录

## 🛡️ 稳健性与容错设计

- API 请求统一走 `retry_utils`，提供指数退避、抖动和批量重试
- LLM 返回的 JSON 采用多层兜底解析（代码块提取、引号修复、`ast.literal_eval` 等）
- Canon Bible 生成失败时会回退到默认骨架，确保流程不中断
- 项目配置在读写前后自动补全必需字段，避免手工编辑造成崩溃
- 实体生成会优先解析用户输入的名称，确保 LLM 输出与存储保持一致

## 🧪 测试与开发

- 激活虚拟环境：`. bin/activate`
- 运行单个测试：`python -m pytest tests/test_entity_manager.py`
- 全量测试：`python -m pytest tests`
- 开发过程中建议随手执行 `git status`，避免把临时导出或备份文件提交进仓库
- 调试 API 请求时可在 `.env` 中调整模型或代理设置

## 🆘 常见问题

**Q: 需要什么API密钥？如何获取？**

A: 需要OpenRouter的API密钥。访问 [OpenRouter官网](https://openrouter.ai) 注册账号并创建API密钥，然后填入`.env`文件中的`OPENROUTER_API_KEY=`后面。OpenRouter支持多种AI模型，价格相对便宜。

**Q: 如何切换AI模型？**

A: 在主菜单选择"系统设置"→"AI模型管理"→"切换AI模型"，可选择预设模型或添加自定义模型。默认使用Qwen-2.5-72B，性价比较高。

**Q: 网络连接不稳定，如何设置代理？**

A: 编辑`.env`文件，取消注释并设置`HTTP_PROXY`和`HTTPS_PROXY`行，填入您的代理地址（如`http://127.0.0.1:7890`）。

**Q: 如何自定义AI提示词？**

A: 在系统设置中选择"Prompts模板管理"，可以查看和编辑当前项目的提示词配置，针对不同题材调整AI创作风格。

**Q: 如何管理多个小说项目？**

A: 在主菜单选择"项目管理"，可以创建、切换、编辑或删除项目，每个项目数据完全独立。

**Q: 如何导出我的小说？**

A: 在“小说正文生成管理”中选择“导出小说”，支持导出单章节、章节范围或完整小说，导出文件包含标准元数据和精确字数统计。

## ⚠️ 注意事项与限制

- 长对话或大段 Canon Bible 生成仍可能触发速率限制，可在设置里调整重试参数
- JSON 数据直接保存在磁盘，建议定期备份项目目录或纳入版本控制
- 目前仅提供命令行 UI，若需 GUI 可基于 `export_ui.py`、`workbench_ui.py` 扩展
- 生成内容需配合人工审校与命名规范，以确保世界观的一致性
- 建议在稳定的网络环境下切换项目，等待提示词加载完成再进行下一步

## 📄 开源协议

本项目采用 MIT License 开源协议。

## 🚀 开始创作

**准备好开始你的AI辅助小说创作之旅了吗？**

1. 克隆项目：`git clone https://github.com/hahagood/MetaNovel-Engine.git`
2. 安装依赖：`pip install -r requirements.txt`
3. 配置API密钥
4. 运行：`python meta_novel_cli.py`
5. 创建你的第一个项目！

---

**让AI成为你最好的创作伙伴！** ✨

## 📜 更新日志

### v0.0.21 (2025-08-02)
- **修复**: 解决了在多项目模式下，AI生成内容时错误地加载项目根目录的`prompts.json`而不是当前小说项目下的`prompts.json`的问题。现在可以确保每个项目使用其独立的、修改后的提示词。
- **优化**: 调整了导出文件的分隔符样式和文件名格式，使其更加美观和规范。
- **测试**: 为Prompt加载逻辑添加了单元测试，提高了代码的健壮性。
