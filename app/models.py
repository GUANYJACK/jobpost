from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    job_title: Optional[str]
    company_name: Optional[str]
    salary: Optional[str]
    location: Optional[str]
    compensation: Optional[str]
    jd_text: Optional[str]
    status: str = "Scraped"
    applied_at: Optional[datetime]
    tailored_resume_text: Optional[str]
    final_cover_letter_text: Optional[str]
