#!/usr/bin/env python3
"""
Humanize Writing - Detect AI patterns in text
Analyzes text for common AI writing characteristics
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple


# AI pattern definitions
AI_PATTERNS = {
    "generic_openings": [
        r"in today's (world|society|era|landscape)",
        r"in (our|this) (modern|current|rapidly changing) (world|society|era)",
        r"in this day and age",
        r"as we all know",
        r"it (is|was) (important|crucial|essential) to (note|understand|remember)",
        r"it (is|was) worth (mentioning|noting)",
    ],
    "excessive_signposting": [
        r"^(first|second|third|fourth|finally)[,.]?\s",
        r"^(firstly|secondly|thirdly)[,.]?\s",
        r"let's (dive|jump|get) (in|right in|started)",
        r"without further ado",
        r"in conclusion",
        r"to (sum up|summarize)",
    ],
    "formal_language": [
        r"one could argue",
        r"it could be said",
        r"some might suggest",
        r"furthermore",
        r"moreover",
        r"additionally",
        r"nevertheless",
        r"nonetheless",
    ],
    "vague_generalizations": [
        r"many people",
        r"some experts",
        r"research shows",
        r"studies indicate",
        r"it is widely believed",
        r"various factors",
        r"there are (many|several) reasons",
    ],
    "passive_voice": [
        r"was (done|made|created|decided)",
        r"were (done|made|created|decided)",
        r"is (considered|believed|thought)",
        r"are (considered|believed|thought)",
    ],
}


def detect_patterns(text: str) -> Dict:
    """
    Detect AI writing patterns in text
    
    Args:
        text: Input text to analyze
    
    Returns:
        Dictionary with detected patterns and scores
    """
    text_lower = text.lower()
    results = {
        "patterns_found": {},
        "total_score": 0,
        "risk_level": "low",
        "suggestions": []
    }
    
    total_matches = 0
    
    for category, patterns in AI_PATTERNS.items():
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text_lower, re.IGNORECASE)
            if found:
                matches.extend(found)
        
        if matches:
            results["patterns_found"][category] = {
                "count": len(matches),
                "examples": list(set(matches))[:3]  # Unique examples, max 3
            }
            total_matches += len(matches)
    
    # Calculate score (0-100)
    word_count = len(text.split())
    if word_count > 0:
        pattern_density = (total_matches / word_count) * 100
        results["total_score"] = min(100, pattern_density * 5)  # Scale up
    
    # Determine risk level
    if results["total_score"] < 20:
        results["risk_level"] = "low"
    elif results["total_score"] < 50:
        results["risk_level"] = "medium"
    else:
        results["risk_level"] = "high"
    
    # Generate suggestions
    if "generic_openings" in results["patterns_found"]:
        results["suggestions"].append("Replace generic opening with specific hook")
    
    if "excessive_signposting" in results["patterns_found"]:
        results["suggestions"].append("Remove signposting phrases, use natural flow")
    
    if "formal_language" in results["patterns_found"]:
        results["suggestions"].append("Replace formal phrases with casual alternatives")
    
    if "vague_generalizations" in results["patterns_found"]:
        results["suggestions"].append("Add specific examples instead of generalizations")
    
    if "passive_voice" in results["patterns_found"]:
        results["suggestions"].append("Convert passive voice to active voice")
    
    # Check for lack of contractions
    contraction_count = len(re.findall(r"\b(don't|can't|won't|isn't|aren't|didn't|it's|that's|there's)\b", text_lower))
    if contraction_count < 2 and word_count > 100:
        results["suggestions"].append("Add contractions for conversational tone")
    
    return results


def analyze_structure(text: str) -> Dict:
    """
    Analyze text structure for AI characteristics
    """
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    if not paragraphs:
        return {"paragraph_count": 0, "avg_length": 0, "uniformity_score": 0}
    
    lengths = [len(p.split()) for p in paragraphs]
    avg_length = sum(lengths) / len(lengths)
    
    # Check uniformity (AI tends to have similar paragraph lengths)
    if len(lengths) > 1:
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        uniformity_score = 100 - min(100, variance / 10)  # Lower variance = higher uniformity
    else:
        uniformity_score = 0
    
    return {
        "paragraph_count": len(paragraphs),
        "avg_length": round(avg_length, 1),
        "lengths": lengths,
        "uniformity_score": round(uniformity_score, 1)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze text for AI writing patterns"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input file containing text to analyze"
    )
    parser.add_argument(
        "--output",
        help="Output file for analysis results (JSON)"
    )
    
    args = parser.parse_args()
    
    # Load text
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error loading text: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Analyze
    pattern_results = detect_patterns(text)
    structure_results = analyze_structure(text)
    
    # Combine results
    results = {
        "pattern_analysis": pattern_results,
        "structure_analysis": structure_results,
        "overall_assessment": {
            "ai_likelihood": pattern_results["risk_level"],
            "confidence": round(pattern_results["total_score"], 1),
            "word_count": len(text.split())
        }
    }
    
    # Output
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
