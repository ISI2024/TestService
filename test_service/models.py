from test_service.database import Base
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Boolean


class Users(Base):
    __tablename__ = "users"

    login = Column(String, primary_key=True)
    wallet = Column(Float, nullable=False)
    email = Column(String, nullable=False)


class ExaminationResult(Base):
    __tablename__ = "examinations_results"

    id = Column(Integer, primary_key=True)
    examination_date = Column(String, nullable=True)
    analyzer = Column(String, nullable=True)
    fk_user = Column(String, ForeignKey('users.login'), nullable=False)
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
