from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Resume(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None)
    resume_text: str
    adjusted_text: Optional[str]
    updated_at: Optional[datetime]
    file_path: Optional[str]
    original_filename: Optional[str]

# Application模型保持不变
