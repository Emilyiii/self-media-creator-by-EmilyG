#!/usr/bin/env python3
"""
Content Image Generator - Automatic image selection
Selects the best images from generated variations based on criteria
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional


def evaluate_image(image_path: str, criteria: Dict) -> Dict:
    """
    Evaluate an image based on selection criteria
    
    Args:
        image_path: Path to the image file
        criteria: Selection criteria dict
    
    Returns:
        Evaluation result with score and reasoning
    """
    # TODO: Implement actual image evaluation
    # This could use:
    # - CLIP for relevance scoring
    # - Aesthetic prediction models
    # - Manual rules (file size, dimensions, etc.)
    
    # Placeholder implementation
    result = {
        "path": image_path,
        "score": 0.0,
        "reasoning": "Placeholder evaluation"
    }
    
    # Check file exists and has reasonable size
    path = Path(image_path)
    if path.exists():
        size = path.stat().st_size
        if size > 10000:  # At least 10KB
            result["score"] = 0.8
            result["reasoning"] = f"File exists and has reasonable size ({size} bytes)"
        else:
            result["score"] = 0.3
            result["reasoning"] = f"File too small ({size} bytes), may be corrupted"
    else:
        result["score"] = 0.0
        result["reasoning"] = "File does not exist"
    
    return result


def select_best_images(
    generation_results: List[Dict],
    selection_config: Dict
) -> List[Dict]:
    """
    Select best images from generation results
    
    Args:
        generation_results: List of generation result dicts
        selection_config: Configuration for selection
            - strategy: "best_per_group" | "threshold" | "top_n"
            - group_by: field to group variations (default: "id" prefix)
            - threshold: minimum score for threshold strategy
            - top_n: number of images to select for top_n strategy
    
    Returns:
        List of selected images with metadata
    """
    strategy = selection_config.get("strategy", "best_per_group")
    
    # Group images by their base ID (e.g., "cover_v1" and "cover_v2" both group under "cover")
    groups = {}
    for result in generation_results:
        if result.get("status") not in ("success", "dry_run"):
            continue
        
        image_id = result.get("id", "")
        # Extract base ID (e.g., "cover" from "cover_v1")
        base_id = image_id.rsplit("_v", 1)[0] if "_v" in image_id else image_id
        
        if base_id not in groups:
            groups[base_id] = []
        groups[base_id].append(result)
    
    selected = []
    
    if strategy == "best_per_group":
        # Select best from each group
        for base_id, images in groups.items():
            # Evaluate all images in group
            evaluated = []
            for img in images:
                eval_result = evaluate_image(img.get("path", ""), {})
                evaluated.append({
                    **img,
                    "score": eval_result["score"],
                    "reasoning": eval_result["reasoning"]
                })
            
            # Sort by score and pick best
            evaluated.sort(key=lambda x: x["score"], reverse=True)
            best = evaluated[0]
            
            selected.append({
                "id": base_id,
                "selected_path": best["path"],
                "score": best["score"],
                "alternatives": [e["path"] for e in evaluated[1:]],
                "reasoning": best["reasoning"]
            })
    
    elif strategy == "threshold":
        threshold = selection_config.get("threshold", 0.7)
        for result in generation_results:
            if result.get("status") not in ("success", "dry_run"):
                continue
            
            eval_result = evaluate_image(result.get("path", ""), {})
            if eval_result["score"] >= threshold:
                selected.append({
                    "id": result.get("id"),
                    "selected_path": result["path"],
                    "score": eval_result["score"],
                    "reasoning": eval_result["reasoning"]
                })
    
    elif strategy == "top_n":
        top_n = selection_config.get("top_n", 3)
        
        # Evaluate all
        evaluated = []
        for result in generation_results:
            if result.get("status") not in ("success", "dry_run"):
                continue
            eval_result = evaluate_image(result.get("path", ""), {})
            evaluated.append({
                **result,
                "score": eval_result["score"],
                "reasoning": eval_result["reasoning"]
            })
        
        # Sort and pick top N
        evaluated.sort(key=lambda x: x["score"], reverse=True)
        for item in evaluated[:top_n]:
            selected.append({
                "id": item.get("id"),
                "selected_path": item["path"],
                "score": item["score"],
                "reasoning": item["reasoning"]
            })
    
    return selected


def main():
    parser = argparse.ArgumentParser(
        description="Select best images from generated variations"
    )
    parser.add_argument(
        "--results",
        required=True,
        help="JSON file containing generation results"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file for selection results"
    )
    parser.add_argument(
        "--strategy",
        choices=["best_per_group", "threshold", "top_n"],
        default="best_per_group",
        help="Selection strategy"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Minimum score for threshold strategy"
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=3,
        help="Number of images for top_n strategy"
    )
    
    args = parser.parse_args()
    
    # Load generation results
    try:
        with open(args.results, 'r', encoding='utf-8') as f:
            generation_results = json.load(f)
    except Exception as e:
        print(f"Error loading results: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Configure selection
    config = {
        "strategy": args.strategy,
        "threshold": args.threshold,
        "top_n": args.top_n
    }
    
    # Select best images
    selected = select_best_images(generation_results, config)
    
    # Save results
    output = {
        "selection_config": config,
        "selected_images": selected,
        "summary": {
            "total_evaluated": len(generation_results),
            "selected_count": len(selected),
            "average_score": sum(s["score"] for s in selected) / len(selected) if selected else 0
        }
    }
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"Selection complete!")
    print(f"Selected {len(selected)} images from {len(generation_results)} candidates")
    print(f"Results saved to: {output_path}")
    
    for img in selected:
        print(f"  ✓ {img['id']}: {img['selected_path']} (score: {img['score']:.2f})")


if __name__ == "__main__":
    main()
