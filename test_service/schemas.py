from datetime import datetime
from pydantic import BaseModel


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
