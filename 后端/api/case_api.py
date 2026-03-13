from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from db.DB import get_db
from models.entity import CaseHistory, Patient
from models.template import CaseRecordRequest

router = APIRouter()


def build_response(code: int, message: str, data):
    return {"code": code, "message": message, "data": data}


def get_next_patient_id(db: Session) -> int:
    max_id = db.execute(select(func.max(Patient.id))).scalar()
    return (max_id or 0) + 1


@router.post("/saveCaseHistory")
def save_case_history(request: CaseRecordRequest, db: Session = Depends(get_db)) -> dict:
    report_id = request.reportId.strip()
    if not report_id:
        return build_response(0, "reportId is required", {})

    case_history = db.get(CaseHistory, report_id)
    if case_history is None:
        case_history = CaseHistory(reportId=report_id)
        db.add(case_history)

    case_history.time = request.time
    case_history.outcome = request.outcome
    case_history.leftPhoto = request.leftPhoto
    case_history.rightPhoto = request.rightPhoto
    case_history.aiSuggestion = request.aiSuggestion

    patient = db.execute(select(Patient).where(Patient.reportId == report_id)).scalar_one_or_none()
    if patient is None:
        patient = Patient(
            id=request.patientId or get_next_patient_id(db),
            reportId=report_id,
        )
        db.add(patient)

    patient.name = request.name
    patient.gender = request.gender
    patient.age = request.age

    db.commit()

    return build_response(
        1,
        "success",
        {
            "patientId": patient.id,
            "reportId": case_history.reportId,
        },
    )


@router.get("/getCaseHistory/{report_id}")
def get_case_history(report_id: str, db: Session = Depends(get_db)) -> dict:
    statement = (
        select(Patient, CaseHistory)
        .join(CaseHistory, Patient.reportId == CaseHistory.reportId)
        .where(Patient.reportId == report_id)
    )
    record = db.execute(statement).first()
    if not record:
        return build_response(0, "Case not found", {})

    patient, case_history = record
    data = {
        "patientId": patient.id,
        "name": patient.name,
        "gender": patient.gender,
        "age": patient.age,
        "reportId": case_history.reportId,
        "time": case_history.time,
        "outcome": case_history.outcome,
        "leftPhoto": case_history.leftPhoto,
        "rightPhoto": case_history.rightPhoto,
        "aiSuggestion": case_history.aiSuggestion,
    }
    return build_response(1, "success", data)
