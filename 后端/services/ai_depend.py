import http.client
import json
import re


class ai:
    api_key = "sk-xNoKJZg0BcyKLcWlqYOzE0VM2nhvrqUXnngz63P4Oaf3dapj"
    # gpt api
    api_url = "https://api.chatanywhere.com.cn"
    headers = {
        'Authorization': f"Bearer {api_key}",
        'Content-Type': 'application/json'
    }
    conn = http.client.HTTPSConnection("api.chatanywhere.tech")

    @classmethod
    async def call_ai_api(self, age: int, gender: str, outcome: str) -> str:
        """
        调用大模型API，获取诊断建议
        """

        prompt = f"""
        我是一名眼科医生，根据以下患者信息，详细提供提供诊断建议和治疗流程：
        年龄：{age}，性别：{gender},
        确诊疾病：{outcome},
        请提供：
        ###1. 治疗建议
        ###2. 检查计划
        ###3. 用药建议
        """

        payload = json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        self.conn.request("POST", "/v1/chat/completions", payload, self.headers)
        data = json.loads(self.conn.getresponse().read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        # result = re.sub(r'(\d+\.)', r'###\1', content)
        return content

    @classmethod
    async def get_ai_answer(self, question: str) -> str:
        """
        获取AI模型的诊断建议
        """

        prompt = f"""
        请关于我下面的提问进行回答，要求回答具体清晰准确,并按照下面的格式进行回复,请回复详细一点
        1. answer...
        2. answer...
        ...
        下面我将开始提问
        {question},请问怎么解决？
        """
        payload = json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        self.conn.request("POST", "/v1/chat/completions", payload, self.headers)
        data = json.loads(self.conn.getresponse().read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        # result = re.sub(r'\d\.', r'###\d\.', content)
        return content
