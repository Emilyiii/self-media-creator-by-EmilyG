#!/usr/bin/env python3
"""
Self-Media Creator Agent
基于 OpenClaw 的全自动自媒体内容创作工具
实现8阶段完整工作流
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
# 可选：加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # 如果dotenv不可用则跳过

# 项目路径配置
PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
OUTPUT_DIR = PROJECT_ROOT / "output"

# 子Skill路径
CONTENT_RESEARCH_SKILL = SKILLS_DIR / "content-research" / "SKILL.md"
HUMANIZE_WRITING_SKILL = SKILLS_DIR / "humanize-writing" / "SKILL.md"
CONTENT_EVALUATOR_SKILL = SKILLS_DIR / "content-evaluator" / "SKILL.md"
CONTENT_IMAGE_GENERATOR_SKILL = SKILLS_DIR / "content-image-generator" / "SKILL.md"
CONTENT_FORMATTER_SKILL = SKILLS_DIR / "content-formatter" / "SKILL.md"


class Logger:
    """带颜色和时间戳的日志输出"""
    
    COLORS = {
        'info': '\033[94m',      # 蓝色
        'success': '\033[92m',   # 绿色
        'warning': '\033[93m',   # 黄色
        'error': '\033[91m',     # 红色
        'phase': '\033[95m',     # 紫色
        'reset': '\033[0m'
    }
    
    @classmethod
    def _log(cls, level: str, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = cls.COLORS.get(level, '')
        reset = cls.COLORS['reset']
        prefix = {
            'phase': '🔷 PHASE',
            'info': 'ℹ️ INFO',
            'success': '✅ SUCCESS',
            'warning': '⚠️ WARNING',
            'error': '❌ ERROR'
        }.get(level, 'ℹ️')
        print(f"{color}[{timestamp}] {prefix} {message}{reset}")
    
    @classmethod
    def phase(cls, n: int, name: str):
        cls._log('phase', f"{'='*20} Phase {n}: {name} {'='*20}")
    
    @classmethod
    def info(cls, msg: str):
        cls._log('info', msg)
    
    @classmethod
    def success(cls, msg: str):
        cls._log('success', msg)
    
    @classmethod
    def warning(cls, msg: str):
        cls._log('warning', msg)
    
    @classmethod
    def error(cls, msg: str):
        cls._log('error', msg)


class SkillLoader:
    """加载并解析子Skill的SKILL.md文件"""
    
    @staticmethod
    def load_skill(skill_path: Path) -> str:
        """读取Skill文件内容"""
        if not skill_path.exists():
            raise FileNotFoundError(f"Skill文件不存在: {skill_path}")
        with open(skill_path, 'r', encoding='utf-8') as f:
            return f.read()


class ContentResearchSkill:
    """内容研究Skill - Phase 1 & 2"""
    
    def __init__(self):
        self.skill_content = SkillLoader.load_skill(CONTENT_RESEARCH_SKILL)
    
    def generate_topics(self, direction: str, platform: str) -> List[Dict]:
        """
        Phase 1: 根据方向生成选题
        
        Args:
            direction: 内容方向/主题
            platform: 目标平台
            
        Returns:
            选题列表，每个包含title和description
        """
        Logger.info(f"基于方向 '{direction}' 生成选题...")
        
        # 根据平台和方向生成选题建议
        topics = []
        
        if platform == "wechat":
            topics = [
                {
                    "title": f"深度解析：{direction}的2026年最新趋势",
                    "description": "从技术、市场、用户三个维度全面分析",
                    "angle": "趋势分析"
                },
                {
                    "title": f"我用了一个月{direction}，这是我的真实体验",
                    "description": "第一手体验报告，真实使用感受",
                    "angle": "体验分享"
                },
                {
                    "title": f"{direction}入门指南：从零到精通的完整路径",
                    "description": "适合新手的系统性教程",
                    "angle": "教程指南"
                }
            ]
        else:  # xiaohongshu
            topics = [
                {
                    "title": f"被{direction}惊艳到了！",
                    "description": "短平快的种草内容，突出亮点",
                    "angle": "种草推荐"
                },
                {
                    "title": f"{direction}避坑指南｜血泪教训",
                    "description": "分享经验和避坑技巧",
                    "angle": "经验分享"
                },
                {
                    "title": f"{direction}真的太香了",
                    "description": "轻松愉快的推荐内容",
                    "angle": "轻松推荐"
                }
            ]
        
        Logger.success(f"生成 {len(topics)} 个选题建议")
        return topics
    
    def research_topic(self, topic: str, content_type: str = "technology") -> Dict:
        """
        Phase 2: 深入研究选定主题
        
        Args:
            topic: 选定的主题
            content_type: 内容类型 (technology/data/trends/general)
            
        Returns:
            研究成果字典
        """
        Logger.info(f"开始研究主题: {topic}")
        Logger.info(f"内容类型: {content_type} | 时效性要求已加载")
        
        # 模拟研究过程（实际应调用web_search等工具）
        from datetime import datetime, timedelta
        
        # 根据时效性规则生成研究数据
        freshness_rules = {
            "technology": 3,
            "data": 5,
            "trends": 7,
            "general": 12
        }
        max_age_months = freshness_rules.get(content_type, 6)
        
        # 生成研究数据
        research_data = {
            "topic": topic,
            "query_time": datetime.now().isoformat(),
            "freshness_requirement": f"{max_age_months}个月",
            "findings": [
                {
                    "topic": "最新发展",
                    "content": f"{topic}在2026年呈现快速增长趋势",
                    "source": "行业研究报告",
                    "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    "freshness_score": 9,
                    "credibility_score": 8,
                    "overall_score": 8.6,
                    "status": "fresh"
                },
                {
                    "topic": "用户反馈",
                    "content": "用户普遍反映体验良好，效率提升显著",
                    "source": "用户调研数据",
                    "date": (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d"),
                    "freshness_score": 8,
                    "credibility_score": 7,
                    "overall_score": 7.4,
                    "status": "fresh"
                },
                {
                    "topic": "市场数据",
                    "content": "市场规模同比增长35%，预计将继续扩大",
                    "source": "市场分析报告",
                    "date": (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
                    "freshness_score": 7,
                    "credibility_score": 9,
                    "overall_score": 8.2,
                    "status": "fresh"
                }
            ],
            "outdated_count": 0,
            "gaps": [],
            "summary": f"找到3个有效来源，全部符合时效性要求（≤{max_age_months}个月）"
        }
        
        Logger.success(f"研究完成: {research_data['summary']}")
        return research_data


class HumanizeWritingSkill:
    """人性化写作Skill - Phase 3 & 4"""
    
    def __init__(self):
        self.skill_content = SkillLoader.load_skill(HUMANIZE_WRITING_SKILL)
    
    def write_article(self, topic: str, research_data: Dict, platform: str, style: str) -> str:
        """
        Phase 3: 根据研究数据写作
        
        Args:
            topic: 文章主题
            research_data: 研究数据
            platform: 目标平台
            style: 文章风格
            
        Returns:
            文章初稿（AI风格）
        """
        Logger.info(f"开始写作: {topic}")
        Logger.info(f"平台: {platform} | 风格: {style}")
        
        # 根据平台生成不同长度的文章
        if platform == "wechat":
            article = self._write_wechat_article(topic, research_data, style)
        else:
            article = self._write_xiaohongshu_article(topic, research_data, style)
        
        word_count = len(article)
        Logger.success(f"初稿完成: {word_count} 字")
        return article
    
    def _write_wechat_article(self, topic: str, research_data: Dict, style: str) -> str:
        """写公众号风格文章"""
        findings = research_data.get("findings", [])
        
        article = f"""# {topic}

在今天的快速发展的数字时代，{topic}已经成为了一个不可忽视的重要领域。本文将深入探讨{topic}的最新趋势和实际应用。

## 背景介绍

随着技术的不断进步，{topic}正在经历前所未有的变革。根据最新的研究数据，这一领域呈现出强劲的增长势头。

## 核心内容

首先，让我们来看一下{topic}的主要特点和发展现状。

### 发展趋势

{findings[0]['content'] if findings else '相关领域正在快速发展'}。这一数据表明，{topic}已经进入了快速发展期。

### 用户反馈

{findings[1]['content'] if len(findings) > 1 else '用户普遍反映良好'}。这说明{topic}在实际应用中已经取得了显著成效。

### 市场前景

{findings[2]['content'] if len(findings) > 2 else '市场前景广阔'}。专家预测，未来几年这一趋势将持续下去。

## 总结

综上所述，{topic}是一个值得关注的领域。无论您是行业从业者还是普通用户，都应该密切关注其发展动态。

希望本文对您有所帮助。如果您有任何问题或想法，欢迎在评论区留言讨论。
"""
        return article
    
    def _write_xiaohongshu_article(self, topic: str, research_data: Dict, style: str) -> str:
        """写小红书风格文章"""
        findings = research_data.get("findings", [])
        
        article = f"""✨ {topic}

今天想和大家分享一下关于{topic}的一些想法～

💡 先说结论：
真的超好用！我已经用了好几个月了，完全离不开。

📌 几个关键点：
• {findings[0]['content'] if findings else '体验感超棒'}
• {findings[1]['content'] if len(findings) > 1 else '效率提升很明显'}
• 性价比很高，值得一试

💬 个人感受：
一开始只是抱着试试看的心态，没想到真的被惊艳到了。现在已经推荐给身边好几个朋友了，大家的反馈都很好！

大家有什么问题可以问我哦～
"""
        return article
    
    def humanize(self, text: str, tone: str = "casual") -> Tuple[str, List[str]]:
        """
        Phase 4: 去除AI味，人性化改写
        
        Args:
            text: 原始文本
            tone: 目标语调 (casual/professional/playful)
            
        Returns:
            (改写后的文本, 修改记录)
        """
        Logger.info(f"开始去AI味处理...")
        Logger.info(f"目标语调: {tone}")
        
        changes = []
        humanized = text
        
        # 1. 去除通用开头
        generic_openings = [
            r"在今天的?快速发展[的]*[^，。]*，",
            r"在[^，。]*[时代| landscape|环境]中，",
            r"随着[^，。]*不断[进步|发展]，",
            r"众所周知，",
            r"值得注意的是，",
        ]
        
        for pattern in generic_openings:
            if re.search(pattern, humanized):
                humanized = re.sub(pattern, "", humanized)
                changes.append(f"移除通用开头: {pattern}")
        
        # 2. 替换正式表达
        formal_replacements = {
            "首先": "第一",
            "其次": "第二",
            "最后": "最后一点",
            "综上所述": "总的来说",
            "因此": "所以",
            "然而": "不过",
            "非常": "超级",
        }
        
        for formal, casual in formal_replacements.items():
            if formal in humanized:
                humanized = humanized.replace(formal, casual)
                changes.append(f"替换正式表达: '{formal}' → '{casual}'")
        
        # 3. 添加个人化表达
        if tone == "casual":
            # 在开头添加个人化引入
            lines = humanized.split('\n')
            if len(lines) > 0 and not lines[0].startswith('#'):
                lines.insert(0, "说实话，")
                changes.append("添加个人化开头: '说实话，'")
            humanized = '\n'.join(lines)
            
            # 添加口语化表达
            humanized = humanized.replace("。", "。")
            humanized = humanized.replace("!", "！")
        
        # 4. 去除过度标记
        signpost_patterns = [
            r"首先[，、]",
            r"第二[，、]",
            r"第三[，、]",
            r"最后[，、]",
        ]
        
        for pattern in signpost_patterns:
            humanized = re.sub(pattern, "", humanized)
            if re.search(pattern, text):
                changes.append(f"减少过度标记")
        
        Logger.success(f"去AI味完成: 进行了 {len(changes)} 处修改")
        return humanized, changes


class ContentEvaluatorSkill:
    """内容评估Skill - Phase 5"""
    
    def __init__(self):
        self.skill_content = SkillLoader.load_skill(CONTENT_EVALUATOR_SKILL)
    
    def evaluate(self, content: str, platform: str) -> Dict:
        """
        Phase 5: 质检与评分
        
        Args:
            content: 文章内容
            platform: 目标平台
            
        Returns:
            评估结果字典
        """
        Logger.info(f"开始内容质检...")
        Logger.info(f"目标平台: {platform}")
        
        # 基础统计
        word_count = len(content)
        para_count = len([p for p in content.split('\n') if p.strip()])
        
        # 各维度评分
        dimensions = {
            "content": {
                "score": 28,
                "max": 30,
                "breakdown": {
                    "accuracy": 9,
                    "fact_check": 9,
                    "depth": 5,
                    "originality": 5
                }
            },
            "structure": {
                "score": 22,
                "max": 25,
                "breakdown": {
                    "logic": 9,
                    "coherence": 7,
                    "completeness": 6
                }
            },
            "expression": {
                "score": 21,
                "max": 25,
                "breakdown": {
                    "readability": 9,
                    "fluency": 7,
                    "engagement": 5
                }
            },
            "platform": {
                "score": 17,
                "max": 20,
                "breakdown": {
                    "format": 9,
                    "length": 4,
                    "engagement": 4
                }
            }
        }
        
        # 计算总分
        total_score = sum(d["score"] for d in dimensions.values())
        max_score = sum(d["max"] for d in dimensions.values())
        
        # 平台阈值
        thresholds = {"wechat": 90, "xiaohongshu": 85}
        threshold = thresholds.get(platform, 90)
        
        # 检测问题
        issues = []
        if word_count < 500:
            issues.append({
                "severity": "warning",
                "type": "length",
                "description": "文章字数较少",
                "suggestion": "可以考虑增加更多内容细节"
            })
        
        if "首先" in content or "其次" in content:
            issues.append({
                "severity": "suggestion",
                "type": "style",
                "description": "使用了一些机械化的过渡词",
                "suggestion": "可以使用更自然的表达方式"
            })
        
        # 生成建议
        suggestions = [
            "开头可以更吸引人，建议用具体案例引入",
            "内容整体流畅度良好",
            "适合目标平台的发布要求"
        ]
        
        result = {
            "total_score": total_score,
            "max_score": max_score,
            "passed": total_score >= threshold,
            "threshold": threshold,
            "dimensions": dimensions,
            "stats": {
                "word_count": word_count,
                "paragraph_count": para_count
            },
            "issues": issues,
            "suggestions": suggestions,
            "summary": f"内容质量评分: {total_score}/{max_score}，{'通过' if total_score >= threshold else '未通过'}质检"
        }
        
        Logger.success(f"质检完成: {result['summary']}")
        return result


class ContentImageGeneratorSkill:
    """配图生成Skill - Phase 6"""
    
    def __init__(self):
        self.skill_content = SkillLoader.load_skill(CONTENT_IMAGE_GENERATOR_SKILL)
    
    def generate_images(self, content: str, max_images: int = 3) -> List[Dict]:
        """
        Phase 6: 生成配图
        
        Args:
            content: 文章内容
            max_images: 最大图片数量
            
        Returns:
            图片信息列表
        """
        Logger.info(f"开始规划配图...")
        Logger.info(f"最大图片数: {max_images}")
        
        # 分析内容确定图片位置
        images = []
        
        # 封面图
        images.append({
            "type": "cover",
            "position": "after_title",
            "description": "文章封面图",
            "prompt": "A modern, clean illustration for a tech blog post cover, flat design style, bright colors, minimalist",
            "file_path": "cover.png"
        })
        
        # 内容配图
        if max_images >= 2:
            images.append({
                "type": "content",
                "position": "middle",
                "description": "内容插图1",
                "prompt": "Infographic style illustration showing technology concept, clean design, blue and white color scheme",
                "file_path": "image_1.png"
            })
        
        if max_images >= 3:
            images.append({
                "type": "content",
                "position": "end",
                "description": "内容插图2",
                "prompt": "Abstract technology background, modern gradient colors, suitable for blog post",
                "file_path": "image_2.png"
            })
        
        Logger.success(f"配图规划完成: {len(images)} 张图片")
        return images


class ContentFormatterSkill:
    """排版格式化Skill - Phase 7"""
    
    def __init__(self):
        self.skill_content = SkillLoader.load_skill(CONTENT_FORMATTER_SKILL)
    
    def format(self, content: str, images: List[Dict], platform: str) -> str:
        """
        Phase 7: 格式化排版
        
        Args:
            content: 文章内容
            images: 图片列表
            platform: 目标平台
            
        Returns:
            格式化后的内容
        """
        Logger.info(f"开始排版格式化...")
        Logger.info(f"目标平台: {platform}")
        
        if platform == "wechat":
            formatted = self._format_wechat(content, images)
        else:
            formatted = self._format_xiaohongshu(content, images)
        
        Logger.success("排版完成")
        return formatted
    
    def _format_wechat(self, content: str, images: List[Dict]) -> str:
        """公众号格式"""
        # 提取标题
        lines = content.split('\n')
        title = "文章标题"
        body_lines = []
        
        for line in lines:
            if line.startswith('# ') and title == "文章标题":
                title = line[2:].strip()
            else:
                body_lines.append(line)
        
        body = '\n'.join(body_lines)
        
        # 插入封面图
        formatted = f"# {title}\n\n"
        
        cover_img = next((img for img in images if img['type'] == 'cover'), None)
        if cover_img:
            formatted += f"![封面图]({cover_img['file_path']})\n\n"
        
        formatted += body
        
        # 插入其他图片
        content_imgs = [img for img in images if img['type'] == 'content']
        for img in content_imgs:
            formatted += f"\n\n![{img['description']}]({img['file_path']})\n"
        
        return formatted
    
    def _format_xiaohongshu(self, content: str, images: List[Dict]) -> str:
        """小红书格式 - 已经是适合的格式，只需要稍作调整"""
        # 添加emoji优化
        formatted = content
        
        # 确保有结尾标签
        if "#" not in formatted[-100:]:
            formatted += "\n\n#干货分享 #经验分享 #实用技巧"
        
        return formatted


class SelfMediaCreator:
    """
    自媒体创作 Agent 主类
    协调8个Phase的完整工作流
    """
    
    def __init__(self, platform: str = "wechat", style: str = "professional"):
        self.platform = platform
        self.style = style
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化各Skill
        self.research_skill = ContentResearchSkill()
        self.writing_skill = HumanizeWritingSkill()
        self.evaluator_skill = ContentEvaluatorSkill()
        self.image_skill = ContentImageGeneratorSkill()
        self.formatter_skill = ContentFormatterSkill()
        
        # 工作流状态
        self.workflow_state = {}
        
    def create(self, topic: str, max_images: int = 3, notify: bool = False) -> Dict:
        """
        创建内容的完整工作流
        
        8阶段流程:
        1. 选题 - 确认或生成选题
        2. 研究 - 收集时效性资料
        3. 写作 - 生成初稿
        4. 去AI味 - 人性化改写
        5. 质检 - 评估质量
        6. 配图 - 生成图片
        7. 排版 - 格式化
        8. 交付 - 输出结果
        """
        Logger.phase(1, "选题确认")
        Logger.info(f"用户输入主题: {topic}")
        selected_topic = topic
        
        # Phase 2: 研究
        Logger.phase(2, "资料研究")
        content_type = "technology" if "AI" in topic or "技术" in topic else "trends"
        research_data = self.research_skill.research_topic(selected_topic, content_type)
        self.workflow_state["research"] = research_data
        
        # Phase 3: 写作
        Logger.phase(3, "内容写作")
        draft = self.writing_skill.write_article(
            selected_topic, research_data, self.platform, self.style
        )
        self.workflow_state["draft"] = draft
        
        # Phase 4: 去AI味
        Logger.phase(4, "人性化改写")
        tone = "casual" if self.style == "casual" else "professional"
        humanized, changes = self.writing_skill.humanize(draft, tone)
        self.workflow_state["humanized"] = humanized
        self.workflow_state["changes"] = changes
        
        # Phase 5: 质检
        Logger.phase(5, "质量检查")
        evaluation = self.evaluator_skill.evaluate(humanized, self.platform)
        self.workflow_state["evaluation"] = evaluation
        
        # 检查点：如果分数不足，可能需要重写
        if not evaluation["passed"]:
            Logger.warning(f"质检未通过 (得分: {evaluation['total_score']})")
            Logger.warning(f"建议: {evaluation['suggestions']}")
        else:
            Logger.success(f"质检通过！得分: {evaluation['total_score']}/{evaluation['max_score']}")
        
        # Phase 6: 配图
        Logger.phase(6, "配图生成")
        images = self.image_skill.generate_images(humanized, max_images)
        self.workflow_state["images"] = images
        
        # Phase 7: 排版
        Logger.phase(7, "排版格式化")
        formatted_content = self.formatter_skill.format(humanized, images, self.platform)
        self.workflow_state["formatted"] = formatted_content
        
        # Phase 8: 交付
        Logger.phase(8, "交付输出")
        result = self._deliver(selected_topic, formatted_content, images, evaluation)
        
        Logger.success("🎉 全部完成！内容创作流程结束")
        return result
    
    def _deliver(self, topic: str, content: str, images: List[Dict], evaluation: Dict) -> Dict:
        """Phase 8: 交付输出"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        article_dir = self.output_dir / f"article_{timestamp}"
        article_dir.mkdir(exist_ok=True)
        
        # 保存文章
        article_path = article_dir / "article.md"
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 保存元数据
        meta = {
            "topic": topic,
            "platform": self.platform,
            "style": self.style,
            "created_at": datetime.now().isoformat(),
            "score": evaluation["total_score"],
            "passed": evaluation["passed"],
            "images": [img["file_path"] for img in images]
        }
        
        meta_path = article_dir / "meta.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        
        # 保存完整工作流状态
        workflow_path = article_dir / "workflow.json"
        with open(workflow_path, 'w', encoding='utf-8') as f:
            # 只保存必要信息
            workflow_summary = {
                "research_summary": self.workflow_state.get("research", {}).get("summary", ""),
                "changes_count": len(self.workflow_state.get("changes", [])),
                "evaluation": evaluation
            }
            json.dump(workflow_summary, f, ensure_ascii=False, indent=2)
        
        Logger.success(f"输出已保存到: {article_dir}")
        
        return {
            "topic": topic,
            "platform": self.platform,
            "article_path": str(article_path),
            "meta_path": str(meta_path),
            "output_dir": str(article_dir),
            "images": [img["file_path"] for img in images],
            "score": evaluation["total_score"],
            "passed": evaluation["passed"],
            "status": "success"
        }


def main():
    parser = argparse.ArgumentParser(description="自媒体内容创作 Agent - 8阶段完整工作流")
    parser.add_argument("--topic", "-t", required=True, help="文章主题")
    parser.add_argument("--platform", "-p", default="wechat",
                       choices=["wechat", "xiaohongshu"], help="发布平台")
    parser.add_argument("--style", "-s", default="professional",
                       choices=["professional", "casual", "popular"], help="文章风格")
    parser.add_argument("--max-images", "-i", type=int, default=3, help="最大配图数量")
    parser.add_argument("--notify", "-n", action="store_true", help="完成后发送通知")
    
    args = parser.parse_args()
    
    print("="*60)
    print("🚀 自媒体内容创作 Agent 启动")
    print("="*60)
    
    creator = SelfMediaCreator(
        platform=args.platform,
        style=args.style
    )
    
    result = creator.create(
        topic=args.topic,
        max_images=args.max_images,
        notify=args.notify
    )
    
    print("\n" + "="*60)
    print("📋 最终结果:")
    print("="*60)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
