# app/schemas/audio.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class AudioOut(BaseModel):
    word_id: int
    audio_type: str
    format: str
    path: str
    duration_secs: Optional[float] = None
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)