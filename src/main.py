"""
main.py -- 辩论系统入口

用法:
  python -m src.main --topic "要不要学Rust" --mock    (模拟模式, 不需要API key)
  python -m src.main --topic "微服务还是单体" --rounds 3
  python -m src.main --topic "..." --output debate.txt (保存到文件)

环境变量: OPENAI_API_KEY=(mock模式下不需要)
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
    parser.add_argument("--mock", action="store_true",
                        help="模拟模式, 用预设回复演示流程, 不需要API key")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="安静模式, 只输出最终裁决")
    parser.add_argument("--output", "-o", default=None,
                        help="保存完整辩论记录到文件")
    args = parser.parse_args()

    # --- 选择LLM后端 ---
    if args.mock:
        from src.mock_llm import MockLLM
        llm = MockLLM()
        print("模式: 模拟 (MockLLM, 不需要API key)")
    else:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            print("错误: 请设置 OPENAI_API_KEY 环境变量")
            print("  或使用 --mock 进入模拟模式")
            sys.exit(1)
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model = args.model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        llm = LLMClient(api_key=api_key, base_url=base_url, model=model)
        print(f"模式: API ({model})")

    print(f"轮数: {args.rounds}")
    print()

    # --- 执行辩论 ---
    coordinator = DebateCoordinator(llm, max_rounds=args.rounds)
    result = coordinator.run(args.topic, verbose=not args.quiet)

    if args.quiet:
        print(result.verdict)

    print(f"\n总结: {result.summary}")

    # --- 导出到文件 ---
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(f"辩论话题: {result.topic}\n")
            f.write(f"轮数: {args.rounds}\n")
            f.write(f"模式: {'模拟' if args.mock else 'API'}\n")
            f.write("=" * 50 + "\n\n")
            for r in result.rounds:
                f.write(f"[{r.speaker}] (第{r.round_num}轮)\n")
                f.write(r.content + "\n\n")
            f.write("-" * 50 + "\n")
            f.write(f"[裁判 - 最终裁决]\n{result.verdict}\n")
        print(f"\n辩论记录已保存到: {args.output}")


if __name__ == "__main__":
    main()
