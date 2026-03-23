# Self-Media Creator 重构方案（第一版）

## 重构目标
把项目从“Python 编排型自动化项目”重构为“Skill 驱动的人机协作式内容工作流”。

## 核心原则
1. Agent 负责协作、判断、推进，不再由 Python 脚本模拟思考。
2. Skill 负责沉淀方法论、验收标准、步骤协议。
3. Python 只保留真正工具属性的能力（如导出、格式转换）。
4. 用户在关键节点参与：选题、结构确认、终稿确认。

## 第一轮已处理
- 已移出 active scripts 的遗留编排脚本至 `archive/legacy-scripts/`
- 已清空 `output/` 下生成产物，仅保留 `.gitkeep`
- 已收敛 `.gitignore`，避免中间产物继续进仓库

## 推荐结构
- `skills/self-media-workflow/`：主 Skill，定义完整协作流程
- `skills/topic-planning/`：选题与角度拆解
- `skills/content-research/`：资料研究与事实提炼
- `skills/draft-writing/`：初稿生成
- `skills/final-polish/`：终稿润色与去模板腔
- `skills/content-image-generator/`：配图规划
- `skills/content-formatter/`：排版与交付
- `archive/legacy-scripts/`：历史脚本，仅保留作参考，不参与现行流程

## 三阶段迁移
### 阶段 1：减法
- 删除/归档伪编排脚本
- 停止 Python 调 LLM 的绕路设计
- 收敛输出目录与仓库管理

### 阶段 2：搭主 Skill
- 新建 `self-media-workflow` 主 Skill
- 定义步骤、输入输出、确认点、回退策略
- 明确每个子 Skill 的职责边界

### 阶段 3：最小闭环
- 方向输入 → 选题 → 用户选择 → 初稿 → 用户反馈 → 终稿润色 → 排版交付
- 先不追求全自动，先追求协作顺畅、结果稳定


## 新增进展（2026-03-23）
- 已新增 `topic-planning`、`draft-writing`、`final-polish` 技能骨架
- 已完成第一轮 Skill 审计：`docs/skill-audit-20260323.md`
- 已将 `humanize-writing` 迁移为 `final-polish`
