"""
mock_llm.py -- 模拟LLM, 不需要API key也能跑demo

预设了一些回复模板, 不同角色返回不同风格的内容。
用来演示辩论流程, 不需要花钱调API。

用法:
  python -m src.main --topic "xxx" --mock

230511535 杨光裕
"""

import random


# 预设回复库, 按角色分类
MOCK_RESPONSES = {
    "proposer": [
        (
            "针对这个话题，我提出以下方案：\n\n"
            "方案一：采用渐进式重构。好处是风险小，可以逐步验证；"
            "缺点是周期较长，前期看不到明显收益。\n\n"
            "方案二：整体重写。好处是一步到位，架构更清晰；"
            "缺点是风险集中，开发周期不好控制。\n\n"
            "建议从方案一开始，在关键模块验证后再决定是否扩大范围。"
        ),
        (
            "回应批评者的观点：\n\n"
            "你说的边界情况确实存在。但我认为可以通过以下措施来缓解：\n"
            "1. 加充分的自动化测试覆盖\n"
            "2. 设置灰度发布阶段，先在小范围验证\n"
            "3. 准备回滚方案\n\n"
            "方案一的优势在于可控性，这些风险都在可接受范围内。"
        ),
    ],
    "critic": [
        (
            "我看到了几个问题：\n\n"
            "1. 方案一没有考虑团队规模。如果只有2-3个人，维护新旧两套系统的成本可能超过收益。\n\n"
            "2. 方案假设了完美的测试覆盖，但实际项目中测试覆盖率通常不足。\n\n"
            "3. 没有说明如果验证失败怎么办——有备选方案吗？"
        ),
        (
            "补充几点质疑：\n\n"
            "1. 灰度发布虽然好，但如果新旧系统数据不兼容怎么办？\n\n"
            "2. 时间成本没有量化——'开发周期不好控制'到底是多少？\n\n"
            "建议在方案中加入具体的时间估算和风险矩阵。"
        ),
    ],
    "judge": [
        (
            "听完双方的辩论，我的裁决如下：\n\n"
            "方案一（渐进式重构）胜出。理由：\n"
            "1. 风险可控，符合工程实践\n"
            "2. 可以在过程中持续学习和调整\n"
            "3. 即使失败，损失也有限\n\n"
            "实施建议：\n"
            "- 先选一个独立模块做试点（预计2周）\n"
            "- 试点成功后制定详细迁移计划\n"
            "- 每两周做一次回顾，评估是否继续\n"
            "- 保留回滚能力至少到迁移完成后1个月"
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
