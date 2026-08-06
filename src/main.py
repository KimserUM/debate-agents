"""
main.py -- 辩论系统入口

用法:
  python -m src.main --topic "要不要学Rust" --mock       (mock模式, 不需要API key)
  python -m src.main --topic "微服务还是单体" --rounds 3
  python -m src.main --topic "..." --config roles.json   (自定义角色)
  python -m src.main --topic "..." --output debate.txt   (保存到文件)
  python -m src.main --init-config my_roles.json         (导出默认配置模板)

环境变量: OPENAI_API_KEY=(mock模式下不需要)
可选: OPENAI_BASE_URL, OPENAI_MODEL

230511535 杨光裕
"""

import os
import sys
import argparse

from src.llm import LLMClient
from src.debate import DebateCoordinator


def main():
    parser = argparse.ArgumentParser(
        description="多Agent辩论系统 -- 3个role辩论, judge裁决"
    )
    parser.add_argument("--topic", "-t", default=None,
                        help="辩论话题")
    parser.add_argument("--rounds", "-r", type=int, default=2,
                        help="辩论round数(默认2round)")
    parser.add_argument("--model", "-m", default=None,
                        help="模型名(默认gpt-4o-mini)")
    parser.add_argument("--mock", action="store_true",
                        help="mock模式, 预设reply, 不需要API key")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="安静模式, 只输出verdict")
    parser.add_argument("--output", "-o", default=None,
                        help="保存完整debate记录到文件")
    parser.add_argument("--config", "-c", default=None,
                        help="自定义role配置文件(JSON)")
    parser.add_argument("--stats", "-s", action="store_true",
                        help="显示debate统计信息")
    parser.add_argument("--init-config", default=None,
                        help="导出默认配置模板到指定路径, 然后退出")
    args = parser.parse_args()

    # --init-config: 导出模板后退出
    if args.init_config:
        from src.config import save_default_config
        save_default_config(args.init_config)
        return

    if not args.topic:
        parser.error("需要 --topic 参数")

    # --- 自定义角色 ---
    agent_configs = None
    if args.config:
        from src.config import load_config, build_agents_from_config
        cfg = load_config(args.config)
        agent_configs = build_agents_from_config(cfg)
        if "settings" in cfg:
            s = cfg["settings"]
            if "max_rounds" in s and not args.rounds:
                args.rounds = s["max_rounds"]
        print(f"加载自定义角色: {[a.name for a in agent_configs]}")

    # --- 选择LLM后端 ---
    if args.mock:
        from src.mock_llm import MockLLM
        llm = MockLLM()
        print("模式: MockLLM (不需要API key)")
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
    coordinator = DebateCoordinator(
        llm, max_rounds=args.rounds, agent_configs=agent_configs
    )
    result = coordinator.run(args.topic, verbose=not args.quiet)

    if args.quiet:
        print(result.verdict)

    print(f"\n总结: {result.summary}")

    # --- 统计 ---
    if args.stats:
        print()
        print(coordinator.stats.summary())

    # --- 导出到文件 ---
    if args.output:
        dirname = os.path.dirname(os.path.abspath(args.output))
        os.makedirs(dirname or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(f"辩论话题: {result.topic}\n")
            f.write(f"轮数: {args.rounds}\n")
            f.write(f"模式: {'mock' if args.mock else 'API'}\n")
            f.write("=" * 50 + "\n\n")
            for r in result.rounds:
                f.write(f"[{r.speaker}] (第{r.round_num}round)\n")
                f.write(r.content + "\n\n")
            f.write("-" * 50 + "\n")
            f.write(f"[Judge -- 最终verdict]\n{result.verdict}\n")
            if args.stats:
                f.write("\n" + coordinator.stats.summary() + "\n")
        print(f"\n辩论记录已保存到: {args.output}")


if __name__ == "__main__":
    main()
