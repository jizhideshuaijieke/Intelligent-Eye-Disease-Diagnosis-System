import logging

import jwt

from core.config import settings
from datetime import datetime, timedelta


def create_jwt_token(user_id: int, username: str) -> str:
    # 定义 payload
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)  # 设置过期时间
    }
    # 生成 JWT
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logging.info("令牌过期")
    except jwt.InvalidTokenError:
        logging.info("无效的令牌")