from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import computed_field
from urllib.parse import quote_plus

load_dotenv()

class Settings(BaseSettings):
    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    S3_BUCKET_NAME: str

    # Qdrant
    QDRANT_API_KEY: str
    QDRANT_URL: str

    # PostgreSQL
    DB_NAME: str
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str

    # Auth / JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # OpenAI
    OPENAI_API_KEY: str

    @computed_field
    @property
    def DB_URL(self) -> str:
        db_pass = quote_plus(self.DB_PASS)
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{db_pass}"
            f"@{self.DB_HOST}:{self.DB_PORT}"
            f"/{self.DB_NAME}"
        )

settings = Settings()