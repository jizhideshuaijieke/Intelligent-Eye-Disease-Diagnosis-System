import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import ai_api, ai_model_api, case_api, disease_date_api, smtp_api, user_api
from core.config import settings
from db.DB import init_db

app = FastAPI(title="Eye Diagnosis Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/health")
def health_check() -> dict:
    return {"code": 1, "message": "success", "data": "ok"}


app.include_router(disease_date_api.router)
app.include_router(case_api.router)
app.include_router(ai_api.router)
app.include_router(smtp_api.router)
app.include_router(ai_model_api.router)
app.include_router(user_api.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
