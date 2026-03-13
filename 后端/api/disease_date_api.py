import re
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from db.DB import get_db
from models.entity import CaseHistory, Doctor, Logging, Patient
from models.template import DiseaseDateAge, LoginRequest
from services.jwt_depend import create_jwt_token
from services.password_depend import verify_password

router = APIRouter()

DISEASE_KEYS = ("diabetes", "glaucoma", "cataract", "AMD", "hypertension", "myopia", "others")
DISEASE_ALIASES = {
    "diabetes": ("糖尿病", "糖网", "diabetes", "diabetic"),
    "glaucoma": ("青光眼", "glaucoma"),
    "cataract": ("白内障", "cataract"),
    "AMD": ("amd", "黄斑", "macular"),
    "hypertension": ("高血压", "hypertension", "hypertensive"),
    "myopia": ("近视", "病理性近视", "myopia"),
    "others": ("其他", "异常", "other"),
}
DATE_FORMATS = (
    "%Y.%m.%d",
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%Y.%m.%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
)


def build_response(code: int, message: str, data):
    return {"code": code, "message": message, "data": data}


def normalize_text(value: str | None) -> str:
    return str(value or "").strip().lower()


def extract_month(value: str | None) -> int | None:
    text = str(value or "").strip()
    if not text:
        return None

    normalized = (
        text.replace("年", "-")
        .replace("月", "-")
        .replace("日", "")
        .replace(".", "-")
        .replace("/", "-")
    )
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).month
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(normalized).month
    except ValueError:
        pass

    match = re.search(r"^\d{4}-(\d{1,2})", normalized)
    if match:
        month = int(match.group(1))
        if 1 <= month <= 12:
            return month
    return None


def map_outcome_to_key(outcome: str | None) -> str | None:
    normalized = normalize_text(outcome)
    if not normalized or normalized == "正常":
        return None

    for key in DISEASE_KEYS:
        aliases = DISEASE_ALIASES.get(key, ())
        if any(alias in normalized for alias in aliases):
            return key
    return "others"


def build_empty_distribution() -> dict[str, int]:
    return {key: 0 for key in DISEASE_KEYS}


def resolve_age_group(age: int | None, thresholds: list[int]) -> int | None:
    if age is None:
        return None
    if age <= thresholds[0]:
        return 0
    if age <= thresholds[1]:
        return 1
    if age <= thresholds[2]:
        return 2
    if age <= thresholds[3]:
        return 3
    if age <= thresholds[4]:
        return 4
    return 5


@router.get("/getPatientsNum")
async def get_patients_num(db: Session = Depends(get_db)) -> dict:
    statement = select(CaseHistory.time).join(Patient, Patient.reportId == CaseHistory.reportId)
    monthly = [0] * 12

    for (check_time,) in db.execute(statement).all():
        month = extract_month(check_time)
        if month:
            monthly[month - 1] += 1

    return build_response(1, "success", monthly)


@router.get("/getDiseasesDistribution")
async def get_diseases_distribution(db: Session = Depends(get_db)) -> dict:
    statement = select(CaseHistory.outcome).join(Patient, Patient.reportId == CaseHistory.reportId)
    distribution = build_empty_distribution()

    for (outcome,) in db.execute(statement).all():
        key = map_outcome_to_key(outcome)
        if key:
            distribution[key] += 1

    return build_response(1, "success", distribution)


@router.post("/getDiseaseConditionByAge")
async def get_disease_condition_by_age(request: DiseaseDateAge, db: Session = Depends(get_db)) -> dict:
    thresholds = [
        request.firstAge,
        request.secondAge,
        request.thirdAge,
        request.forthAge,
        request.fifthAge,
    ]
    rows = [build_empty_distribution() for _ in range(6)]
    statement = (
        select(Patient.age, CaseHistory.outcome)
        .join(CaseHistory, Patient.reportId == CaseHistory.reportId)
        .order_by(Patient.id.asc())
    )

    for age, outcome in db.execute(statement).all():
        disease_key = map_outcome_to_key(outcome)
        age_index = resolve_age_group(age, thresholds)
        if disease_key is None or age_index is None:
            continue
        rows[age_index][disease_key] += 1

    return build_response(1, "success", rows)


@router.post("/loginByAccount")
async def login_by_account(request: LoginRequest, db: Session = Depends(get_db)) -> dict:
    identifier = request.name.strip()
    if not identifier or not request.password:
        return build_response(0, "Account or password is required", {})

    conditions = [Doctor.name == identifier]
    if identifier.isdigit():
        conditions.append(Doctor.accountId == int(identifier))

    statement = (
        select(Doctor, Logging)
        .join(Logging, Logging.accountId == Doctor.accountId)
        .where(or_(*conditions))
    )
    record = db.execute(statement).first()

    if not record:
        return build_response(0, "Account or password is incorrect", {})

    doctor, login = record
    if not verify_password(request.password, login.password):
        return build_response(0, "Account or password is incorrect", {})

    token = create_jwt_token(doctor.accountId, doctor.name)
    payload = {
        "token": token,
        "accountId": doctor.accountId,
        "name": doctor.name,
    }
    return build_response(1, "success", payload)
