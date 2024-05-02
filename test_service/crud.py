from datetime import datetime
from operator import and_
from typing import Optional
from sqlalchemy.orm import Session
from rest_api.common.analyzer.models import AllowedExaminations, Analyzer
from rest_api.common.research.models import ExaminationResult, Files
from rest_api.common.users.models import User
from rest_api.common.research.shemas import Examination, MyFile, NewFile


def check_if_analyzer_available(analyzer_id: int, db: Session) -> bool:
    res: Optional[Analyzer] = db.query(Analyzer).filter(Analyzer.id == analyzer_id).first()

    if res is None:
        return False

    elif not res.is_usable:
        return False

    return True


def create_allowed_examination(user_id: int, analyzer_id: int, db: Session) -> None:
    allowed_examination: AllowedExaminations = AllowedExaminations(fk_user=user_id, fk_analyzer=analyzer_id)

    db.add(allowed_examination)
    db.commit()


def read_allowed_examination(user_id: int, db: Session) -> Optional[tuple[int, int, str]]:
    allowed_examination = db.query(AllowedExaminations.fk_user, AllowedExaminations.fk_analyzer,
                                   Analyzer.code).join(Analyzer,
                                                       Analyzer.id == AllowedExaminations.fk_analyzer).filter(
                                                           AllowedExaminations.fk_user == user_id).first()
    return allowed_examination


def delete_allowed_examination(user_id: int, analyzer_id: int, db: Session) -> None:
    user: Optional[AllowedExaminations] = db.query(AllowedExaminations).filter(
        and_(AllowedExaminations.fk_user == user_id, AllowedExaminations.fk_analyzer == analyzer_id)).first()

    db.delete(user)
    db.commit()


def create_file(new_file: NewFile, db: Session) -> None:
    file: Files = Files(fk_user=new_file.fk_user,
                        fk_analyzer=new_file.fk_analyzer,
                        absolute_path=new_file.absolute_path,
                        fk_format=new_file.fk_format.value,
                        fk_type=new_file.fk_type.value)

    db.add(file)
    db.commit()


def create_examination_result(user_id: int, analyzer_id: int, data: Examination, db: Session) -> None:
    examination_result: ExaminationResult = ExaminationResult(examination_date=data.date,
                                                              fk_analyzer=analyzer_id,
                                                              fk_user=user_id,
                                                              leukocytes=data.leukocytes,
                                                              nitrite=data.nitrite,
                                                              urobilinogen=data.urobilinogen,
                                                              protein=data.protein,
                                                              ph=data.ph,
                                                              blood=data.blood,
                                                              specific_gravity=data.specific_gravity,
                                                              ascorbate=data.ascorbate,
                                                              ketone=data.ketone,
                                                              bilirubin=data.bilirubin,
                                                              glucose=data.glucose,
                                                              micro_albumin=data.micro_albumin)

    db.add(examination_result)
    db.commit()


def read_my_files_by_type(file_type: str, user_id: str, db: Session) -> list[tuple[int, str, str]]:
    res: list[tuple[int, str, str]] = db.query(Files.id, Analyzer.code, Files.absolute_path).join(
        Analyzer,
        Analyzer.id == Files.fk_analyzer).filter(and_(Files.fk_user == user_id,
                                                      Files.fk_type == file_type)).all()

    return res


def delete_file(id: int, db: Session) -> None:
    res: Optional[Files] = db.query(Files).filter(Files.id == id).first()

    db.delete(res)
    db.commit()


def find_file(id: int, user_login: str, db: Session) -> Optional[Files]:
    res: Optional[Files] = db.query(Files).join(User, User.id == Files.fk_user).filter(
        and_(Files.id == id, User.login == user_login)).first()
    return res
