import logging

from core.config import settings
from db.DB import get_db
from models.entity import *
from fastapi import APIRouter, Depends
from models.template import TokenRequest, DiseaseDateAge, LoginRequest
from services.jwt_depend import create_jwt_token, decode_jwt_token
from sqlalchemy.orm import Session

router = APIRouter()


@router.get('/getPatientsNum')
async def disease_date(db: Session = Depends(get_db)) -> dict:
    # payload = decode_jwt_token(request.token)
    # if not payload:
    #     return {
    #         "code": 0,
    #         "message": "token验证失败",
    #         "data": ""
    #     }
    try:
        result = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        mouth_data = db.query(Paients.time).all()
        for data in mouth_data:
            if data[0]:
                # mouth_time = data[0].sqlit(".")[1]
                mouth_time = data[0]
                result[int(mouth_time.split(".")[1])-1] += 1

        response = {
            "code": 1,
            "message": "成功获取数据",
            "data": result
        }
        # logging.info(response)
    except Exception as e:
        response = {
            "code": 0,
            "message": "获取数据失败",
            "data": str(e)
        }
        # logging.error("Error:获取月份患病人数失败",response)
    return response


@router.get('/getDiseasesDistribution')
async def disease_dirtribution(db: Session = Depends(get_db)) -> dict:
    # payload = decode_jwt_token(request.token)
    # if not payload:
    #     return {
    #         "code": 0,
    #         "message": "token验证失败",
    #         "data": ""
    #     }
    try:
        result = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        outcomes = db.query(Paients.outCome).all()
        for outcome in outcomes:
            if outcome[0]:
                # print(outcome[0])
                if outcome[0] >= 10:
                    result[1] += 1
                else:
                    result[outcome[0]] += 1

        data = {
            "diabetes": result[1],
            "glaucoma": result[2],
            "cataract": result[3],
            "AMD": result[4],
            "hypertension": result[5],
            "myopia": result[6],
            "others": result[7]
        }

        response = {
            "code": 1,
            "message": "成功获取数据",
            "data": data
        }
        logging.info(response)
    except Exception as e:
        response = {
            "code": 0,
            "message": "获取数据失败",
            "data": str(e)
        }
        # logging.error("Error:获取疾病分布失败", response)
    return response


@router.post('/getDiseaseConditionByAge')
async def disease_date(request: DiseaseDateAge, db: Session = Depends(get_db)) -> dict:
    # payload = decode_jwt_token(request.token)
    # if not payload:
    #     return {
    #         "code": 0,
    #         "message": "token验证失败",
    #         "data": ""
    #     }
    try:
        result = [[0 for _ in range(9)] for _ in range(7)]
        # print(result)

        outcomes = db.query(Paients.outCome, Paients.age).all()
        # print(outcomes)
        for outcome in outcomes:
            if outcome[0] and outcome[1]:
                # print(outcome)
                if 10 <= outcome[0]:
                    if outcome[1] <= request.firstAge:
                        result[1][1] += 1
                    elif request.firstAge < outcome[1] <= request.secondAge:
                        result[2][1] += 1
                    elif request.secondAge < outcome[1] <= request.thirdAge:
                        result[3][1] += 1
                    elif request.thirdAge < outcome[1] <= request.forthAge:
                        result[4][1] += 1
                    elif request.forthAge < outcome[1] <= request.fifthAge:
                        result[5][1] += 1
                    else:
                        result[6][1] += 1
                else:
                    if outcome[1] <= request.firstAge:
                        result[1][outcome[0]] += 1
                    elif request.firstAge < outcome[1] <= request.secondAge:
                        result[2][outcome[0]] += 1
                    elif request.secondAge < outcome[1] <= request.thirdAge:
                        result[3][outcome[0]] += 1
                    elif request.thirdAge < outcome[1] <= request.forthAge:
                        result[4][outcome[0]] += 1
                    elif request.forthAge < outcome[1] <= request.fifthAge:
                        result[5][outcome[0]] += 1
                    else:
                        result[6][outcome[0]] += 1
            else:
                continue

        # logging.info(result)
        keys = ["diabetes", "glaucoma", "cataract", "AMD", "hypertension", "myopia", "others"]
        data = []
        for i in range(1, 7):  # 行索引 1~7
            row = result[i]
            entry = {
                keys[0]: row[1],
                keys[1]: row[2],
                keys[2]: row[3],
                keys[3]: row[4],
                keys[4]: row[5],
                keys[5]: row[6],
            }
            data.append(entry)
        # print(data)
        response = {
            "code": 1,
            "message": "成功获取数据",
            "data": data
        }
        # logging.info(response)
    except Exception as e:
        response = {
            "code": 0,
            "message": "获取数据失败",
            "data": str(e)
        }
        logging.error("Error:获取疾病分布失败", response)
    return response


@router.post('/loginByAccount')
async def get_token(request: LoginRequest, db: Session = Depends(get_db)) -> dict:
    # 这里可以根据账号密码进行登录验证，并返回token
    # 这里暂时返回一个测试token
    # 实际项目中，token应该由服务端生成，并返回给客户端，客户端需要将token存储在本地，并在每次请求时附带上
    name = request.name
    password = request.password
    Name, Password = db.query(User.name, User.password).filter(User.name == name).first()
    token = create_jwt_token(name, password)
    if Password == password:
        response = {
            "code": 1,
            "message": "登录成功",
            "data": {
                "token": token
            }
        }
        # print(decode_jwt_token(token))
    else:
        response = {
            "code": 0,
            "message": "用户名或密码错误",
            "data": {}
        }
    return response


