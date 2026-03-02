#!/usr/bin/env python3
"""
Content Research - Research with freshness validation
Searches for information and validates freshness
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


# Freshness rules by content type
FRESHNESS_RULES = {
    "technology": {"months": 3, "description": "技术类资料，3个月内"},
    "data": {"months": 5, "description": "数据/统计，5个月内"},
    "trends": {"months": 7, "description": "行业趋势，7个月内"},
    "general": {"months": 12, "description": "通用知识，12个月内"}
}


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse various date formats"""
    formats = [
        "%Y-%m-%d",
        "%Y-%m",
        "%Y年%m月%d日",
        "%Y年%m月",
        "%Y/%m/%d",
        "%Y/%m",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Try to extract year-month from text
    match = re.search(r'(\d{4})[年/-](\d{1,2})', date_str)
    if match:
        year, month = int(match.group(1)), int(match.group(2))
        try:
            return datetime(year, month, 1)
        except ValueError:
            pass
    
    return None


def calculate_freshness_score(pub_date: datetime, content_type: str = "general") -> Dict:
    """
    Calculate freshness score based on publication date
    
    Returns:
        Dict with score, status, and cutoff info
    """
    now = datetime.now()
    age_days = (now - pub_date).days
    age_months = age_days / 30
    
    # Get cutoff for content type
    rule = FRESHNESS_RULES.get(content_type, FRESHNESS_RULES["general"])
    cutoff_months = rule["months"]
    cutoff_date = now - timedelta(days=cutoff_months * 30)
    
    # Calculate score
    if age_months <= 1:
        score = 10
    elif age_months <= 3:
        score = 8 + (3 - age_months) / 2
    elif age_months <= 6:
        score = 6 + (6 - age_months) / 3
    elif age_months <= 12:
        score = 4 + (12 - age_months) / 6
    else:
        score = max(0, 3 - (age_months - 12) / 6)
    
    # Determine status
    if age_months <= cutoff_months:
        status = "fresh"
    elif age_months <= cutoff_months * 1.5:
        status = "aging"
    else:
        status = "outdated"
    
    return {
        "score": round(score, 1),
        "status": status,
        "age_months": round(age_months, 1),
        "age_days": age_days,
        "cutoff_months": cutoff_months,
        "cutoff_date": cutoff_date.strftime("%Y-%m-%d"),
        "description": rule["description"]
    }


def evaluate_source_credibility(source: str, source_type: str = "web") -> int:
    """
    Evaluate source credibility (0-10)
    
    This is a simplified version - real implementation would use
    domain reputation, author authority, etc.
    """
    # High credibility sources
    high_cred = [
        "github.com", "arxiv.org", "ieee.org", "acm.org",
        "nature.com", "science.org", "reuters.com", "bloomberg.com",
        "techcrunch.com", "theverge.com", "wired.com"
    ]
    
    # Medium credibility
    med_cred = [
        "medium.com", "dev.to", "towardsdatascience.com",
        "zhihu.com", "juejin.cn", "csdn.net"
    ]
    
    source_lower = source.lower()
    
    for domain in high_cred:
        if domain in source_lower:
            return 9
    
    for domain in med_cred:
        if domain in source_lower:
            return 7
    
    # Default for unknown sources
    return 5


def research_topic(
    query: str,
    content_type: str = "general",
    min_sources: int = 3
) -> Dict:
    """
    Research a topic with freshness validation
    
    Note: This is a placeholder. Real implementation would:
    1. Call web search API (Brave, Google)
    2. Parse results
    3. Extract dates
    4. Score each source
    """
    # Placeholder results
    results = {
        "query": query,
        "content_type": content_type,
        "search_time": datetime.now().isoformat(),
        "findings": [],
        "outdated_count": 0,
        "fresh_count": 0
    }
    
    # In real implementation, these would come from web search
    # For now, return structure example
    
    return results


def validate_sources(
    sources: List[Dict],
    content_type: str = "general"
) -> Dict:
    """
    Validate a list of sources for freshness
    
    Args:
        sources: List of source dicts with 'date' and 'source' fields
        content_type: Type of content being researched
    
    Returns:
        Validation results
    """
    validated = []
    outdated = []
    
    for src in sources:
        date_str = src.get("date", "")
        pub_date = parse_date(date_str)
        
        if not pub_date:
            validated.append({
                **src,
                "freshness": {
                    "score": 0,
                    "status": "unknown",
                    "error": "无法解析日期"
                }
            })
            continue
        
        freshness = calculate_freshness_score(pub_date, content_type)
        credibility = evaluate_source_credibility(src.get("source", ""))
        
        # Calculate overall score
        overall = (freshness["score"] * 0.4) + (credibility * 0.4) + (src.get("relevance", 5) * 0.2)
        
        result = {
            **src,
            "freshness": freshness,
            "credibility_score": credibility,
            "overall_score": round(overall, 1)
        }
        
        if freshness["status"] == "outdated":
            outdated.append(result)
        else:
            validated.append(result)
    
    # Sort by overall score
    validated.sort(key=lambda x: x["overall_score"], reverse=True)
    
    return {
        "validation_time": datetime.now().isoformat(),
        "content_type": content_type,
        "total_sources": len(sources),
        "fresh_sources": len(validated),
        "outdated_sources": len(outdated),
        "validated": validated,
        "outdated": outdated,
        "gaps": generate_gaps_report(validated, outdated)
    }


def generate_gaps_report(validated: List[Dict], outdated: List[Dict]) -> List[str]:
    """Generate report of research gaps"""
    gaps = []
    
    if not validated:
        gaps.append("没有找到有效的最新资料，建议扩大搜索范围")
    
    if len(outdated) > len(validated):
        gaps.append("过时资料较多，建议优先搜索2026年最新内容")
    
    # Check for date coverage
    dates = [parse_date(v.get("date", "")) for v in validated if parse_date(v.get("date", ""))]
    if dates:
        newest = max(dates)
        if (datetime.now() - newest).days > 60:
            gaps.append(f"最新资料为{newest.strftime('%Y-%m')}，建议搜索更近内容")
    
    return gaps


def main():
    parser = argparse.ArgumentParser(
        description="Research with freshness validation"
    )
    parser.add_argument(
        "--query",
        help="Search query"
    )
    parser.add_argument(
        "--sources",
        help="JSON file with existing sources to validate"
    )
    parser.add_argument(
        "--type",
        choices=["technology", "data", "trends", "general"],
        default="general",
        help="Content type for freshness rules"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file for results"
    )
    
    args = parser.parse_args()
    
    if args.sources:
        # Validate existing sources
        try:
            with open(args.sources, 'r', encoding='utf-8') as f:
                sources = json.load(f)
        except Exception as e:
            print(f"Error loading sources: {e}", file=sys.stderr)
            sys.exit(1)
        
        result = validate_sources(sources, args.type)
    
    elif args.query:
        # Research new topic
        result = research_topic(args.query, args.type)
    
    else:
        print("Error: Either --query or --sources required", file=sys.stderr)
        sys.exit(1)
    
    # Save output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
