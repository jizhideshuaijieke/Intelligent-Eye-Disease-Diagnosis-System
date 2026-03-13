from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from db.DB import get_db
from models.entity import Doctor, Logging
from models.template import (
    ChangePasswordRequest,
    RegisterRequest,
    TokenRequest,
    UpdatePersonalInfoRequest,
)
from services.jwt_depend import decode_jwt_token
from services.password_depend import hash_password, verify_password

router = APIRouter()


def build_response(code: int, message: str, data):
    return {"code": code, "message": message, "data": data}


def resolve_account_id(token: str) -> int | None:
    payload = decode_jwt_token(token)
    if not payload:
        return None
    account_id = payload.get("account_id", payload.get("user_id"))
    return int(account_id) if account_id is not None else None


def get_next_account_id(db: Session) -> int:
    max_id = db.execute(select(func.max(Doctor.accountId))).scalar()
    return (max_id or 100000) + 1


def build_profile_payload(doctor: Doctor, login: Logging) -> dict:
    return {
        "name": doctor.name,
        "accountId": doctor.accountId,
        "gender": doctor.gender,
        "age": doctor.age,
        "department": doctor.department,
        "email": login.email,
        "phone": login.phone,
        "photo": doctor.photo,
    }


@router.post("/registerByAccount")
def register_by_account(request: RegisterRequest, db: Session = Depends(get_db)) -> dict:
    username = request.name.strip()
    if not username or not request.password:
        return build_response(0, "Username and password are required", {})

    exists = db.execute(select(Doctor.accountId).where(Doctor.name == username)).first()
    if exists:
        return build_response(0, "Username already exists", {})

    account_id = get_next_account_id(db)
    doctor = Doctor(accountId=account_id, name=username)
    login = Logging(
        accountId=account_id,
        email=request.email,
        phone=request.phone,
        password=hash_password(request.password),
    )

    db.add(doctor)
    db.add(login)
    db.commit()

    return build_response(
        1,
        "success",
        {"accountId": account_id, "name": username},
    )


@router.post("/getPersonalInform")
def get_personal_information(request: TokenRequest, db: Session = Depends(get_db)) -> dict:
    account_id = resolve_account_id(request.token)
    if account_id is None:
        return build_response(0, "Invalid token", {})

    statement = (
        select(Doctor, Logging)
        .join(Logging, Logging.accountId == Doctor.accountId)
        .where(Doctor.accountId == account_id)
    )
    record = db.execute(statement).first()
    if not record:
        return build_response(0, "User not found", {})

    doctor, login = record
    return build_response(1, "success", build_profile_payload(doctor, login))


@router.post("/updatePersonalInform")
def update_personal_information(request: UpdatePersonalInfoRequest, db: Session = Depends(get_db)) -> dict:
    account_id = resolve_account_id(request.token)
    if account_id is None:
        return build_response(0, "Invalid token", {})

    statement = (
        select(Doctor, Logging)
        .join(Logging, Logging.accountId == Doctor.accountId)
        .where(Doctor.accountId == account_id)
    )
    record = db.execute(statement).first()
    if not record:
        return build_response(0, "User not found", {})

    doctor, login = record
    doctor.name = request.name if request.name is not None else doctor.name
    doctor.gender = request.gender if request.gender is not None else doctor.gender
    doctor.age = request.age if request.age is not None else doctor.age
    doctor.department = request.department if request.department is not None else doctor.department
    doctor.photo = request.photo if request.photo is not None else doctor.photo
    login.email = request.email if request.email is not None else login.email
    login.phone = request.phone if request.phone is not None else login.phone

    db.commit()
    db.refresh(doctor)
    db.refresh(login)

    return build_response(1, "success", build_profile_payload(doctor, login))


@router.post("/changePassword")
def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db)) -> dict:
    account_id = resolve_account_id(request.token)
    if account_id is None:
        return build_response(0, "Invalid token", {})

    login = db.get(Logging, account_id)
    if not login:
        return build_response(0, "User not found", {})

    if not verify_password(request.oldPassword, login.password):
        return build_response(0, "Original password is incorrect", {})

    login.password = hash_password(request.newPassword)
    db.commit()

    return build_response(1, "success", {})
