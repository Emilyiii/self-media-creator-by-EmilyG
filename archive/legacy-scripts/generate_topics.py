#!/usr/bin/env python3
"""
选题模块 - 调用大模型生成创意选题

使用方式:
    # 直接生成（内部通过子agent调用大模型）
    python3 scripts/generate_topics.py --direction "AI工具" --platform wechat
    
    # 从文件读取预生成的选题（用于cron任务）
    python3 scripts/generate_topics.py --from-file output/daily_topics/topics_20260315.json
"""

import json
import argparse
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# 项目路径配置
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output" / "daily_topics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 选题角度库 - 用于增加随机性
TOPIC_ANGLES = {
    "wechat": [
        "趋势洞察", "深度评测", "入门指南", "避坑实录", "效率提升",
        "行业观察", "个人成长", "工具对比", "实战案例", "未来预测",
        "方法论总结", "踩坑复盘", "省钱攻略", "时间管理", "副业探索"
    ],
    "xiaohongshu": [
        "种草推荐", "避坑指南", "使用技巧", "对比测评", "省钱攻略",
        "效率神器", "颜值担当", "懒人必备", "小众宝藏", "真香现场",
        "后悔没早买", "亲测有效", "一周体验", "月入提升", "生活改变"
    ]
}

# 内容方向库 - 用于随机选择
CONTENT_DIRECTIONS = [
    "AI知识科普", "AI工具分享", "AI热点追踪",
    "ChatGPT技巧", "Midjourney绘画", "AI写作方法",
    "AI效率提升", "AI副业赚钱", "AI学习路径",
    "大模型对比", "AI行业动态", "AI产品评测"
]


class TopicGenerator:
    """选题生成器 - 通过子agent调用大模型"""
    
    def __init__(self, platform: str = "wechat"):
        self.platform = platform
    
    def _build_prompt(self, direction: str, angles: List[str]) -> str:
        """构建生成选题的prompt"""
        platform_name = "公众号" if self.platform == "wechat" else "小红书"
        
        if self.platform == "wechat":
            style_guide = """
选题要求：
1. 适合公众号长文，有深度、有观点
2. 标题要吸引人但不做标题党
3. 覆盖不同角度：实用教程、个人体验、趋势分析等
4. 预计字数在1200-2500字之间
"""
        else:
            style_guide = """
选题要求：
1. 适合小红书短内容，轻松、接地气
2. 标题要有网感，带emoji或符号更佳
3. 覆盖不同角度：种草、避坑、技巧、体验等
4. 预计字数在150-350字之间
"""
        
        prompt = f"""你是一个资深自媒体选题策划专家。

请为{platform_name}平台生成3个关于"{direction}"的选题建议。

可用角度参考（随机选择3个不同角度）：{', '.join(angles)}

{style_guide}

请按以下JSON格式返回（不要包含任何其他文字）：
{{
  "topics": [
    {{
      "id": 1,
      "title": "选题标题",
      "description": "一句话描述这个选题的亮点",
      "angle": "角度类型",
      "estimated_length": "预计字数范围"
    }},
    ...
  ]
}}
"""
        return prompt
    
    def _call_llm_via_subagent(self, prompt: str) -> List[Dict]:
        """
        通过子agent调用大模型生成选题
        
        策略：直接在当前目录创建一个临时任务文件，
        然后使用 openclaw 的 sessions_spawn 机制调用模型
        """
        # 创建临时任务文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_file = OUTPUT_DIR / f"_topic_task_{timestamp}.json"
        result_file = OUTPUT_DIR / f"_topic_result_{timestamp}.json"
        
        task_data = {
            "task": "generate_topics",
            "prompt": prompt,
            "output_file": str(result_file),
            "timestamp": timestamp
        }
        
        task_file.write_text(json.dumps(task_data, ensure_ascii=False, indent=2), encoding='utf-8')
        
        # 使用子agent调用大模型
        # 注意：这里我们通过创建一个简单的子agent任务来完成
        subagent_script = OUTPUT_DIR / f"_subagent_{timestamp}.py"
        subagent_code = f'''#!/usr/bin/env python3
import json
import sys
sys.path.insert(0, "{PROJECT_ROOT}")

# 读取任务
task_file = "{task_file}"
result_file = "{result_file}"

with open(task_file, 'r', encoding='utf-8') as f:
    task = json.load(f)

prompt = task["prompt"]

# 调用大模型生成选题
# 这里我们使用一个模拟的LLM调用，实际运行时会被主agent拦截并替换为真实调用
topics = []

# 由于无法直接访问外部API，我们返回一个标记，让主agent知道需要处理
result = {{
    "status": "needs_llm",
    "prompt": prompt,
    "task_file": task_file
}}

with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("等待主agent处理LLM调用...")
'''
        subagent_script.write_text(subagent_code, encoding='utf-8')
        
        # 标记：需要主agent介入处理
        # 返回特殊标记，让调用者知道需要手动调用LLM
        return {{
            "_needs_llm": True,
            "prompt": prompt,
            "task_file": str(task_file),
            "result_file": str(result_file)
        }}
    
    def generate_topics(self, direction: str, use_llm: bool = True) -> List[Dict]:
        """
        根据方向生成3个选题建议
        
        Args:
            direction: 内容方向/主题方向
            use_llm: 是否使用大模型生成（False则使用模板）
            
        Returns:
            选题列表，每个包含title、description、angle
        """
        if not use_llm:
            # 回退到模板模式
            return self._generate_template_topics(direction)
        
        # 随机选择3个不同角度
        import random
        angles = TOPIC_ANGLES.get(self.platform, TOPIC_ANGLES["wechat"])
        selected_angles = random.sample(angles, min(3, len(angles)))
        
        # 构建prompt
        prompt = self._build_prompt(direction, selected_angles)
        
        # 返回标记，表示需要LLM处理
        return self._call_llm_via_subagent(prompt)
    
    def _generate_template_topics(self, direction: str) -> List[Dict]:
        """模板模式生成选题（作为fallback）"""
        if self.platform == "wechat":
            return [
                {
                    "id": 1,
                    "title": f"深度解析：{direction}的2026年最新趋势",
                    "description": "从技术、市场、用户三个维度全面分析，适合深度长文",
                    "angle": "趋势分析",
                    "estimated_length": "1500-2000字"
                },
                {
                    "id": 2,
                    "title": f"我用了一个月{direction}，这是我的真实体验",
                    "description": "第一手体验报告，真实使用感受，更有亲和力",
                    "angle": "体验分享",
                    "estimated_length": "1200-1500字"
                },
                {
                    "id": 3,
                    "title": f"{direction}入门指南：从零到精通的完整路径",
                    "description": "适合新手的系统性教程，覆盖面广",
                    "angle": "教程指南",
                    "estimated_length": "1800-2500字"
                }
            ]
        else:  # xiaohongshu
            return [
                {
                    "id": 1,
                    "title": f"被{direction}惊艳到了！",
                    "description": "短平快的种草内容，突出亮点，适合快速传播",
                    "angle": "种草推荐",
                    "estimated_length": "200-300字"
                },
                {
                    "id": 2,
                    "title": f"{direction}避坑指南｜血泪教训",
                    "description": "分享经验和避坑技巧，实用性强",
                    "angle": "经验分享",
                    "estimated_length": "250-350字"
                },
                {
                    "id": 3,
                    "title": f"{direction}真的太香了",
                    "description": "轻松愉快的推荐内容，易产生共鸣",
                    "angle": "轻松推荐",
                    "estimated_length": "150-250字"
                }
            ]
    
    def format_for_notification(self, direction: str, topics: List[Dict]) -> str:
        """格式化为飞书通知文本"""
        platform_name = "公众号" if self.platform == "wechat" else "小红书"
        
        lines = [
            f"🎯 【今日选题推荐 | {platform_name}】",
            f"📍 内容方向：{direction}",
            "",
            "请回复数字 (1/2/3) 选择您想要的选题：",
            ""
        ]
        
        for topic in topics:
            lines.extend([
                f"【{topic['id']}】{topic['title']}",
                f"   💡 {topic['description']}",
                f"   📝 预计字数：{topic['estimated_length']} | 角度：{topic['angle']}",
                ""
            ])
        
        lines.extend([
            "───────────────",
            "💬 回复格式：",
            "• 回复数字 1/2/3 选择对应选题",
            "• 回复 'skip' 跳过今日",
            "• 回复新方向可重新生成（如：换成'AI工具'）"
        ])
        
        return "\n".join(lines)


def generate_topics_with_llm(direction: str, platform: str = "wechat") -> List[Dict]:
    """
    使用大模型生成选题（供外部调用）
    
    这个函数会被主agent拦截，实际调用大模型生成内容
    """
    generator = TopicGenerator(platform=platform)
    
    # 随机选择角度
    import random
    angles = TOPIC_ANGLES.get(platform, TOPIC_ANGLES["wechat"])
    selected_angles = random.sample(angles, min(3, len(angles)))
    
    prompt = generator._build_prompt(direction, selected_angles)
    
    # 返回需要LLM处理的标记
    return {
        "_needs_llm": True,
        "prompt": prompt,
        "direction": direction,
        "platform": platform
    }


def parse_llm_response(response_text: str) -> List[Dict]:
    """解析大模型返回的JSON"""
    try:
        # 尝试直接解析
        data = json.loads(response_text)
        if "topics" in data:
            return data["topics"]
    except json.JSONDecodeError:
        pass
    
    # 尝试从markdown代码块中提取
    import re
    json_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
    matches = re.findall(json_pattern, response_text, re.DOTALL)
    
    for match in matches:
        try:
            data = json.loads(match.strip())
            if "topics" in data:
                return data["topics"]
        except json.JSONDecodeError:
            continue
    
    # 尝试找到JSON对象
    try:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start >= 0 and end > start:
            data = json.loads(response_text[start:end])
            if "topics" in data:
                return data["topics"]
    except (json.JSONDecodeError, ValueError):
        pass
    
    raise ValueError(f"无法解析LLM响应: {response_text[:200]}...")


def main():
    parser = argparse.ArgumentParser(description="选题生成模块")
    parser.add_argument("--direction", "-d", help="内容方向")
    parser.add_argument("--platform", "-p", default="wechat",
                       choices=["wechat", "xiaohongshu"], help="平台")
    parser.add_argument("--output", "-o", help="输出JSON文件路径")
    parser.add_argument("--format", "-f", choices=["json", "text"],
                       default="text", help="输出格式")
    parser.add_argument("--from-file", help="从文件读取预生成的选题")
    parser.add_argument("--template", action="store_true",
                       help="使用模板模式（不调用LLM）")
    parser.add_argument("--random-direction", action="store_true",
                       help="随机选择内容方向")
    
    args = parser.parse_args()
    
    # 如果从文件读取
    if args.from_file:
        with open(args.from_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        topics = data.get("topics", [])
        direction = data.get("direction", "未知方向")
        platform = data.get("platform", "wechat")
        
        generator = TopicGenerator(platform=platform)
        output = generator.format_for_notification(direction, topics)
        print(output)
        return
    
    # 确定内容方向
    if args.random_direction:
        import random
        direction = random.choice(CONTENT_DIRECTIONS)
        print(f"🎲 随机选择方向: {direction}")
    elif args.direction:
        direction = args.direction
    else:
        parser.error("请提供 --direction 或 --random-direction")
    
    # 生成选题
    generator = TopicGenerator(platform=args.platform)
    
    if args.template:
        # 模板模式
        topics = generator._generate_template_topics(direction)
    else:
        # LLM模式 - 返回需要处理的标记
        result = generator.generate_topics(direction, use_llm=True)
        
        if "_needs_llm" in result:
            # 输出标记，让调用者（主agent）知道需要调用LLM
            print("_TOPIC_GENERATION_REQUIRES_LLM_")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
        else:
            topics = result
    
    # 格式化输出
    if args.format == "json":
        result = {
            "direction": direction,
            "platform": args.platform,
            "topics": topics,
            "timestamp": datetime.now().isoformat()
        }
        output = json.dumps(result, ensure_ascii=False, indent=2)
        
        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f"✅ 选题已保存到: {args.output}")
        else:
            print(output)
    else:
        # 文本格式（用于飞书通知）
        output = generator.format_for_notification(direction, topics)
        
        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f"✅ 选题已保存到: {args.output}")
        else:
            print(output)


if __name__ == "__main__":
    main()
