"""
main.py -- 辩论系统入口

用法:
  python -m src.main --topic "要不要学Rust"
  python -m src.main --topic "微服务还是单体" --rounds 3

环境变量: OPENAI_API_KEY=(必填)
可选: OPENAI_BASE_URL=(默认OpenAI), OPENAI_MODEL=(默认gpt-4o-mini)

230511535 杨光裕
"""

import os
import sys
import argparse

from src.llm import LLMClient
from src.debate import DebateCoordinator


def main():
    parser = argparse.ArgumentParser(
        description="多Agent辩论系统 -- 3个角色辩论, 裁判裁决"
    )
    parser.add_argument("--topic", "-t", required=True,
                        help="辩论话题")
    parser.add_argument("--rounds", "-r", type=int, default=2,
                        help="辩论轮数(默认2轮)")
    parser.add_argument("--model", "-m", default=None,
                        help="模型名(默认gpt-4o-mini)")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="安静模式, 只输出最终裁决")
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        print("错误: 请设置 OPENAI_API_KEY 环境变量")
        print("  export OPENAI_API_KEY=sk-xxx")
        sys.exit(1)

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = args.model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    print(f"模型: {model}")
    print(f"轮数: {args.rounds}")
    print()

    llm = LLMClient(api_key=api_key, base_url=base_url, model=model)
    coordinator = DebateCoordinator(llm, max_rounds=args.rounds)
    result = coordinator.run(args.topic, verbose=not args.quiet)

    if args.quiet:
        print(result.verdict)

    # 显示总结
    print(f"\n总结: {result.summary}")


if __name__ == "__main__":
    main()
