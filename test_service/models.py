from rest_api.database import Base
from sqlalchemy import Column, BigInteger, String, Date
from datetime import date


class ExaminationResult(Base):
    __tablename__ = "examinations_results"

    id = Column(BigInteger, primary_key=True)
    examination_date = Column(Date, nullable=True)
    fk_analyzer = Column(BigInteger, nullable=True)
    fk_user = Column(BigInteger, nullable=True)
    leukocytes = Column(String, nullable=True)
    nitrite = Column(String, nullable=True)
    urobilinogen = Column(String, nullable=True)
    protein = Column(String, nullable=True)
    ph = Column(String, nullable=True)
    blood = Column(String, nullable=True)
    specific_gravity = Column(String, nullable=True)
    ascorbate = Column(String, nullable=True)
    ketone = Column(String, nullable=True)
    bilirubin = Column(String, nullable=True)
    glucose = Column(String, nullable=True)
    micro_albumin = Column(String, nullable=True)

    def __init__(self, examination_date: date, fk_analyzer: int, fk_user: int, leukocytes: str | None,
                 nitrite: str | None, urobilinogen: str | None, protein: str | None, ph: str | None,
                 blood: str | None, specific_gravity: str | None, ascorbate: str | None, ketone: str | None,
                 bilirubin: str | None, glucose: str | None, micro_albumin: str | None):
        self.examination_date = examination_date
        self.fk_analyzer = fk_analyzer
        self.fk_user = fk_user
        self.leukocytes = leukocytes
        self.nitrite = nitrite
        self.urobilinogen = urobilinogen
        self.protein = protein
        self.ph = ph
        self.blood = blood
        self.specific_gravity = specific_gravity
        self.ascorbate = ascorbate
        self.ketone = ketone
        self.bilirubin = bilirubin
        self.glucose = glucose
        self.micro_albumin = micro_albumin


class Files(Base):
    __tablename__ = "files"

    id = Column(BigInteger, primary_key=True)
    fk_user = Column(BigInteger, nullable=False)
    fk_analyzer = Column(BigInteger, nullable=False)
    absolute_path = Column(String, nullable=False)
    fk_format = Column(String, nullable=False)
    fk_type = Column(String, nullable=False)

    def __init__(self, fk_user: int, fk_analyzer: int, absolute_path: str, fk_format: str,
                 fk_type: str) -> None:
        self.fk_user = fk_user
        self.fk_analyzer = fk_analyzer
        self.absolute_path = absolute_path
        self.fk_format = fk_format
        self.fk_type = fk_type
