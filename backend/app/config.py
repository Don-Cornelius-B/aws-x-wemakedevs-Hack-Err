import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENSEARCH_HOST: str = os.getenv("OPENSEARCH_HOST", "http://localhost:9200")
    LOCALSTACK_ENDPOINT: str = os.getenv("LOCALSTACK_ENDPOINT", "http://localhost:4566")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "ner-landslide-guard-secret-key-for-local-dev")
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
