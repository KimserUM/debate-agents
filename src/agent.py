"""
agent.py -- 辩论Agent

每个Agent有角色名、性格描述和系统prompt。
converse()方法发送消息并返回回复, 会自动维护对话历史。

230511535 杨光裕
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from src.llm import LLMClient


@dataclass
class AgentConfig:
    """Agent配置"""
    name: str                          # 角色名, 如"方案提出者"
    role: str                          # 英文id, 如"proposer"
    personality: str                   # 人格描述
    color: str = "#4a9eff"             # 终端输出颜色(没用上, 留着)


# 预设角色配置
def get_default_agents() -> List[AgentConfig]:
    return [
        AgentConfig(
            name="方案提出者",
            role="proposer",
            personality=(
                "你是一个创意十足的问题解决者。你的职责是: "
                "1) 深入分析问题, 提出2-3个具体可行的方案; "
                "2) 每个方案要说明优缺点; "
                "3) 用数据和逻辑支撑你的论点。"
                "保持专业、客观, 不要模棱两可。"
            ),
        ),
        AgentConfig(
            name="批评者",
            role="critic",
            personality=(
                "你是一个严谨的批判性思考者。你的职责是: "
                "1) 找出上一个方案提出者方案中的漏洞和风险; "
                "2) 质疑其假设, 指出未考虑的边界情况; "
                "3) 提出需要进一步验证的问题。"
                "你不是为了抬杠而抬杠, 你的目标是让方案更完善。"
                "保持理性, 不要人身攻击。每次指出2-3个具体问题。"
            ),
        ),
        AgentConfig(
            name="裁判",
            role="judge",
            personality=(
                "你是一个公正的裁判。你的职责是: "
                "1) 听完双方的论点后, 做出最终判断; "
                "2) 综合双方观点, 给出最优方案; "
                "3) 说明为什么选这个方案, 以及实施时需要注意什么。"
                "你的结论必须有说服力, 不能和稀泥。"
            ),
        ),
    ]


class DebateAgent:
    """辩论参与者"""

    def __init__(self, config: AgentConfig, llm: LLMClient):
        self.config = config
        self.llm = llm
        self._system_prompt = (
            f"你是{config.name}。\n{config.personality}\n"
            "用中文回复。保持简洁, 每次回复不超过300字。"
        )
        self._history: List[Dict[str, str]] = []

    def reset(self):
        """重置对话历史"""
        self._history = []

    def hear(self, speaker: str, message: str):
        """听到别人的发言"""
        self._history.append({"role": "user", "content": f"[{speaker}]: {message}"})

    def speak(self, topic: str = None) -> str:
        """发言"""
        messages = [{"role": "system", "content": self._system_prompt}]

        if topic and not self._history:
            messages.append({
                "role": "user",
                "content": f"请就以下话题发表你的看法:\n\n{topic}",
            })
        else:
            messages.extend(self._history)

        response = self.llm.chat(messages)
        self._history.append({"role": "assistant", "content": response})
        return response

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def role(self) -> str:
        return self.config.role
