"""
mock_llm.py -- 模拟LLM, 不需要API key也能跑demo

预设了一些回复模板, 不同角色返回不同风格的内容。
用来演示辩论流程, 不需要花钱调API。

用法:
  python -m src.main --topic "xxx" --mock

230511535 杨光裕
"""

import random


# 预设回复库, 按role分类
MOCK_RESPONSES = {
    "proposer": [
        (
            "针对这个话题, 我提出以下方案:\n\n"
            "方案一: 渐进式refactor。好处是risk可控, 可以逐步验证;"
            "缺点是timeline较长, 前期看不到明显ROI。\n\n"
            "方案二: full rewrite。好处是一步到位, architecture更清晰;"
            "缺点是risk集中, 开发周期不好控制。\n\n"
            "建议从方案一开始, 在核心module验证后再决定是否扩大scope。"
        ),
        (
            "回应critic的观点:\n\n"
            "你说的edge case确实存在。但我认为可以通过以下措施来mitigate:\n"
            "1. 加充分的automated test coverage\n"
            "2. 设置canary release阶段, 先在小范围验证\n"
            "3. 准备rollback方案\n\n"
            "方案一的优势在于controllable risk, 这些都在可接受范围内。"
        ),
    ],
    "critic": [
        (
            "我看到了几个问题:\n\n"
            "1. 方案一没有考虑team size。如果只有2-3个人, 维护新旧两套"
            "系统的cost可能超过benefit。\n\n"
            "2. 方案假设了完美的test coverage, 但实际项目中覆盖率通常不足。\n\n"
            "3. 没有说明如果validation失败怎么办——有backup plan吗？"
        ),
        (
            "补充几点质疑:\n\n"
            "1. canary release虽然好, 但如果新旧系统data schema不兼容怎么办？\n\n"
            "2. time cost没有量化——'开发周期不好控制'到底是多久？\n\n"
            "建议在方案中加入具体的time estimation和risk matrix。"
        ),
    ],
    "judge": [
        (
            "听完双方的debate, 我的verdict如下:\n\n"
            "方案一(渐进式refactor)胜出。理由:\n"
            "1. risk可控, 符合engineering best practice\n"
            "2. 可以在过程中持续iterate和调整\n"
            "3. 即使失败, loss也有限\n\n"
            "实施建议:\n"
            "- 先选一个独立module做pilot(预计2周)\n"
            "- pilot成功后制定详细migration plan\n"
            "- 每两周做一次retrospective, 评估是否继续\n"
            "- 保留rollback能力至少到migration完成后1个月"
        ),
    ],
}


class MockLLM:
    """模拟LLM, 返回预设回复"""

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
        self._call_count = 0

    def chat(self, messages: list,
             temperature: float = None,
             max_tokens: int = None) -> str:
        """
        根据messages里最后一次assistant或user内容判断角色,
        返回对应预设回复。
        """
        self._call_count += 1

        # 从system prompt推断角色
        system_msg = ""
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
                break

        if "提出者" in system_msg or "proposer" in system_msg:
            role = "proposer"
        elif "批评者" in system_msg or "critic" in system_msg:
            role = "critic"
        elif "裁判" in system_msg or "judge" in system_msg:
            role = "judge"
        else:
            # 看最后一条user消息来判断
            role = "proposer"
            last_user = ""
            for m in reversed(messages):
                if m["role"] == "user":
                    last_user = m["content"]
                    break
            if "裁决" in last_user or "判断" in last_user:
                role = "judge"
            elif "质疑" in last_user or "批评" in last_user:
                role = "critic"

        responses = MOCK_RESPONSES.get(role, MOCK_RESPONSES["proposer"])
        idx = (self._call_count - 1) % len(responses)
        return responses[idx]
