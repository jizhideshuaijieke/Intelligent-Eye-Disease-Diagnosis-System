import http.client
import json

from core.config import settings


class ai:
    @classmethod
    def _headers(cls):
        if not settings.AI_CHAT_API_KEY:
            raise RuntimeError("AI_CHAT_API_KEY is not configured")
        return {
            "Authorization": f"Bearer {settings.AI_CHAT_API_KEY}",
            "Content-Type": "application/json",
        }

    @classmethod
    def _request_chat(cls, prompt: str) -> str:
        payload = json.dumps(
            {
                "model": settings.AI_CHAT_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
            }
        )
        conn = http.client.HTTPSConnection(settings.AI_CHAT_HOST)
        conn.request("POST", settings.AI_CHAT_PATH, payload, cls._headers())
        raw = conn.getresponse().read().decode("utf-8")
        data = json.loads(raw)
        return data["choices"][0]["message"]["content"]

    @classmethod
    async def call_ai_api(cls, age: int, gender: str, outcome: str) -> str:
        prompt = f"""
        我是一名眼科医生，根据以下患者信息，详细提供诊断建议和治疗流程：
        年龄：{age}，性别：{gender}，
        确诊疾病：{outcome}，
        请提供：
        1. 治疗建议
        2. 检查计划
        3. 用药建议
        """
        return cls._request_chat(prompt)

    @classmethod
    async def get_ai_answer(cls, question: str) -> str:
        prompt = f"""
        请围绕下面问题给出清晰、具体的回答，并按编号输出：
        1. ...
        2. ...
        问题：{question}
        """
        return cls._request_chat(prompt)
