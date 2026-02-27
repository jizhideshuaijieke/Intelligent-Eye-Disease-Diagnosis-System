import uvicorn

from api import disease_date_api, ai_api, smtp_api, ai_model_api, user_api
from fastapi import FastAPI
from core.config import settings
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


app.include_router(disease_date_api.router)
app.include_router(ai_api.router)
app.include_router(smtp_api.router)
app.include_router(ai_model_api.router)
app.include_router(user_api.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
