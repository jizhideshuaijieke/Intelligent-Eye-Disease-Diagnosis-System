import requests

from core.config import settings


def get_model_prediction(model_endpoint):
    """
    请求获取 AI 大模型的诊断结果。
    """
    try:
        response = requests.get(model_endpoint)

        if response.status_code == 200:
            # 解析 JSON 数据
            result = response.json()
            print("Model prediction received:", result)
            return result
        else:
            # 打印错误信息
            print(f"Error: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        # 捕获所有 requests 库的异常（如连接错误、超时等）
        print(f"Request failed: {e}")
        return None


