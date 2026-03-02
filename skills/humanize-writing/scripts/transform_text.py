#!/usr/bin/env python3
"""
Humanize Writing - Transform AI text to natural human voice
Applies humanizing transformations to text
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict


# Transformation rules
TRANSFORMATIONS = {
    "casual": {
        "openings": {
            r"in today's (world|society|era|landscape)[,.]?\s*": ["", "Here's the thing: ", "So, "],
            r"it (is|was) (important|crucial|essential) to (note|understand|remember) that\s*": ["", "Here's the thing: ", ""],
            r"as we all know[,.]?\s*": ["", ""],
        },
        "transitions": {
            r"furthermore[,.]?\s*": ["Plus, ", "And, ", "Also, "],
            r"moreover[,.]?\s*": ["Plus, ", "What's more, ", ""],
            r"additionally[,.]?\s*": ["Plus, ", "And, ", ""],
            r"however[,.]?\s*": ["But, ", "Still, ", "That said, "],
            r"nevertheless[,.]?\s*": ["But, ", "Still, ", ""],
        },
        "formal": {
            r"one could argue that\s*": ["I'd argue that ", "I think ", ""],
            r"it could be said that\s*": ["", ""],
            r"some might suggest\s*": ["Some say ", "People think ", ""],
            r"it is worth noting that\s*": ["", "Note: ", ""],
        },
        "contractions": {
            r"\bdo not\b": "don't",
            r"\bcannot\b": "can't",
            r"\bwill not\b": "won't",
            r"\bis not\b": "isn't",
            r"\bare not\b": "aren't",
            r"\bdid not\b": "didn't",
            r"\bhas not\b": "hasn't",
            r"\bhave not\b": "haven't",
            r"\bit is\b": "it's",
            r"\bthat is\b": "that's",
            r"\bthere is\b": "there's",
        }
    },
    "professional": {
        "openings": {
            r"in today's (world|society|era|landscape)[,.]?\s*": ["", "In recent years, ", ""],
            r"it (is|was) (important|crucial|essential) to (note|understand|remember) that\s*": ["", "Importantly, ", ""],
        },
        "transitions": {
            r"furthermore[,.]?\s*": ["Additionally, ", "Also, ", ""],
            r"moreover[,.]?\s*": ["What's more, ", "Additionally, ", ""],
            r"however[,.]?\s*": ["But, ", "That said, ", "Still, "],
        },
        "formal": {
            r"one could argue that\s*": ["I believe ", "In my view, ", ""],
            r"it could be said that\s*": ["", ""],
        },
        "contractions": {
            # Keep some contractions for professional but human tone
            r"\bdo not\b": "don't",
            r"\bcannot\b": "can't",
            r"\bis not\b": "isn't",
            r"\bare not\b": "aren't",
            r"\bit is\b": "it's",
        }
    }
}


def apply_transformations(text: str, tone: str = "casual") -> str:
    """
    Apply humanizing transformations to text
    
    Args:
        text: Input text
        tone: Target tone (casual/professional)
    
    Returns:
        Transformed text
    """
    import random
    
    rules = TRANSFORMATIONS.get(tone, TRANSFORMATIONS["casual"])
    transformed = text
    changes = []
    
    # Apply opening transformations
    for pattern, replacements in rules.get("openings", {}).items():
        if re.search(pattern, transformed, re.IGNORECASE):
            replacement = random.choice(replacements)
            transformed = re.sub(pattern, replacement, transformed, flags=re.IGNORECASE)
            if replacement:
                changes.append(f"Replaced generic opening with: '{replacement}'")
    
    # Apply transition transformations
    for pattern, replacements in rules.get("transitions", {}).items():
        matches = list(re.finditer(pattern, transformed, re.IGNORECASE))
        for match in matches:
            replacement = random.choice(replacements)
            transformed = transformed[:match.start()] + replacement + transformed[match.end():]
            if replacement:
                changes.append(f"Replaced '{match.group()}' with '{replacement}'")
    
    # Apply formal phrase transformations
    for pattern, replacements in rules.get("formal", {}).items():
        matches = list(re.finditer(pattern, transformed, re.IGNORECASE))
        for match in matches:
            replacement = random.choice(replacements)
            transformed = transformed[:match.start()] + replacement + transformed[match.end():]
            if replacement:
                changes.append(f"Replaced formal phrase with: '{replacement}'")
    
    # Apply contractions
    for pattern, replacement in rules.get("contractions", {}).items():
        matches = len(re.findall(pattern, transformed, re.IGNORECASE))
        if matches > 0:
            transformed = re.sub(pattern, replacement, transformed, flags=re.IGNORECASE)
            changes.append(f"Applied {matches} contraction(s): {pattern} → {replacement}")
    
    # Remove excessive signposting
    signpost_patterns = [
        r"^(first|second|third|fourth|finally)[,.]?\s*",
        r"let's (dive|jump|get) (in|right in|started)[,.]?\s*",
        r"without further ado[,.]?\s*",
    ]
    for pattern in signpost_patterns:
        if re.search(pattern, transformed, re.IGNORECASE | re.MULTILINE):
            transformed = re.sub(pattern, "", transformed, flags=re.IGNORECASE | re.MULTILINE)
            changes.append(f"Removed signposting pattern: {pattern}")
    
    return transformed, changes


def vary_structure(text: str) -> str:
    """
    Vary sentence and paragraph structure
    """
    paragraphs = text.split('\n\n')
    varied = []
    
    for i, para in enumerate(paragraphs):
        sentences = re.split(r'([.!?。！？])', para)
        sentences = [''.join(sentences[i:i+2]) for i in range(0, len(sentences)-1, 2)]
        
        # Occasionally combine short sentences
        if len(sentences) > 2 and i % 3 == 0:
            combined = sentences[0] + ' ' + sentences[1]
            sentences = [combined] + sentences[2:]
        
        # Occasionally split long sentences (simplified)
        # In practice, this would use NLP
        
        varied.append(' '.join(sentences))
    
    return '\n\n'.join(varied)


def add_personal_touch(text: str, tone: str = "casual") -> str:
    """
    Add personal voice markers
    """
    if tone == "casual":
        # Add occasional personal asides
        personal_phrases = [
            " (I know, obvious right?)",
            " (Learned this the hard way)",
            " (Trust me on this one)",
        ]
        # Insert after first long paragraph
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 1 and len(paragraphs[0]) > 100:
            paragraphs[0] = paragraphs[0].rstrip() + personal_phrases[1]
        text = '\n\n'.join(paragraphs)
    
    return text


def main():
    parser = argparse.ArgumentParser(
        description="Transform AI text to natural human voice"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input file containing text to transform"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file for transformed text"
    )
    parser.add_argument(
        "--tone",
        choices=["casual", "professional", "playful"],
        default="casual",
        help="Target tone"
    )
    parser.add_argument(
        "--vary-structure",
        action="store_true",
        help="Vary sentence and paragraph structure"
    )
    parser.add_argument(
        "--add-personal",
        action="store_true",
        help="Add personal voice markers"
    )
    
    args = parser.parse_args()
    
    # Load text
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error loading text: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Apply transformations
    transformed, changes = apply_transformations(text, args.tone)
    
    if args.vary_structure:
        transformed = vary_structure(transformed)
        changes.append("Varied sentence and paragraph structure")
    
    if args.add_personal:
        transformed = add_personal_touch(transformed, args.tone)
        changes.append("Added personal voice markers")
    
    # Save output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(transformed)
    
    # Output result
    result = {
        "input_file": args.input,
        "output_file": str(output_path),
        "tone": args.tone,
        "transformations_applied": changes,
        "original_length": len(text),
        "transformed_length": len(transformed)
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nTransformed text saved to: {output_path}")


if __name__ == "__main__":
    main()
