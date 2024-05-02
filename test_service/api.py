import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from rest_api.common.analyzer.models import Analyzer
from rest_api.common.research.shemas import Examination, ExaminationResult, FileFormat, FileType, MyFile, NewFile
from rest_api.research import crud
from rest_api.analyzer import crud as analyzer_crud
from rest_api.users.profiles import crud as profiles_crud
from rest_api.common.analyzer.errors import no_connection_researcher_analyzer, no_available_analyzer_with_code, no_queue_response, unable_to_process_analyzer_response, analyzer_webrtc_error
from rest_api.common.research.errors import no_available_examination, no_file, wrong_file_name, already_verified
from rest_api.common.users.errors import no_user_with_given_login
from rest_api.common.queue_data import QueueCommand
from rest_api.common.enums import Commands
from rest_api.common.research.models import Files
from rest_api.common.analyzer.schemas import AnalyzerResearcher
from utils.redis_queue import insert_to_queue, read_analyzer_response, insert_response
from utils.file import save_file as util_save_file
from utils.file import extract_filename, delete
from redis import Redis
from rest_api.common.data_classes import Lights, WebrtcResponse, PhotoSeries
from fastapi import UploadFile
from fastapi.responses import FileResponse

import os


async def turn_on_webrtc(analyzer_code: str, researcher_login: str, db: Session, redis_client: Redis) -> str:
    conn: Optional[AnalyzerResearcher] = analyzer_crud.find_researcher_analyzer_by_login(
        user_login=researcher_login, analyzer_code=analyzer_code, db=db)

    if conn is None:
        raise no_connection_researcher_analyzer

    res: bool = crud.check_if_analyzer_available(analyzer_id=conn.analyzer_id, db=db)

    if not res:
        raise no_available_analyzer_with_code

    message: QueueCommand = QueueCommand(type=Commands.WEBRTC_ON)

    insert_to_queue(redis_client=redis_client, queue_name=analyzer_code, message=message)

    try:
        result: Optional[WebrtcResponse] = read_analyzer_response(redis_client=redis_client,
                                                                  analyzer_code=analyzer_code)

        if result is None:
            raise no_queue_response

        result: str = result.get_data()

    except ValueError:
        raise unable_to_process_analyzer_response

    except KeyError:
        raise unable_to_process_analyzer_response

    except SystemError as e:
        raise analyzer_webrtc_error(message=e.args[0])

    return result


async def setup_lights(analyzer_code: str, db: Session, redis_client: Redis, data: Lights,
                       researcher_login: str):
    conn: Optional[AnalyzerResearcher] = analyzer_crud.find_researcher_analyzer_by_login(
        user_login=researcher_login, analyzer_code=analyzer_code, db=db)

    if conn is None:
        raise no_connection_researcher_analyzer

    res: bool = crud.check_if_analyzer_available(analyzer_id=conn.analyzer_id, db=db)

    if not res:
        raise no_available_analyzer_with_code

    insert_to_queue(redis_client=redis_client,
                    queue_name=analyzer_code,
                    message=QueueCommand(type=Commands.LIGHT_UP_DIODES, data=data))


async def allow_examination(analyzer_code: str, user_login: str, db: Session) -> None:
    user: Optional[int] = profiles_crud.find_user(login=user_login, db=db)

    if user is None:
        raise no_user_with_given_login

    analyzer: Optional[Analyzer] = analyzer_crud.read_analyzer_by_code(code=analyzer_code, db=db)

    if analyzer is None:
        raise no_available_analyzer_with_code

    try:
        crud.create_allowed_examination(user_id=user[0], analyzer_id=analyzer.id, db=db)

    except IntegrityError:
        raise already_verified


async def can_examination(user_login: str, db: Session) -> bool:
    user: Optional[int] = profiles_crud.find_user(login=user_login, db=db)

    if user is None:
        raise no_user_with_given_login

    allowed: Optional[tuple[int, int, str]] = crud.read_allowed_examination(user_id=user[0], db=db)

    if allowed is None:
        return False

    return True


async def start_examination(user_login: str, db: Session, redis_client: Redis) -> None:
    user: Optional[int] = profiles_crud.find_user(login=user_login, db=db)

    if user is None:
        raise no_user_with_given_login

    allowed: Optional[tuple[int, int, str]] = crud.read_allowed_examination(user_id=user[0], db=db)

    if allowed is None:
        return no_available_examination

    message: QueueCommand = QueueCommand(type=Commands.CUSTOMER_TEST, user_login=user_login)

    user_id: int = allowed[0]
    analyzer_id: int = allowed[1]
    analyzer_code: str = allowed[2]

    insert_to_queue(redis_client=redis_client, queue_name=analyzer_code, message=message)

    crud.delete_allowed_examination(user_id=user_id, analyzer_id=analyzer_id, db=db)


async def save_file(user_login: str, analyzer_code: str, file: UploadFile, file_type: FileType,
                    db: Session) -> None:
    file_name: str = str(file.filename)

    try:
        file_format: FileFormat = FileFormat[file_name.split('.')[-1].upper()]

    except KeyError:
        raise wrong_file_name

    directory: str = f"{os.getcwd()}/files/{file_type.value}/{user_login}"
    file_name: str = str(datetime.datetime.now()).replace(' ', '_') + '_' + file_name

    user: Optional[int] = profiles_crud.find_user(login=user_login, db=db)

    if user is None:
        raise no_user_with_given_login

    analyzer: Optional[Analyzer] = analyzer_crud.read_analyzer_by_code(code=analyzer_code, db=db)

    if analyzer is None:
        raise no_available_analyzer_with_code

    util_save_file(directory=directory, file=file.file, file_name=file_name)

    crud.create_file(db=db,
                     new_file=NewFile(fk_user=user[0],
                                      fk_analyzer=analyzer.id,
                                      fk_format=file_format,
                                      fk_type=file_type,
                                      absolute_path=f"{directory}/{file_name}"))


async def save_examination_result(analyzer_code: str, data: ExaminationResult, db: Session) -> None:
    user: Optional[int] = profiles_crud.find_user(login=data.user_login, db=db)

    if user is None:
        raise no_user_with_given_login

    analyzer: Optional[Analyzer] = analyzer_crud.read_analyzer_by_code(code=analyzer_code, db=db)

    if analyzer is None:
        raise no_available_analyzer_with_code

    crud.create_examination_result(user_id=user[0], analyzer_id=analyzer.id, data=data.examination, db=db)


async def my_files_by_type(user_login: str, file_type: str, db: Session) -> list[MyFile]:
    user: Optional[int] = profiles_crud.find_user(login=user_login, db=db)

    if user is None:
        raise no_user_with_given_login

    my_files: list[tuple[int, str, str]] = crud.read_my_files_by_type(user_id=user[0],
                                                                      file_type=file_type,
                                                                      db=db)

    res = []

    for file in my_files:
        res.append(
            MyFile(id=file[0],
                   analyzer_code=file[1],
                   name=extract_filename(absolute_path=file[2], user_login=user_login)))

    return res


async def remove_file(id: int, user_login: str, db: Session) -> None:
    file: Optional[Files] = crud.find_file(id=id, user_login=user_login, db=db)

    if file is None:
        raise no_file

    delete(absolute_path=file.absolute_path)

    crud.delete_file(id=id, db=db)


async def read_file(id: int, user_login: str, db: Session) -> FileResponse:
    file: Optional[Files] = crud.find_file(id=id, user_login=user_login, db=db)

    if file is None:
        raise no_file

    return FileResponse(file.absolute_path)


async def make_cut_photo(user_login: str, analyzer_code: str, db: Session, redis_client: Redis) -> None:
    conn: Optional[AnalyzerResearcher] = analyzer_crud.find_researcher_analyzer_by_login(
        user_login=user_login, analyzer_code=analyzer_code, db=db)

    if conn is None:
        raise no_connection_researcher_analyzer

    res: bool = crud.check_if_analyzer_available(analyzer_id=conn.analyzer_id, db=db)

    if res is False:
        raise no_available_analyzer_with_code

    insert_to_queue(redis_client=redis_client,
                    queue_name=analyzer_code,
                    message=QueueCommand(type=Commands.CUT_PHOTO, user_login=user_login))


async def make_photo_series(user_login: str, analyzer_code: str, data: PhotoSeries, db: Session,
                            redis_client: Redis):
    conn: Optional[AnalyzerResearcher] = analyzer_crud.find_researcher_analyzer_by_login(
        user_login=user_login, analyzer_code=analyzer_code, db=db)

    if conn is None:
        raise no_connection_researcher_analyzer

    res: bool = crud.check_if_analyzer_available(analyzer_id=conn.analyzer_id, db=db)

    if res is False:
        raise no_available_analyzer_with_code

    insert_to_queue(redis_client=redis_client,
                    queue_name=analyzer_code,
                    message=QueueCommand(type=Commands.TAKE_PHOTOS_SERIES, data=data, user_login=user_login))
