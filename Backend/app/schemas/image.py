# app/schemas/image.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ImageOut(BaseModel):
    word_id: int
    image_type: str
    path: str
    format: str
    creator: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

