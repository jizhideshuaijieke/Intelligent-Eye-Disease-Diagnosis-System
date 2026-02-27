import logging

from fastapi import APIRouter
from services.QQsmtp_depend import Email

router = APIRouter()


@router.post('/sendEmail')
async def send_email(account: str):
    try:
        flag = await Email.sendEmail(account)
        if flag:
            response = {
                "code": 1,
                "message": "成功发送邮箱验证码",
                "data": ""
            }
            return response
        else:
            response = {
                "code": 0,
                "message": "发送失败，详情见日志",
                "data": ""
            }
            return response
    except Exception as e:
        response = {
            "code": 0,
            "message": "发送失败，详情见日志",
            "data": ""
        }
        logging.error(f"Error: {e}")
        return response

