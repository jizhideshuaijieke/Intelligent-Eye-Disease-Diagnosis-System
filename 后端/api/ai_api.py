import logging

from db.DB import get_db
from fastapi import APIRouter, Depends
from models.template import TokenRequest, QuestionRequest, Question2Request
from models.entity import *
from services.ai_depend import ai
from services.jwt_depend import decode_jwt_token
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/aiSuggestion")
async def predict(request: Question2Request) -> dict:
    # payload = decode_jwt_token(request.token)
    # if not payload:
    #     return {
    #         "code": 0,
    #         "message": "token验证失败",
    #         "data": ""
    #     }

    try:
        logging.info("AI suggestion API called")
        ai_suggestion = await ai.call_ai_api(request.age, request.gender, request.outcome)
        logging.info(f"Received request for AI suggestion ")
        response = {
            "code": 1,
            "message": "成功获取ai建议",
            "data": ai_suggestion
        }
        return response
    except Exception as e:
        logging.error(f"Error while processing AI suggestion request: {e}")
        return {
            "code": 0,
            "message": "服务器错误",
            "data": e
        }


@router.post("/aiQuestion")
async def answer(request: QuestionRequest):
    try:
        logging.info("AI answer API called")
        ai_answer = await ai.get_ai_answer(request.question)
        return {
            "code": 1,
            "message": "成功获取ai答案",
            "data": ai_answer
        }

    except Exception as e:
        logging.error(f"Error while processing AI answer request: {e}")
        return {
            "code": 0,
            "message": "服务器错误",
            "data": e
        }
