"""
debate.py -- 辩论协调器

编排三个Agent的发言顺序:
  Round 1: 方案提出者发言
  Round 2: 批评者质疑
  Round 3: 方案提出者回应
  Round 4: 批评者补充
  (可选额外回合)
  Final: 裁判裁决

用法:
  coordinator = DebateCoordinator(llm_client, max_rounds=2)
  result = coordinator.run("要不要在项目里引入微服务架构?")

230511535 杨光裕
"""

import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from src.llm import LLMClient
from src.agent import DebateAgent, AgentConfig, get_default_agents
from src.stats import DebateStats


@dataclass
class DebateRound:
    """一轮辩论记录"""
    round_num: int
    speaker: str
    content: str


@dataclass
class DebateResult:
    """辩论结果"""
    topic: str
    rounds: List[DebateRound] = field(default_factory=list)
    verdict: str = ""
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "rounds": [
                {"round": r.round_num, "speaker": r.speaker,
                 "content": r.content}
                for r in self.rounds
            ],
            "verdict": self.verdict,
            "summary": self.summary,
        }


class DebateCoordinator:
    """
    辩论协调器。控制发言顺序和轮数。

    max_rounds: proposer和critic各发言的次数(默认2, 即来回2round + judge)
    agent_configs: 自定义角色配置, 传None用默认三角色
    """

    def __init__(self, llm: LLMClient, max_rounds: int = 2,
                 agent_configs: List[AgentConfig] = None):
        self.llm = llm
        self.max_rounds = max_rounds
        self.stats = DebateStats()
        self.agents = self._create_agents(agent_configs)

    def _create_agents(self, configs: List[AgentConfig] = None
                       ) -> Dict[str, DebateAgent]:
        if configs is None:
            configs = get_default_agents()
        return {
            cfg.role: DebateAgent(cfg, self.llm)
            for cfg in configs
        }

    def run(self, topic: str, verbose: bool = True) -> DebateResult:
        """同步执行辩论, 带stats追踪"""
        result = DebateResult(topic=topic)
        self.stats = DebateStats(topic=topic)
        self.stats.start()

        proposer = self.agents["proposer"]
        critic = self.agents["critic"]
        judge = self.agents["judge"]

        if verbose:
            print(f"辩论话题: {topic}")
            print("=" * 50)

        # Round 1: proposer首次发言
        msg = proposer.speak(topic)
        result.rounds.append(DebateRound(1, proposer.name, msg))
        self.stats.record_speech(proposer.name, msg)
        critic.hear(proposer.name, msg)
        judge.hear(proposer.name, msg)
        if verbose:
            print(f"\n[{proposer.name}]\n{msg}\n")

        # 交替发言
        for i in range(self.max_rounds):
            # critic
            msg = critic.speak(topic)
            result.rounds.append(
                DebateRound(i * 2 + 2, critic.name, msg)
            )
            self.stats.record_speech(critic.name, msg)
            proposer.hear(critic.name, msg)
            judge.hear(critic.name, msg)
            if verbose:
                print(f"[{critic.name}]\n{msg}\n")

            # proposer回应
            if i < self.max_rounds - 1:
                msg = proposer.speak(topic)
                result.rounds.append(
                    DebateRound(i * 2 + 3, proposer.name, msg)
                )
                self.stats.record_speech(proposer.name, msg)
                critic.hear(proposer.name, msg)
                judge.hear(proposer.name, msg)
                if verbose:
                    print(f"[{proposer.name}]\n{msg}\n")

        # 最终裁决
        verdict_prompt = (
            f"辩论主题: {topic}\n\n"
            "你已经听完了双方的辩论。请给出最终裁决:\n"
            "1) 总结双方的核心论点\n"
            "2) 哪个方案更好, 为什么\n"
            "3) 实施建议和注意事项"
        )
        verdict = judge.speak(verdict_prompt)
        result.verdict = verdict
        self.stats.record_verdict(verdict)
        self.stats.finish()
        if verbose:
            print(f"[{judge.name} -- 最终裁决]\n{verdict}\n")
            print("=" * 50)
            print("辩论结束")

        # 生成简要总结
        summary_prompt = (
            f"用100字以内总结这场辩论:\n话题: {topic}\n"
            f"裁决: {verdict[:500]}"
        )
        result.summary = self.llm.chat([
            {"role": "system", "content": "你用中文总结, 一句话。不超过100字。"},
            {"role": "user", "content": summary_prompt},
        ])

        return result

    async def run_async(self, topic: str, verbose: bool = True) -> DebateResult:
        """异步执行(预留, 当前和同步版一样)"""
        return self.run(topic, verbose)


# ---- 测试(不需要API key, 只测结构) ----
if __name__ == "__main__":
    print("DebateCoordinator结构测试:")
    print(f"  默认max_rounds: 2")
    print(f"  角色: proposer, critic, judge")
    print(f"  发言顺序: proposer -> critic -> proposer -> critic -> judge")
    print()
    print("配置API key后运行:")
    print("  export OPENAI_API_KEY=sk-xxx")
    print("  python -m src.debate --topic '是否应该在项目中使用微服务'")
