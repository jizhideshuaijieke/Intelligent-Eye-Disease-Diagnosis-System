from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # mysql config
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "change_me"
    MYSQL_DB: str = "eye_diagnosis_system_db"
    DATABASE_URL: str = ""

    # fastapi config
    HOST: str = "0.0.0.0"
    PORT: int = 8800

    # QQsmpt config
    MAIL_HOST: str = "smtp.qq.com"
    MAIL_PORT: int = 465
    MAIL_USER: str = "your_email@qq.com"
    MAIL_PASSWORD: str = "your_smtp_auth_code"

    # model service config
    AI_MODEL_URL: str = "http://127.0.0.1:5000"

    # ai chat service config
    AI_CHAT_API_KEY: str = ""
    AI_CHAT_HOST: str = "api.chatanywhere.tech"
    AI_CHAT_PATH: str = "/v1/chat/completions"
    AI_CHAT_MODEL: str = "gpt-3.5-turbo"

    # jwt config
    JWT_SECRET_KEY: str = "please_change_this_in_env"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 7

    # redis config
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = ""

    @model_validator(mode="after")
    def build_urls(self):
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
                f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
            )
        if not self.REDIS_URL:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return self


settings = Settings()
