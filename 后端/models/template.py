from pydantic import BaseModel, ConfigDict, Field


class TokenRequest(BaseModel):
    token: str


class LoginRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(alias="username")
    password: str


class RegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(alias="username")
    password: str
    email: str | None = None
    phone: str | None = None


class UpdatePersonalInfoRequest(BaseModel):
    token: str
    name: str | None = None
    gender: str | None = None
    age: int | None = None
    department: str | None = None
    email: str | None = None
    phone: str | None = None
    photo: str | None = None


class ChangePasswordRequest(BaseModel):
    token: str
    oldPassword: str
    newPassword: str


class CaseRecordRequest(BaseModel):
    patientId: int | None = None
    name: str
    gender: str | None = None
    age: int | None = None
    reportId: str
    time: str | None = None
    outcome: str | None = None
    leftPhoto: str | None = None
    rightPhoto: str | None = None
    aiSuggestion: str | None = None


class QuestionRequest(BaseModel):
    question: str


class Question2Request(BaseModel):
    age: int
    gender: str
    outcome: str


class DiseaseDateAge(BaseModel):
    firstAge: int
    secondAge: int
    thirdAge: int
    forthAge: int
    fifthAge: int


class DiseaseDate(BaseModel):
    index: int
    name: str
    path: str
    probabilities: list[dict]
