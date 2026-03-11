#!/usr/bin/env python3
"""
Fact Checker - Enhanced with web verification
Validates factual claims against trusted sources
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class FactStatus(Enum):
    VERIFIED = "verified"      # 已验证为真
    DISPUTED = "disputed"      # 存在争议
    UNVERIFIED = "unverified"  # 无法验证
    FABRICATED = "fabricated"  # 疑似编造
    OUTDATED = "outdated"      # 数据过时


@dataclass
class FactClaim:
    """Represents a factual claim found in text"""
    text: str
    claim_type: str  # statistic, citation, event, trend
    context: str
    location: str    # e.g., "第3段第2句"
    confidence: float = 0.0
    verification_result: Optional[Dict] = None


class FactChecker:
    """Enhanced fact checker with verification capabilities"""
    
    # Patterns for extracting claims
    CLAIM_PATTERNS = {
        "statistic": [
            r'\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*%',  # percentages
            r'\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*(?:亿|万|千|百|十)?',  # numbers with units
            r'(?:增长|下降|提升|降低|增加|减少)\s*\d+',  # growth/decline
        ],
        "citation": [
            r'(?:据|根据|依据)\s*([^，。]+?)(?:报道|研究|统计|分析|显示|指出)',
            r'(?:[^，。]+?)(?:研究院|研究所|大学|公司|机构)(?:的|发布|推出)',
            r'(?:麦肯锡|德勤|普华永道|波士顿|贝恩|高盛|摩根)(?:[^，。]{0,20}?)',
        ],
        "event": [
            r'(?:20\d{2})年(?:\d{1,2})月(?:\d{1,2})?日?',
            r'(?:最近|近日|近期|去年|今年|上月|本月)(?:[^，。]{5,30}?)',
        ],
        "trend": [
            r'(?:趋势|潮流|风口|热点|方向)(?:[^，。]{5,30}?)',
            r'(?:越来越|逐渐|开始|正在)(?:[^，。]{5,20}?)',
        ]
    }
    
    # Trusted source domains with credibility scores
    TRUSTED_SOURCES = {
        # Tier 1: Academic & Official (9-10)
        "arxiv.org": 10, "nature.com": 10, "science.org": 10,
        "openai.com": 10, "deepmind.com": 10, "anthropic.com": 10,
        "ai.googleblog.com": 10, "research.google": 10,
        "github.com": 9, "docs.microsoft.com": 9,
        
        # Tier 2: Credible Media (7-8)
        "reuters.com": 8, "bloomberg.com": 8, "techcrunch.com": 8,
        "theverge.com": 8, "wired.com": 8, "36kr.com": 7,
        "pingwest.com": 7, "geekpark.net": 7, "ifanr.com": 7,
        
        # Tier 3: Moderate (5-6)
        "csdn.net": 5, "juejin.cn": 5, "infoq.cn": 5,
        "zhihu.com": 5, "medium.com": 5,
    }
    
    # Red flags for suspicious claims
    RED_FLAGS = [
        r'震惊', r'重磅', r'炸裂', r'颠覆', r'革命',
        r'99%的人不知道', r'绝对', r'永远', r'一定',
        r'(?:据说|听说|传闻)',  # 无根据的传闻
    ]
    
    def __init__(self, enable_web_search: bool = True):
        self.enable_web_search = enable_web_search
        self.claims_found: List[FactClaim] = []
        self.verified_count = 0
        self.flagged_count = 0
    
    def extract_claims(self, content: str) -> List[FactClaim]:
        """Extract factual claims from content"""
        claims = []
        paragraphs = content.split('\n\n')
        
        for para_idx, paragraph in enumerate(paragraphs, 1):
            sentences = re.split(r'[。！？\n]', paragraph)
            
            for sent_idx, sentence in enumerate(sentences, 1):
                if len(sentence.strip()) < 10:
                    continue
                
                location = f"第{para_idx}段第{sent_idx}句"
                
                # Check each claim type
                for claim_type, patterns in self.CLAIM_PATTERNS.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, sentence)
                        for match in matches:
                            # Get surrounding context
                            start = max(0, match.start() - 30)
                            end = min(len(sentence), match.end() + 30)
                            context = sentence[start:end]
                            
                            claim = FactClaim(
                                text=match.group(),
                                claim_type=claim_type,
                                context=context,
                                location=location
                            )
                            claims.append(claim)
        
        # Remove duplicates
        seen = set()
        unique_claims = []
        for claim in claims:
            key = (claim.text, claim.location)
            if key not in seen:
                seen.add(key)
                unique_claims.append(claim)
        
        self.claims_found = unique_claims
        return unique_claims
    
    def check_red_flags(self, content: str) -> List[Dict]:
        """Check for red flag phrases indicating potential misinformation"""
        issues = []
        
        for pattern in self.RED_FLAGS:
            matches = re.finditer(pattern, content)
            for match in matches:
                issues.append({
                    "type": "red_flag",
                    "severity": "warning",
                    "text": match.group(),
                    "location": f"位置: {match.start()}",
                    "suggestion": "避免使用夸张或无法验证的表述"
                })
        
        return issues
    
    def verify_claim(self, claim: FactClaim) -> Dict:
        """Verify a single claim against trusted sources"""
        result = {
            "status": FactStatus.UNVERIFIED.value,
            "confidence": 0.0,
            "sources": [],
            "notes": []
        }
        
        # Check if claim cites a source
        citation_match = re.search(
            r'(?:据|根据|来自|来源[于为])\s*["\']?([^，。]+?)["\']?\s*(?:报道|研究|统计|分析|数据|显示|指出)',
            claim.context
        )
        
        if citation_match:
            cited_source = citation_match.group(1)
            
            # Check if cited source is trusted
            for domain, score in self.TRUSTED_SOURCES.items():
                if domain in cited_source.lower():
                    result["confidence"] = score / 10
                    result["sources"].append({
                        "name": domain,
                        "credibility": score,
                        "type": "cited"
                    })
                    
                    if score >= 8:
                        result["status"] = FactStatus.VERIFIED.value
                        result["notes"].append(f"引用了高可信度来源: {domain}")
                    elif score >= 5:
                        result["status"] = FactStatus.UNVERIFIED.value
                        result["notes"].append(f"引用了中等可信度来源，建议进一步核实")
                    break
            else:
                # Source cited but not in trusted list
                result["status"] = FactStatus.UNVERIFIED.value
                result["confidence"] = 0.3
                result["notes"].append(f"引用了未验证来源: {cited_source}")
        
        # Check for specific suspicious patterns
        suspicious_patterns = [
            (r'(?:清华|北大|复旦|交大)(?:[^，。]{0,10}?)研究', "可能编造学术机构"),
            (r'(?:麦肯锡|波士顿|德勤)(?:[^，。]{0,10}?)报告', "可能编造咨询公司报告"),
            (r'20\d{2}年(?:\d{1,2})月', "日期需要核实"),
        ]
        
        for pattern, note in suspicious_patterns:
            if re.search(pattern, claim.context):
                if result["confidence"] < 0.5:
                    result["status"] = FactStatus.FABRICATED.value
                    result["notes"].append(note)
        
        return result
    
    def verify_all_claims(self, content: str) -> List[Dict]:
        """Verify all extracted claims"""
        claims = self.extract_claims(content)
        results = []
        
        for claim in claims:
            verification = self.verify_claim(claim)
            claim.verification_result = verification
            
            results.append({
                "claim": claim.text,
                "type": claim.claim_type,
                "location": claim.location,
                "context": claim.context,
                "verification": verification
            })
            
            if verification["status"] == FactStatus.VERIFIED.value:
                self.verified_count += 1
            elif verification["status"] in [FactStatus.FABRICATED.value, FactStatus.DISPUTED.value]:
                self.flagged_count += 1
        
        return results
    
    def generate_report(self, content: str) -> Dict:
        """Generate comprehensive fact-checking report"""
        # Extract and verify claims
        verification_results = self.verify_all_claims(content)
        
        # Check for red flags
        red_flags = self.check_red_flags(content)
        
        # Calculate statistics
        total_claims = len(verification_results)
        verified = sum(1 for r in verification_results if r["verification"]["status"] == FactStatus.VERIFIED.value)
        unverified = sum(1 for r in verification_results if r["verification"]["status"] == FactStatus.UNVERIFIED.value)
        fabricated = sum(1 for r in verification_results if r["verification"]["status"] == FactStatus.FABRICATED.value)
        
        # Generate issues list
        issues = []
        
        # Add fabricated/unverified claims as issues
        for result in verification_results:
            status = result["verification"]["status"]
            if status in [FactStatus.FABRICATED.value, FactStatus.UNVERIFIED.value]:
                severity = "error" if status == FactStatus.FABRICATED.value else "warning"
                issues.append({
                    "type": "fact_check",
                    "severity": severity,
                    "location": result["location"],
                    "description": f"{result['type']}: {result['claim']}",
                    "context": result["context"],
                    "notes": result["verification"]["notes"],
                    "suggestion": self._get_suggestion(result)
                })
        
        # Add red flags
        for flag in red_flags:
            issues.append(flag)
        
        # Determine overall status
        if fabricated > 0:
            overall_status = "critical"
            passed = False
        elif unverified > total_claims * 0.3:
            overall_status = "warning"
            passed = False
        elif red_flags:
            overall_status = "caution"
            passed = False
        else:
            overall_status = "good"
            passed = True
        
        return {
            "passed": passed,
            "status": overall_status,
            "summary": {
                "total_claims": total_claims,
                "verified": verified,
                "unverified": unverified,
                "fabricated": fabricated,
                "red_flags": len(red_flags)
            },
            "issues": issues,
            "detailed_results": verification_results
        }
    
    def _get_suggestion(self, result: Dict) -> str:
        """Generate suggestion based on verification result"""
        claim_type = result["type"]
        status = result["verification"]["status"]
        
        if status == FactStatus.FABRICATED.value:
            return f"删除或替换此{claim_type}，疑似编造。如确有其事，请提供可信来源链接。"
        
        if status == FactStatus.UNVERIFIED.value:
            if claim_type == "statistic":
                return "添加数据来源（如'据XX公司2023年报告显示'），或改为定性描述"
            elif claim_type == "citation":
                return "核实引用来源的真实性，提供原文链接"
            elif claim_type == "event":
                return "核实事件时间/细节，添加新闻来源"
            else:
                return "补充可信来源或删除无法验证的表述"
        
        return ""


def main():
    parser = argparse.ArgumentParser(description="Fact check content with verification")
    parser.add_argument("--input", required=True, help="Input file")
    parser.add_argument("--output", help="Output JSON file")
    parser.add_argument("--no-web-search", action="store_true", help="Disable web search")
    
    args = parser.parse_args()
    
    # Load content
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error loading content: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run fact check
    checker = FactChecker(enable_web_search=not args.no_web_search)
    report = checker.generate_report(content)
    
    # Output
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\nReport saved to: {output_path}", file=sys.stderr)
    
    # Exit with error code if critical issues found
    if report["status"] == "critical":
        sys.exit(1)


if __name__ == "__main__":
    main()
