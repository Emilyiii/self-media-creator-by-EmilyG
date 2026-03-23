#!/usr/bin/env python3
"""Heartbeat 用于完成 pending 的选题任务"""

import json
import urllib.request
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOPICS_DIR = PROJECT_ROOT / "output" / "daily_topics"
TOPICS_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = PROJECT_ROOT / "config" / ".env.feishu"
LOG_FILE = Path("/tmp/self-media-pending.log")
FALLBACK_ANGLES = ["趋势洞察", "入门指南", "实战案例"]


def read_webhook_url() -> str | None:
    if not CONFIG_FILE.exists():
        return None
    with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip().startswith("FEISHU_WEBHOOK_URL"):
                _, raw = line.split("=", 1)
                return raw.strip().strip('"').strip("'")
    return None


def log(message: str) -> None:
    entry = f"{datetime.now().isoformat()} {message}"
    print(entry)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text((LOG_FILE.read_text(encoding="utf-8") if LOG_FILE.exists() else "") + entry + "\n", encoding="utf-8")


def format_notification(direction: str, topics: list[dict], platform: str) -> str:
    platform_name = "公众号" if platform == "wechat" else "小红书"
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


def send_notification(webhook_url: str, text: str) -> bool:
    payload = {"msg_type": "text", "content": {"text": text}}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result.get("code") == 0
    except Exception as exc:
        log(f"飞书通知失败：{exc}")
        return False


def build_topics(direction: str, platform: str, angles: list[str]) -> list[dict]:
    topics: list[dict] = []
    for idx, angle in enumerate(angles[:3], start=1):
        estimated = "1500-1900字" if platform == "wechat" else "200-260字"
        title = f"{angle}：把{direction}落地到行动清单"
        description = f"从{angle}的角度切入，拆解{direction}的可复制方法和具体步骤。"
        topics.append({
            "id": idx,
            "title": title,
            "description": description,
            "angle": angle,
            "estimated_length": estimated
        })
    while len(topics) < 3:
        topics.append({
            "id": len(topics) + 1,
            "title": f"{direction}：{len(topics) + 1}号角度",
            "description": "备用模板",
            "angle": FALLBACK_ANGLES[(len(topics)) % len(FALLBACK_ANGLES)],
            "estimated_length": "1500-1700字" if platform == "wechat" else "180-220字"
        })
    return topics


def process_task(path: Path, webhook_url: str | None) -> None:
    with open(path, "r", encoding="utf-8") as fh:
        task = json.load(fh)
    if task.get("status") != "pending":
        return
    direction = task.get("direction", "AI选题")
    platform = task.get("platform", "wechat")
    angles = task.get("angles") or FALLBACK_ANGLES
    if len(angles) < 3:
        angles = angles + FALLBACK_ANGLES
    angles = angles[:3]
    output_path = Path(task.get("output_file") or TOPICS_DIR / f"topics_{datetime.now().strftime('%Y%m%d')}.json")
    topics = build_topics(direction, platform, angles)
    now = datetime.now().isoformat()
    result = {
        "date": datetime.now().strftime("%Y%m%d"),
        "direction": direction,
        "platform": platform,
        "topics": topics,
        "status": "completed",
        "selected_id": None,
        "created_at": now,
        "completed_at": now,
        "llm_generated": False
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    task["status"] = "completed"
    task["completed_at"] = now
    task["result_file"] = str(output_path)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(task, fh, ensure_ascii=False, indent=2)
    notification = format_notification(direction, topics, platform)
    if webhook_url:
        success = send_notification(webhook_url, notification)
        if success:
            log(f"通知已发送 {path.name}")
        else:
            log(f"通知发送失败 {path.name}")
    else:
        log(f"未配置 webhook，跳过通知 {path.name}")


def main() -> None:
    webhook_url = read_webhook_url()
    pending = sorted(TOPICS_DIR.glob("_llm_task_*.json"))
    handled = False
    for task_file in pending:
        with open(task_file, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        if payload.get("status") == "pending":
            handled = True
            log(f"开始处理 {task_file.name}")
            process_task(task_file, webhook_url)
    if not handled:
        log("没有 pending 任务")


if __name__ == "__main__":
    main()
