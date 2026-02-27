from pydantic import BaseModel


class TokenRequest(BaseModel):
    token: str


class LoginRequest(BaseModel):
    name: str
    password: str


class QuestionRequest(BaseModel):
    question: str


class Question2Request(BaseModel):
    age: int
    gender: str
    outcome: str


class DiseaseDateAge(BaseModel):
    # token: str
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

