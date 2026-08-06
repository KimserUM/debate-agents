"""
config.py -- 角色配置加载

支持从JSON文件加载自定义角色。
格式:
{
  "roles": [
    {
      "role": "proposer",
      "name": "方案提出者",
      "personality": "...",
      "color": "#4a9eff"
    }
  ],
  "settings": {
    "max_rounds": 2,
    "language": "zh-CN"
  }
}

用法:
  python -m src.main --topic "..." --config my_roles.json

230511535 杨光裕
"""

import json
import os
from typing import List, Dict, Any, Optional
from src.agent import AgentConfig


def load_config(path: str) -> Dict[str, Any]:
    """加载JSON配置文件"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"配置文件不存在: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 校验基本结构
    if "roles" not in data:
        raise ValueError("配置文件缺少 'roles' 字段")

    roles = data["roles"]
    if not isinstance(roles, list) or len(roles) == 0:
        raise ValueError("'roles' 必须是非空数组")

    valid_roles = {"proposer", "critic", "judge"}
    seen = set()
    for r in roles:
        role_id = r.get("role", "")
        if role_id not in valid_roles:
            raise ValueError(
                f"无效角色ID '{role_id}', 必须是 {valid_roles}"
            )
        if role_id in seen:
            raise ValueError(f"角色ID重复: '{role_id}'")
        seen.add(role_id)

    # 补齐缺失角色
    defaults = {
        "proposer": {
            "role": "proposer",
            "name": "方案提出者",
            "personality": "你是一个创意十足的问题解决者。分析问题, 提出2-3个具体方案。",
        },
        "critic": {
            "role": "critic",
            "name": "批评者",
            "personality": "你是一个严谨的批判性思考者。找漏洞和risk, 质疑assumption。",
        },
        "judge": {
            "role": "judge",
            "name": "裁判",
            "personality": "你是一个公正的裁判。综合双方argument, 给出最优方案。",
        },
    }

    for role_id, default in defaults.items():
        if role_id not in seen:
            roles.append(default)

    data["roles"] = roles
    return data


def build_agents_from_config(config: dict) -> List[AgentConfig]:
    """从配置dict构建AgentConfig列表"""
    agents = []
    for r in config["roles"]:
        agents.append(AgentConfig(
            name=r.get("name", r["role"]),
            role=r["role"],
            personality=r.get("personality", ""),
            color=r.get("color", "#4a9eff"),
        ))
    return agents


def save_default_config(path: str):
    """保存默认配置到文件(方便用户修改)"""
    default = {
        "roles": [
            {
                "role": "proposer",
                "name": "方案提出者",
                "personality": (
                    "你是一个创意十足的问题解决者。你的职责是: "
                    "1) 深入分析问题, 提出2-3个具体可行的方案; "
                    "2) 每个方案要说明trade-off; "
                    "3) 用data和logic支撑你的论点。"
                    "保持专业、客观, 不要模棱两可。"
                ),
            },
            {
                "role": "critic",
                "name": "批评者",
                "personality": (
                    "你是一个严谨的批判性思考者。你的职责是: "
                    "1) 找出上一个方案提出者方案中的漏洞和risk; "
                    "2) 质疑其assumption, 指出未考虑的edge case; "
                    "3) 提出需要进一步验证的问题。"
                    "你不是为了抬杠而抬杠, 你的目标是让方案更完善。"
                    "保持理性, 不要人身攻击。每次指出2-3个具体问题。"
                ),
            },
            {
                "role": "judge",
                "name": "裁判",
                "personality": (
                    "你是一个公正的裁判。你的职责是: "
                    "1) 听完双方的argument后, 做出最终判断; "
                    "2) 综合双方观点, 给出最优方案; "
                    "3) 说明为什么选这个方案, 以及implementation时需要注意什么。"
                    "你的结论必须有说服力, 不能和稀泥。"
                ),
            },
        ],
        "settings": {
            "max_rounds": 2,
            "language": "zh-CN",
        },
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(default, f, ensure_ascii=False, indent=2)

    print(f"默认配置已保存到: {path}")


# ---- 测试 ----
if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        # 保存默认配置
        cfg_path = os.path.join(tmp, "default.json")
        save_default_config(cfg_path)

        # 加载
        cfg = load_config(cfg_path)
        print(f"加载到 {len(cfg['roles'])} 个角色:")
        for r in cfg["roles"]:
            print(f"  {r['role']}: {r['name']}")

        # 构建AgentConfig
        agents = build_agents_from_config(cfg)
        print(f"\n构建了 {len(agents)} 个AgentConfig")
        for a in agents:
            print(f"  {a.role}: {a.name}")

        # 测试部分角色(只定义两个, 自动补第三个)
        partial = os.path.join(tmp, "partial.json")
        with open(partial, "w") as f:
            json.dump({
                "roles": [
                    {"role": "proposer", "name": "DBA专家",
                     "personality": "你是数据库专家, 从数据库角度分析。"},
                    {"role": "critic", "name": "安全专家",
                     "personality": "你是安全专家, 从security角度挑刺。"},
                ]
            }, f)

        cfg2 = load_config(partial)
        print(f"\n部分配置补齐后: {[r['name'] for r in cfg2['roles']]}")

    print("\nconfig测试通过")
