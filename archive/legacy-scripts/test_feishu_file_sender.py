#!/usr/bin/env python3
"""
飞书文件发送功能测试
测试 FeishuFileSender 类的各项功能
"""

import os
import sys
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 加载环境变量
try:
    from dotenv import load_dotenv
    env_path = PROJECT_ROOT / "config" / ".env.feishu"
    load_dotenv(env_path)
except ImportError:
    # 如果 dotenv 未安装，直接读取环境变量
    pass

# 手动读取 .env 文件（如果环境变量未设置）
if not os.getenv("FEISHU_APP_ID"):
    env_file = PROJECT_ROOT / "config" / ".env.feishu"
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and value and not os.getenv(key):
                        os.environ[key] = value

from scripts.create_content import FeishuFileSender, Logger


def test_get_token():
    """测试获取 access_token"""
    print("\n" + "="*60)
    print("测试 1: 获取 tenant_access_token")
    print("="*60)
    
    sender = FeishuFileSender()
    if not sender.enabled:
        print("❌ FeishuFileSender 未启用，请检查环境变量")
        return False
    
    token = sender._get_tenant_access_token()
    if token:
        print(f"✅ 成功获取 access_token: {token[:20]}...")
        return True
    else:
        print("❌ 获取 access_token 失败")
        return False


def test_send_text():
    """测试发送文本消息"""
    print("\n" + "="*60)
    print("测试 2: 发送文本消息")
    print("="*60)
    
    sender = FeishuFileSender()
    if not sender.enabled:
        print("❌ FeishuFileSender 未启用")
        return False
    
    test_message = "🧪 这是一条测试消息\n来自 Self-Media Creator 的飞书文件发送功能测试"
    
    if sender.send_text_message(test_message):
        print("✅ 文本消息发送成功")
        return True
    else:
        print("❌ 文本消息发送失败")
        return False


def test_send_local_file():
    """测试发送本地文件"""
    print("\n" + "="*60)
    print("测试 3: 发送本地文件")
    print("="*60)
    
    sender = FeishuFileSender()
    if not sender.enabled:
        print("❌ FeishuFileSender 未启用")
        return False
    
    # 创建一个测试文件
    test_file = PROJECT_ROOT / "output" / "test_feishu_send.txt"
    test_file.parent.mkdir(exist_ok=True)
    
    test_content = """# 飞书文件发送测试

这是一个测试文件，用于验证 FeishuFileSender 类的文件发送功能。

## 测试内容
- 文件上传
- 文件消息发送
- 本地文件读取

## 时间
生成时间: 2026-03-16

---
Self-Media Creator
"""
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"创建测试文件: {test_file}")
    
    if sender.send_local_file(str(test_file), send_notification=True):
        print("✅ 本地文件发送成功")
        return True
    else:
        print("❌ 本地文件发送失败")
        return False


def test_send_markdown_file():
    """测试发送 Markdown 文章文件"""
    print("\n" + "="*60)
    print("测试 4: 发送 Markdown 文章文件")
    print("="*60)
    
    sender = FeishuFileSender()
    if not sender.enabled:
        print("❌ FeishuFileSender 未启用")
        return False
    
    # 创建一个模拟的文章文件
    article_file = PROJECT_ROOT / "output" / "test_article.md"
    article_file.parent.mkdir(exist_ok=True)
    
    article_content = """# AI漫剧：2026年最被低估的变现风口

说实话，第一次看到AI生成的连续剧情视频时，我的第一反应是：这不可能吧？

但数据不会说谎。深入研究后我发现，这不仅是真的，而且可能正在改变整个内容创作的游戏规则。

## 核心发现

### 技术突破
可灵2.0和Runway Gen-4等新一代AI视频模型已能生成连贯角色动作和稳定人物形象，解决了早期AI视频中人物突然换脸、场景变形的问题。

### 应用案例
抖音博主'AI故事馆'用AI制作的《我在古代当王妃》系列单集点赞超50万，人物形象保持80集不崩坏。

## 总结

AI漫剧正处于快速发展的关键期，机遇与挑战并存。

---
*本文由 Self-Media Creator 自动生成*
"""
    
    with open(article_file, 'w', encoding='utf-8') as f:
        f.write(article_content)
    
    print(f"创建测试文章: {article_file}")
    
    # 先发送说明文本
    sender.send_text_message("📄 正在发送一篇测试文章...")
    
    if sender.send_local_file(str(article_file), send_notification=False):
        print("✅ 文章文件发送成功")
        return True
    else:
        print("❌ 文章文件发送失败")
        return False


def test_send_directory():
    """测试发送目录下的所有文件"""
    print("\n" + "="*60)
    print("测试 5: 发送目录下的所有文件")
    print("="*60)
    
    sender = FeishuFileSender()
    if not sender.enabled:
        print("❌ FeishuFileSender 未启用")
        return False
    
    # 创建一个测试目录
    test_dir = PROJECT_ROOT / "output" / "test_directory"
    test_dir.mkdir(exist_ok=True)
    
    # 创建多个测试文件
    for i in range(3):
        test_file = test_dir / f"test_file_{i+1}.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(f"# 测试文件 {i+1}\n\n这是第 {i+1} 个测试文件的内容。\n")
    
    print(f"创建测试目录: {test_dir}")
    print(f"包含 3 个测试文件")
    
    result = sender.send_directory_files(str(test_dir), file_extensions=[".md"])
    
    if result.get("success"):
        print(f"✅ 目录文件发送成功: {result['success_count']}/{result['total']}")
        return True
    else:
        print(f"❌ 目录文件发送失败: {result.get('error')}")
        return False


def test_env_variables():
    """测试环境变量配置"""
    print("\n" + "="*60)
    print("环境变量检查")
    print("="*60)
    
    app_id = os.getenv("FEISHU_APP_ID", "")
    app_secret = os.getenv("FEISHU_APP_SECRET", "")
    user_id = os.getenv("FEISHU_USER_ID", "")
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL", "")
    
    print(f"FEISHU_APP_ID: {'✅ 已设置' if app_id else '❌ 未设置'} ({app_id[:15]}..." if app_id else ")")
    print(f"FEISHU_APP_SECRET: {'✅ 已设置' if app_secret else '❌ 未设置'} ({'*' * 10})")
    print(f"FEISHU_USER_ID: {'✅ 已设置' if user_id else '❌ 未设置'} ({user_id[:15]}..." if user_id else ")")
    print(f"FEISHU_WEBHOOK_URL: {'✅ 已设置' if webhook_url else '❌ 未设置'}")
    
    return bool(app_id and app_secret and user_id)


def main():
    """运行所有测试"""
    print("="*60)
    print("飞书文件发送功能测试")
    print("="*60)
    
    # 检查环境变量
    if not test_env_variables():
        print("\n❌ 环境变量未正确配置，请检查 config/.env.feishu 文件")
        sys.exit(1)
    
    # 运行测试
    results = []
    
    try:
        results.append(("获取 Token", test_get_token()))
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        results.append(("获取 Token", False))
    
    try:
        results.append(("发送文本", test_send_text()))
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        results.append(("发送文本", False))
    
    try:
        results.append(("发送本地文件", test_send_local_file()))
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        results.append(("发送本地文件", False))
    
    try:
        results.append(("发送 Markdown 文章", test_send_markdown_file()))
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        results.append(("发送 Markdown 文章", False))
    
    try:
        results.append(("发送目录文件", test_send_directory()))
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        results.append(("发送目录文件", False))
    
    # 打印测试结果汇总
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！飞书文件发送功能正常工作。")
        return 0
    else:
        print(f"\n⚠️ 有 {total - passed} 项测试失败，请检查配置和网络连接。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
