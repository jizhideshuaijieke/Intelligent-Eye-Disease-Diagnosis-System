from db.DB import get_db
from models.entity import *
from models.template import TokenRequest
from services.jwt_depend import decode_jwt_token

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/getPersonalInform")
def get_users(token: TokenRequest, db: Session = Depends(get_db)):
    user_id = decode_jwt_token(token.token).get("user_id")
    user = db.query(
        User.name, User.accountId, User.gender, User.age, User.department, User.email, User.phone
    ).filter(User.name == user_id).first()
    if user:
        name, accountid, gender, age, department, email, phone = user

    response = {
        "code": 0,
        "message": "获取信息成功",
        "data": {
            "name": name,
            "accountId": accountid,
            "gender": gender,
            "age": age,
            "department": department,
            "email": email,
            "phone": phone
        }
    }
    return response
