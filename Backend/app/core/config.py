from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Gemini
    gemini_api_key: Optional[str] = None
    gemini_model_name: str = "gemini-2.0-flash"

    # OpenAI = ...

    # Diretórios e arquivos
    media_dir: str = r"media"
    input_csv_dir: str = r"inputcsvs" # para carregar uma 
    database_url: str

    # Chave secreta para assinar os JWTs.
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "uma-chave-secreta-muito-forte-para-desenvolvimento"

    ANKI_MODEL_ID: int = 1607392319

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

