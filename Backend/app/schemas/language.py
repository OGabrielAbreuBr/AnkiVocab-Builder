# app/schemas/language.py
from pydantic import BaseModel, ConfigDict

class LanguageOut(BaseModel):
    id: int
    code: str
    name: str

    model_config = ConfigDict(from_attributes=True)
