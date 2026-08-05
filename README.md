# debate-agents

多Agent辩论系统 -- 3个role围绕topic辩论, judge给出最终verdict。

考研复试项目, Agent方向第1个(难度最低)。

*（2026.08 新建）*

## 怎么work的

```
用户提出topic
    |
    v
[Proposer] 分析问题, 提出2-3个proposal
    |
    v
[Critic] 找漏洞, 质疑assumption, 指出risk
    |
    v
[Proposer] 回应质疑, 修正方案    <-- 可选多轮
    |
    v
[Critic] 补充质疑
    |
    v
[Judge] 听取双方, 给出最终verdict
```

三个Agent各自有独立的system prompt和conversation history。
发言顺序和round数由coordinator控制。

## 怎么跑

```bash
# mock模式, 不需要API key就能看demo
python -m src.main --topic "微服务还是单体?" --mock

# 真调API
export OPENAI_API_KEY=sk-xxx
python -m src.main --topic "微服务还是单体架构?"
python -m src.main --topic "要不要学Rust" --rounds 3
python -m src.main --topic "..." --quiet  # 安静模式, 只输出verdict
python -m src.main --topic "..." --mock --output debate.txt  # 保存到文件
```

## 配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| OPENAI_API_KEY | (mock模式不需要) | OpenAI API key |
| OPENAI_BASE_URL | https://api.openai.com/v1 | 兼容API地址(vLLM/Ollama) |
| OPENAI_MODEL | gpt-4o-mini | 模型名 |

## 项目结构

```
debate-agents/
  src/
    main.py         CLI入口 + args解析
    llm.py          LLM client (urllib, 零pip依赖)
    mock_llm.py     Mock LLM (预设回复, demo用)
    agent.py        Agent类 + role config + history管理
    debate.py       Coordinator, 发言顺序 + round控制
```

## 角色说明

| Role | 职责 |
|------|------|
| Proposer | 深入分析, 提出2-3个proposal, 说明优缺点 |
| Critic | 找漏洞和risk, 质疑assumption |
| Judge | 综合双方观点, 给出最终verdict和建议 |

## 技术点

- 纯标准库, 零pip依赖
- OpenAI compatible API (也可以用vLLM/Ollama)
- 每个Agent独立维护conversation history
- Coordinator控制发言顺序, 支持多round debate
- prompt engineering: role personality通过system prompt设定
- mock mode: 不花API钱也能演示完整debate流程

---

230511535 杨光裕 | 2026.08 | BIT CS 考研复试
