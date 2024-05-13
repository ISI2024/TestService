from pydantic import BaseModel
from typing import Optional


class Examination(BaseModel):
    id: int | None
    examination_date: str | None
    leukocytes: str | None
    nitrite: str | None
    urobilinogen: str | None
    protein: str | None
    ph: str | None
    blood: str | None
    specific_gravity: str | None
    ascorbate: str | None
    ketone: str | None
    bilirubin: str | None
    glucose: str | None
    micro_albumin: str | None


# -----


class AnalyzerCommand(BaseModel):
    id: int
    user_login: Optional[str]
