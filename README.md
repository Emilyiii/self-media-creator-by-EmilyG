# Self-Media Creator Agent

基于 OpenClaw 的全自动自媒体内容创作 Agent，实现从选题到发布的完整工作流。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## ✨ 功能特性

- **🎯 智能选题** - 基于热点趋势和用户需求自动生成选题建议
- **🔍 深度研究** - 自动搜索最新资料，验证信息时效性（技术类≤3个月）
- **✍️ AI写作** - 生成专业文章，支持多种风格（专业/轻松/科普）
- **🎭 去AI味** - 智能去除AI写作痕迹，让内容更自然、更有"人味儿"
- **🖼️ 自动配图** - 根据内容自动生成配图方案和AI绘图Prompt
- **📱 多平台排版** - 支持公众号、小红书等平台格式一键导出
- **📊 质量评估** - 内置内容质量评分体系，确保输出质量

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    Self-Media Creator                        │
├─────────────────────────────────────────────────────────────┤
│  选题 → 研究 → 写作 → 去AI味 → 质检 → 配图 → 排版 → 发布    │
└─────────────────────────────────────────────────────────────┘
```

### 核心模块

| 模块 | 功能 | 对应 Skill |
|------|------|-----------|
| content-research | 资料搜索与 freshness 验证 | content-research |
| writing | 文章撰写 | - |
| humanize | 去除AI痕迹 | humanize-writing |
| evaluator | 质量评分 | content-evaluator |
| image-gen | 配图生成 | content-image-generator |
| formatter | 平台排版 | content-formatter |

## 🚀 快速开始

### 环境要求

- Python 3.10+
- OpenClaw 2026.2.13+
- API Keys: Kimi / OpenAI / Seedream (可选)

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/self-media-creator.git
cd self-media-creator

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API Keys
```

### 配置

创建 `.env` 文件：

```env
# LLM API
KIMI_API_KEY=your_kimi_api_key
OPENAI_API_KEY=your_openai_api_key

# Image Generation (可选)
SEEDREAM_API_KEY=your_seedream_api_key

# OpenClaw
OPENCLAW_GATEWAY_URL=ws://127.0.0.1:18789
OPENCLAW_TOKEN=your_token
```

### 使用

#### 方式1：命令行

```bash
# 完整流程
python scripts/create_content.py \
  --topic "AI工具推荐" \
  --platform wechat \
  --style professional \
  --output ./output/

# 仅生成大纲
python scripts/create_content.py \
  --topic "效率提升技巧" \
  --stage outline

# 小红书风格
python scripts/create_content.py \
  --topic "职场干货" \
  --platform xiaohongshu \
  --style casual
```

#### 方式2：Python API

```python
from self_media_creator import Creator

creator = Creator(
    platform="wechat",
    style="professional"
)

result = creator.create(
    topic="国产大模型的突围之路",
    max_images=3,
    notify=True
)

print(f"文章已生成：{result['article_path']}")
print(f"配图已生成：{result['images']}")
```

#### 方式3：OpenClaw Agent

在 OpenClaw 中直接调用：

```
@self-media-creator 帮我写一篇关于AI趋势的公众号文章
```

## 📋 工作流程详解

### Phase 1: 选题 (Topic Selection)
- 输入内容方向或主题
- 输出3-5个选题选项及简要描述
- 用户选择或系统自动选择

### Phase 2: 研究 (Research)
- 生成搜索查询
- 搜索最新信息
- **验证时效性**：技术类≤3个月，数据类≤5个月
- 评分来源（可信度+时效性+相关性）
- 如>30%来源过时，重新搜索或提示用户

### Phase 3: 写作 (Writing)
- 基于研究结果撰写文章
- 整合发现并标注引用
- 检查逻辑流畅性

### Phase 4: 去AI味 (Humanize)
- 检测AI写作模式
- 替换通用开头
- 增加个人声音和情感
- 变化句式结构

### Phase 5: 质量检查 (Quality Check)
- 4维度评分（内容/结构/表达/平台适配）
- 检测问题（事实/逻辑/风格）
- 检查平台规范
- 评分≥90继续，80-89自动修复，<80返回重写

### Phase 6: 配图 (Image Generation)
- 分析内容确定配图机会
- 规划配图方案（≤5张）
- 生成AI绘图Prompt
- 自动生成并选择最佳图片

### Phase 7: 排版 (Formatting)
- 设计排版方案（风格/配色/层次）
- 插入图片到正确位置
- 应用平台特定格式
- 生成多格式输出

### Phase 8: 交付 (Delivery)
- Markdown版本（编辑用）
- HTML版本（公众号）
- 图片文件
- 飞书/邮件通知

## 🎨 平台支持

| 平台 | 状态 | 特性 |
|------|------|------|
| 公众号 (WeChat) | ✅ 已支持 | Markdown + HTML，适配编辑器 |
| 小红书 (Xiaohongshu) | ✅ 已支持 | 纯文本 + emoji，适配移动端 |
| 知乎 | 🚧 开发中 | - |
| B站专栏 | 🚧 开发中 | - |

## 📁 项目结构

```
self-media-creator/
├── README.md                 # 项目说明
├── LICENSE                   # MIT许可证
├── requirements.txt          # Python依赖
├── .env.example             # 环境变量模板
├── .gitignore               # Git忽略文件
│
├── config/                  # 配置文件
│   ├── config.yaml         # 主配置
│   └── platforms/          # 平台特定配置
│       ├── wechat.yaml
│       └── xiaohongshu.yaml
│
├── src/                     # 核心代码
│   ├── __init__.py
│   ├── topic_selector.py   # 选题模块
│   ├── researcher.py       # 研究模块
│   ├── writer.py           # 写作模块
│   ├── humanizer.py        # 去AI味模块
│   ├── evaluator.py        # 质量评估
│   ├── image_generator.py  # 配图生成
│   └── formatter.py        # 排版模块
│
├── skills/                  # OpenClaw Skills
│   ├── content-research/
│   ├── content-evaluator/
│   ├── humanize-writing/
│   ├── content-image-generator/
│   └── content-formatter/
│
├── scripts/                 # 脚本工具
│   ├── create_content.py   # 主入口
│   ├── batch_create.py     # 批量生成
│   └── workflow_runner.py  # 工作流运行器
│
├── templates/               # 模板文件
│   ├── article/            # 文章模板
│   └── image/              # 配图模板
│
├── output/                  # 输出目录
│   └── .gitkeep
│
└── docs/                    # 文档
    ├── workflow.md         # 工作流程详解
    ├── skill-integration.md # Skill集成指南
    └── troubleshooting.md  # 常见问题
```

## ⚙️ 配置说明

### 平台默认配置

**公众号 (WeChat):**
```yaml
target_length: 1500
min_score: 90
max_images: 5
freshness_rules:
  technology: 3    # 月
  data: 5
  trends: 7
```

**小红书 (Xiaohongshu):**
```yaml
target_length: 300
min_score: 85
max_images: 3
```

### 自定义配置

编辑 `config/config.yaml`：

```yaml
# 默认模型
model:
  primary: "kimi-coding/k2p5"
  fallback: "openai/gpt-4"

# 质量阈值
quality:
  min_score: 90
  auto_fix_threshold: 80

# 输出设置
output:
  format: ["markdown", "html"]
  notify: true
```

## 🤝 贡献指南

欢迎提交 Issue 和 PR！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证开源。

## 🙏 致谢

- [OpenClaw](https://github.com/openclaw/openclaw) - 强大的 Agent 框架
- [Kimi](https://kimi.moonshot.cn/) - 大语言模型支持
- 所有贡献者和用户

## 📞 联系方式

- 作者：EmilyG
- 项目主页：https://github.com/Emilyiii/self-media-creator-by-EmilyG

---

> **免责声明**：本工具生成的内容仅供参考，请遵守各平台的内容规范和相关法律法规。
