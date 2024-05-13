from typing import Optional
from sqlalchemy.orm import Session
from test_service.models import Users, ExaminationResult
from test_service.schemas import Examination
from logging import log, INFO, ERROR


# USER
async def create_user(db_session: Session, user_data: dict) -> None:
    try:
        new_user = Users(**user_data)
        db_session.add(new_user)
        db_session.commit()
        log(INFO, "Successfully created new user")

    except Exception as e:
        log(ERROR, f"Unable to create user: {e}")


async def get_user_by_login(db_session: Session, user_login: str) -> Optional[Users]:
    return db_session.query(Users).filter(Users.login == user_login).first()


async def get_all_users(db_session: Session) -> list[Users]:
    return db_session.query(Users).all()


async def update_user(db_session: Session, user_login: str, update_data: dict) -> None:
    try:
        user = db_session.query(Users).filter(Users.login == user_login).first()
        if user:
            for key, value in update_data.items():
                setattr(user, key, value)
            db_session.commit()

        log(INFO, "Successfully updated user")

    except Exception as e:
        log(ERROR, f"Unable to update user: {e}")


async def update_wallet(db_session: Session, user_login: str, change: float) -> None:
    try:
        current_data = db_session.query(Users).filter(Users.login == user_login).first()
        db_session.query(Users).filter(Users.login == user_login).update(
            {'wallet': current_data.wallet + change})
        db_session.commit()

        log(INFO, "Successfully updated user")

    except Exception as e:
        log(ERROR, f"Unable to update user: {e}")


async def delete_user(db_session: Session, login: str) -> None:
    try:
        users = db_session.query(Users).filter(Users.login == login).delete()
        db_session.commit()

        examinations = db_session.query(ExaminationResult).filter(ExaminationResult.fk_user == login).all()
        
        for examination in examinations:
            db_session.delete(examination)
        
        db_session.commit()

        log(INFO, "Successfully deleted user")

    except Exception as e:
        log(ERROR, f"Unable to delete user: {e}")


#----------------------------
# Examinations


async def create_examination_result(db_session: Session, fk_user: str, analyzer: str):
    new_result = ExaminationResult(fk_user=fk_user, analyzer=analyzer)
    db_session.add(new_result)
    db_session.commit()
    db_session.refresh(new_result)
    return new_result


async def get_examination_result_by_id(db_session: Session, result_id: int):
    return db_session.query(ExaminationResult).filter(ExaminationResult.id == result_id).first()


async def get_users_examinations(db_session: Session, login: str):
    results = db_session.query(ExaminationResult).filter(ExaminationResult.fk_user == login).all()

    return [
        Examination(id=result.id,
                    examination_date=result.examination_date,
                    leukocytes=result.leukocytes,
                    nitrite=result.nitrite,
                    urobilinogen=result.urobilinogen,
                    protein=result.protein,
                    ph=result.ph,
                    blood=result.blood,
                    specific_gravity=result.specific_gravity,
                    ascorbate=result.ascorbate,
                    ketone=result.ketone,
                    bilirubin=result.bilirubin,
                    glucose=result.glucose,
                    micro_albumin=result.micro_albumin) for result in results
    ]


async def update_examination_result(db_session: Session, result_id: int, update_data: dict):
    result = db_session.query(ExaminationResult).filter(ExaminationResult.id == result_id).first()
    if result:
        for key, value in update_data.items():
            setattr(result, key, value)
        db_session.commit()
        return result
    return None


async def delete_examination_result(db_session: Session, result_id: int):
    result = db_session.query(ExaminationResult).filter(ExaminationResult.id == result_id).first()
    if result:
        db_session.delete(result)
        db_session.commit()
        return True
    return False
