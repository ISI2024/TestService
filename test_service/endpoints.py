from fastapi import APIRouter, Depends
from fastapi import UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi import HTTPException
from rest_api.common.data_classes import PhotoSeries
from rest_api.dependencies import get_db
from rest_api.common.users.schemas import TokenData, AnalyzerTokenData, QrCodeData
from rest_api.research.api import make_photo_series, make_cut_photo, read_file, remove_file, my_files_by_type, can_examination, turn_on_webrtc, setup_lights, allow_examination, start_examination, save_file, save_examination_result
from rest_api.common.research.shemas import ExaminationResult, FileType, MyFile
from rest_api.common.research.shemas import LightsSetup
from rest_api.dependencies import get_redis
from rest_api.users.credentials.api import get_current_researcher, get_current_analyzer, check_qr_code, get_current_user
from redis import Redis
import json

router = APIRouter(
    prefix="/research",
    tags=["/research"],
    responses={404: {
        "description": "Not found"
    }},
)


@router.put("/webrtc_on/{analyzer_code}", response_model=str, summary="Turn on WebRTC")
async def put_webrtc_on(
    analyzer_code: str,
    token_data: TokenData = Depends(get_current_researcher),
    redis_client: Redis = Depends(get_redis),
    db: Session = Depends(get_db)
) -> str:
    """
    Start camera stream on given analyzer. \n
    It can be executed only on an analyzer that the researcher has access to. \n
    Researcher permission level i required. 
    """
    analyzer: str = await turn_on_webrtc(analyzer_code=analyzer_code,
                                         db=db,
                                         redis_client=redis_client,
                                         researcher_login=token_data.login)

    return analyzer


@router.put("/lights/", summary="Light up LED panel")
async def put_lights(
    input: LightsSetup,
    token_data: TokenData = Depends(get_current_researcher),
    redis_client: Redis = Depends(get_redis),
    db: Session = Depends(get_db)
) -> None:
    """
    It can be executed only on an analyzer that the researcher has access to. \n
    Researcher permission level i required. 
    """
    await setup_lights(analyzer_code=input.analyzer_code,
                       db=db,
                       redis_client=redis_client,
                       data=input.lights,
                       researcher_login=token_data.login)


@router.put("/verify_customer", summary="Verify customer QR code")
async def put_verify_customer(
    qr_code_token: str,
    token_data: AnalyzerTokenData = Depends(get_current_analyzer),
    db: Session = Depends(get_db)
) -> None:
    """
    Check if scanned QR code is valid and user can be examined. \n
    Analyzer permission level is required.
    """
    user_token: QrCodeData = await check_qr_code(token_body=qr_code_token)
    await allow_examination(analyzer_code=token_data.code, user_login=user_token.login, db=db)


@router.get("/can_examination", response_model=bool, summary="Can user start examination")
async def get_can_i_examination(token_data: TokenData = Depends(get_current_user),
                                db: Session = Depends(get_db)) -> bool:
    res: bool = await can_examination(user_login=token_data.login, db=db)
    return res


@router.put("/examination", summary="Start examination")
async def put_examination(token_data: TokenData = Depends(get_current_user),
                          db: Session = Depends(get_db),
                          redis_client: Redis = Depends(get_redis)) -> None:
    if await can_examination(user_login=token_data.login, db=db):
        await start_examination(user_login=token_data.login, db=db, redis_client=redis_client)

    else:
        raise HTTPException(status_code=403, detail="Unable to start examination")


@router.post("/examination_result", summary="Send examination result")
async def post_examination_result(
    result: ExaminationResult,
    token_data: AnalyzerTokenData = Depends(get_current_analyzer),
    db: Session = Depends(get_db)
) -> None:
    """
    Analyzer permission level is required.
    """
    await save_examination_result(analyzer_code=token_data.code, data=result, db=db)


@router.post("/file", summary="Send file")
async def post_file(
    user_login: str,
    file_type: FileType,
    file: UploadFile,
    token_data: AnalyzerTokenData = Depends(get_current_analyzer),
    db: Session = Depends(get_db)
) -> None:
    """
    Send file from analyzer, assign it to specific user and match it with file category. \n
    Analyzer permission level is required.
    """
    await save_file(user_login=user_login,
                    file=file,
                    analyzer_code=token_data.code,
                    file_type=file_type,
                    db=db)


@router.get("/my_files", response_model=list[MyFile], summary="List assigned files")
async def get_my_files(
    type: FileType, token_data: TokenData = Depends(get_current_researcher), db: Session = Depends(get_db)
) -> list[MyFile]:
    """
    Researcher permission level is required.
    """
    res: list[MyFile] = await my_files_by_type(user_login=token_data.login, file_type=type.value, db=db)
    return res


@router.delete("/file", summary="Delete file")
async def delete_file(
    id: int, token_data: TokenData = Depends(get_current_researcher), db: Session = Depends(get_db)) -> None:
    """
    Delete one of files assigned to researcher. \n
    Researcher permission level is required.
    """
    await remove_file(id=id, user_login=token_data.login, db=db)


@router.get("/file", response_class=FileResponse, summary="Get file")
async def get_file(
    id: int, token_data: TokenData = Depends(get_current_researcher), db: Session = Depends(get_db)
) -> FileResponse:
    """
    Returns one of files assigned to researcher. \n
    Researcher permission level is required.
    """
    res = await read_file(id=id, user_login=token_data.login, db=db)
    return res


@router.put("/make_cut_photo", summary="Make cut photo")
async def put_make_cut_photo(
    analyzer_code: str,
    token_data: TokenData = Depends(get_current_researcher),
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis)
) -> None:
    """
    It can be executed only on an analyzer that the researcher has access to. \n
    Researcher permission level i required. 
    """
    await make_cut_photo(user_login=token_data.login,
                         analyzer_code=analyzer_code,
                         db=db,
                         redis_client=redis_client)


@router.put("/make_photo_series", summary="Make series of photos")
async def put_make_photo_series(analyzer_code: str,
                                data: PhotoSeries,
                                token_data: TokenData = Depends(get_current_researcher),
                                db: Session = Depends(get_db),
                                redis_client: Redis = Depends(get_redis)):
    """
    It can be executed only on an analyzer that the researcher has access to. \n
    Researcher permission level i required. 
    """
    await make_photo_series(user_login=token_data.login,
                            analyzer_code=analyzer_code,
                            data=data,
                            db=db,
                            redis_client=redis_client)
