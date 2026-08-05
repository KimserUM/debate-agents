"""
llm.py -- LLM客户端(轻量版)

用urllib直接调OpenAI兼容API, 不依赖第三方SDK。
环境变量 OPENAI_API_KEY 或传参设置key。

230511535 杨光裕
"""

import json
import os
import urllib.request
import urllib.error
from typing import List, Dict


class LLMClient:
    """OpenAI兼容的LLM客户端"""

    def __init__(self,
                 api_key: str = None,
                 base_url: str = "https://api.openai.com/v1",
                 model: str = "gpt-4o-mini",
                 max_tokens: int = 1024,
                 temperature: float = 0.7):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def chat(self, messages: List[Dict[str, str]],
             temperature: float = None,
             max_tokens: int = None) -> str:
        """发送对话, 返回文本回复"""
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
        }

        url = self.base_url + "/chat/completions"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        req = urllib.request.Request(url, data=body, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"API错误 {e.code}: {err[:300]}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"连接失败: {e.reason}")
