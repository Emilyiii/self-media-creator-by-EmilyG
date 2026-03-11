#!/usr/bin/env python3
"""
Content Evaluator - Main evaluation script
Multi-dimensional content quality assessment with fact checking
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Import fact checker
sys.path.insert(0, str(Path(__file__).parent))
from fact_checker import FactChecker, FactStatus


# Default scoring configuration
DEFAULT_CONFIG = {
    "pass_threshold": 90,
    "weights": {
        "content": 30,
        "structure": 25,
        "expression": 25,
        "platform": 20
    },
    "platform_thresholds": {
        "wechat": 90,
        "xiaohongshu": 85
    },
    "fact_check": {
        "enabled": True,
        "strict_mode": True,  # 严格模式：有编造内容直接不通过
        "min_verified_ratio": 0.5  # 至少50%的声明需要可验证
    }
}


class ContentEvaluator:
    def __init__(self, config: Dict = None):
        self.config = config or DEFAULT_CONFIG
    
    def analyze_basic(self, content: str) -> Dict:
        """Basic text analysis"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        sentences = re.split(r'[.!?。！？]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        word_count = len(content)
        
        return {
            "word_count": word_count,
            "paragraph_count": len(paragraphs),
            "sentence_count": len(sentences),
            "avg_sentence_length": word_count / len(sentences) if sentences else 0,
            "paragraph_lengths": [len(p) for p in paragraphs]
        }
    
    def evaluate_content(self, content: str) -> Tuple[int, List[Dict]]:
        """Evaluate content quality (30 points max)"""
        score = 30
        issues = []
        
        # === NEW: Fact Checking ===
        fact_config = self.config.get("fact_check", {"enabled": True})
        if fact_config.get("enabled", True):
            fact_checker = FactChecker()
            fact_report = fact_checker.generate_report(content)
            
            # Deduct points for fact issues
            if fact_report["status"] == "critical":
                score -= 15  # 严重问题扣15分
                issues.append({
                    "type": "fact_check",
                    "severity": "error",
                    "description": f"发现{fact_report['summary']['fabricated']}处疑似编造内容",
                    "suggestion": "删除编造内容，替换为可验证的事实"
                })
            elif fact_report["status"] == "warning":
                score -= 8
                issues.append({
                    "type": "fact_check",
                    "severity": "warning",
                    "description": f"{fact_report['summary']['unverified']}处声明无法验证",
                    "suggestion": "为数据/引用添加可信来源"
                })
            
            # Add detailed fact issues
            for fact_issue in fact_report["issues"]:
                if fact_issue.get("type") == "fact_check":
                    issues.append(fact_issue)
        
        # === Original content checks ===
        # Check for generic statements
        generic_patterns = [
            r"many people",
            r"some experts",
            r"research shows",
            r"it is important",
            r"in today's world"
        ]
        generic_count = sum(len(re.findall(p, content, re.I)) for p in generic_patterns)
        if generic_count > 3:
            score -= min(5, generic_count)
            issues.append({
                "type": "content",
                "severity": "warning",
                "description": f"发现{generic_count}处通用表述，建议添加具体案例",
                "suggestion": "用具体数据或个人经历替换通用表述"
            })
        
        # Check depth (simplified - word count proxy)
        if len(content) < 500:
            score -= 3
            issues.append({
                "type": "content",
                "severity": "suggestion",
                "description": "内容较短，分析可能不够深入",
                "suggestion": "增加案例分析或深入探讨"
            })
        
        return max(0, score), issues
    
    def evaluate_structure(self, content: str) -> Tuple[int, List[Dict]]:
        """Evaluate structure quality (25 points max)"""
        score = 25
        issues = []
        
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Check for opening
        if len(paragraphs) > 0:
            first_para = paragraphs[0]
            if len(first_para) < 50:
                score -= 2
                issues.append({
                    "type": "structure",
                    "severity": "warning",
                    "description": "开头较短，可能缺乏吸引力",
                    "suggestion": "用钩子或问题引入主题"
                })
        
        # Check for conclusion
        if len(paragraphs) > 1:
            last_para = paragraphs[-1]
            conclusion_markers = ['总结', '结论', '总之', '最后', '综上']
            if not any(m in last_para for m in conclusion_markers) and len(last_para) < 100:
                score -= 2
                issues.append({
                    "type": "structure",
                    "severity": "suggestion",
                    "description": "结尾较短，缺少总结",
                    "suggestion": "添加总结段落或行动号召"
                })
        
        # Check transitions
        transition_words = ['首先', '其次', '然后', '此外', '另外', '但是', '然而', '因此', '所以']
        transition_count = sum(content.count(w) for w in transition_words)
        if transition_count < 2 and len(paragraphs) > 3:
            score -= 3
            issues.append({
                "type": "structure",
                "severity": "warning",
                "description": "段落间缺少过渡",
                "suggestion": "添加过渡词或句子增强连贯性"
            })
        
        return max(0, score), issues
    
    def evaluate_expression(self, content: str) -> Tuple[int, List[Dict]]:
        """Evaluate expression quality (25 points max)"""
        score = 25
        issues = []
        
        sentences = re.split(r'[.!?。！？]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Check sentence length
        long_sentences = [s for s in sentences if len(s) > 100]
        if len(long_sentences) > len(sentences) * 0.3:
            score -= 3
            issues.append({
                "type": "expression",
                "severity": "suggestion",
                "description": f"{len(long_sentences)}个长句，影响可读性",
                "suggestion": "拆分长句，每句控制在50字以内"
            })
        
        # Check for hook
        first_para = content[:200]
        hook_patterns = [r'[?？]', r'[!！]', r'你', r'为什么', r'如何', r'知道吗']
        if not any(re.search(p, first_para) for p in hook_patterns):
            score -= 3
            issues.append({
                "type": "expression",
                "severity": "warning",
                "description": "开头缺少吸引力",
                "suggestion": "用问题、数据或故事开头"
            })
        
        # Check for passive voice (simplified)
        passive_patterns = [r'被', r'由.*完成', r'得以']
        passive_count = sum(len(re.findall(p, content)) for p in passive_patterns)
        if passive_count > 5:
            score -= 2
            issues.append({
                "type": "expression",
                "severity": "suggestion",
                "description": "被动语态较多",
                "suggestion": "改用主动语态增强力量感"
            })
        
        return max(0, score), issues
    
    def evaluate_platform(self, content: str, platform: str) -> Tuple[int, List[Dict]]:
        """Evaluate platform fit (20 points max)"""
        score = 20
        issues = []
        
        word_count = len(content)
        
        if platform == "wechat":
            # 公众号标准
            if word_count < 800:
                score -= 3
                issues.append({
                    "type": "platform",
                    "severity": "suggestion",
                    "description": f"字数较少({word_count}字)，公众号建议800字以上",
                    "suggestion": "增加内容深度或案例"
                })
            elif word_count > 3000:
                score -= 2
                issues.append({
                    "type": "platform",
                    "severity": "suggestion",
                    "description": f"字数较多({word_count}字)，可能影响完读率",
                    "suggestion": "精简内容或分篇发布"
                })
            
            # Check headers
            headers = re.findall(r'^#{1,3}\s+', content, re.M)
            if len(headers) < 2 and word_count > 1000:
                score -= 2
                issues.append({
                    "type": "platform",
                    "severity": "suggestion",
                    "description": "缺少小标题",
                    "suggestion": "添加##小标题提升可读性"
                })
        
        elif platform == "xiaohongshu":
            # 小红书标准
            if word_count > 500:
                score -= 3
                issues.append({
                    "type": "platform",
                    "severity": "warning",
                    "description": f"字数过多({word_count}字)，小红书建议200-500字",
                    "suggestion": "精简要点，用 bullet points"
                })
            
            # Check emoji usage
            emojis = re.findall(r'[\u2600-\u26FF\u2700-\u27BF\U0001F300-\U0001F9FF]', content)
            if len(emojis) < 3:
                score -= 2
                issues.append({
                    "type": "platform",
                    "severity": "suggestion",
                    "description": "emoji较少",
                    "suggestion": "添加3-5个相关emoji增强视觉效果"
                })
        
        return max(0, score), issues
    
    def evaluate(self, content: str, platform: str = "wechat") -> Dict:
        """Full evaluation"""
        basic = self.analyze_basic(content)
        
        content_score, content_issues = self.evaluate_content(content)
        structure_score, structure_issues = self.evaluate_structure(content)
        expression_score, expression_issues = self.evaluate_expression(content)
        platform_score, platform_issues = self.evaluate_platform(content, platform)
        
        # Calculate total
        weights = self.config["weights"]
        total_score = (
            content_score * weights["content"] / 30 +
            structure_score * weights["structure"] / 25 +
            expression_score * weights["expression"] / 25 +
            platform_score * weights["platform"] / 20
        )
        
        # Determine pass/fail
        threshold = self.config["platform_thresholds"].get(platform, 90)
        passed = total_score >= threshold
        
        # Combine all issues
        all_issues = content_issues + structure_issues + expression_issues + platform_issues
        
        # Sort by severity
        severity_order = {"error": 0, "warning": 1, "suggestion": 2}
        all_issues.sort(key=lambda x: severity_order.get(x["severity"], 3))
        
        return {
            "total_score": round(total_score, 1),
            "passed": passed,
            "threshold": threshold,
            "basic_stats": basic,
            "dimensions": {
                "content": {
                    "score": content_score,
                    "max": 30,
                    "issues": len(content_issues)
                },
                "structure": {
                    "score": structure_score,
                    "max": 25,
                    "issues": len(structure_issues)
                },
                "expression": {
                    "score": expression_score,
                    "max": 25,
                    "issues": len(expression_issues)
                },
                "platform": {
                    "score": platform_score,
                    "max": 20,
                    "issues": len(platform_issues)
                }
            },
            "issues": all_issues[:10],  # Top 10 issues
            "summary": self._generate_summary(total_score, passed, all_issues)
        }
    
    def _generate_summary(self, score: float, passed: bool, issues: List[Dict]) -> str:
        """Generate evaluation summary"""
        if passed:
            summary = f"内容质量良好（{score:.0f}分），符合发布标准。"
        else:
            summary = f"内容需要改进（{score:.0f}分），建议处理以下问题后重新评估。"
        
        if issues:
            error_count = sum(1 for i in issues if i["severity"] == "error")
            warning_count = sum(1 for i in issues if i["severity"] == "warning")
            
            if error_count > 0:
                summary += f"发现{error_count}个严重问题，{warning_count}个警告。"
            elif warning_count > 0:
                summary += f"发现{warning_count}个改进建议。"
        
        return summary


def main():
    parser = argparse.ArgumentParser(description="Evaluate content quality")
    parser.add_argument("--input", required=True, help="Input file with content")
    parser.add_argument("--platform", default="wechat", choices=["wechat", "xiaohongshu"])
    parser.add_argument("--config", help="Config JSON file")
    parser.add_argument("--output", help="Output JSON file")
    
    args = parser.parse_args()
    
    # Load content
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error loading content: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Load config
    config = None
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config: {e}", file=sys.stderr)
    
    # Evaluate
    evaluator = ContentEvaluator(config)
    result = evaluator.evaluate(content, args.platform)
    
    # Output
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
