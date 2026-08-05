# debate-agents

多Agent辩论系统 -- 3个角色围绕话题辩论, 裁判给出最终裁决。

考研复试项目, Agent方向第1个(难度最低)。

*（2026.08 新建）*

## 怎么工作的

```
用户提出话题
    |
    v
[方案提出者] 分析问题, 提出2-3个方案
    |
    v
[批评者] 找漏洞, 质疑假设, 指出风险
    |
    v
[方案提出者] 回应质疑, 修正方案    <-- 可选多轮
    |
    v
[批评者] 补充质疑
    |
    v
[裁判] 听取双方, 给出最终裁决
```

三个Agent各自有独立的system prompt和对话历史。
发言顺序和轮数由协调器控制。

## 怎么跑

```bash
pip install  # 不需要, 纯标准库+urllib

export OPENAI_API_KEY=sk-xxx
python -m src.main --topic "微服务还是单体架构?"
python -m src.main --topic "要不要学Rust" --rounds 3
python -m src.main --topic "..." --quiet  # 安静模式, 只输出裁决
```

## 配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| OPENAI_API_KEY | (必填) | OpenAI API密钥 |
| OPENAI_BASE_URL | https://api.openai.com/v1 | 兼容API地址 |
| OPENAI_MODEL | gpt-4o-mini | 模型名 |

## 项目结构

```
debate-agents/
  src/
    main.py     入口 + 命令行参数
    llm.py      LLM客户端(urllib, 无第三方依赖)
    agent.py     Agent类, 角色配置, 对话历史
    debate.py   辩论协调器, 发言顺序控制
```

## 角色说明

| 角色 | 职责 |
|------|------|
| 方案提出者 | 深入分析, 提出2-3个方案, 说明优缺点 |
| 批评者 | 找漏洞和风险, 质疑假设 |
| 裁判 | 综合双方观点, 给出最终判断和建议 |

## 技术点

- 纯标准库, 零pip依赖
- OpenAI兼容API(也可以用vLLM/Ollama)
- 每个Agent独立维护对话历史
- 协调器控制发言顺序, 支持多轮辩论
- prompt工程: 角色人格通过system prompt设定

---

230511535 杨光裕 | 2026.08 | 北理工CS考研复试
