"""M4 文案生成 - LLM服务（Ollama本地推理封装）

使用 deepseek-r1:7b 通过 Ollama API 进行文案生成。
回退方案：当 Ollama 不可用时使用 Mock 生成。
"""

from __future__ import annotations
import json
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "deepseek-r1:7b"
FALLBACK_MODEL = "starcoder2:3b"


class LLMService:
    """LLM推理服务 - 封装Ollama API"""

    def __init__(self):
        self._available = False
        self._model_available = False
        self._check_availability()
        if self._available:
            self._check_model()

    def _check_availability(self) -> bool:
        """检查Ollama是否运行"""
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags")
            urllib.request.urlopen(req, timeout=1)
            self._available = True
        except Exception:
            self._available = False
        return self._available

    def _check_model(self) -> bool:
        """检查模型是否可响应（短超时）"""
        try:
            payload = json.dumps({"model": MODEL_NAME, "prompt": "ping", "stream": False, "options": {"num_predict": 1}}).encode()
            req = urllib.request.Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=5)
            self._model_available = True
        except Exception:
            self._model_available = False
            self._available = False  # 禁用LLM
            print(f"LLM: Model {MODEL_NAME} not responding (fallback to mock)")
        return self._model_available

    @property
    def available(self) -> bool:
        return self._available and self._model_available

    def generate(self, prompt: str, system_prompt: str = "", max_tokens: int = 512) -> str | None:
        """调用Ollama生成文本"""
        if not self._available:
            return None

        payload = json.dumps({
            "model": MODEL_NAME,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9,
            }
        }).encode()

        try:
            req = urllib.request.Request(
                OLLAMA_URL,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read())
                return result.get("response", "")
        except Exception as e:
            print(f"LLM Error: {e}")
            return None

    def generate_stream(self, prompt: str, system_prompt: str = ""):
        """流式生成（返回逐行响应）"""
        if not self._available:
            yield None
            return

        payload = json.dumps({
            "model": MODEL_NAME,
            "prompt": prompt,
            "system": system_prompt,
            "stream": True,
            "options": {"temperature": 0.7, "num_predict": 2048},
        }).encode()

        try:
            req = urllib.request.Request(
                OLLAMA_URL, data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                for line in resp:
                    if line:
                        data = json.loads(line)
                        yield data.get("response", "")
                        if data.get("done"):
                            break
        except Exception:
            yield None


llm_service = LLMService()
