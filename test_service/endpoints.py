from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from logging import log, INFO, ERROR


from test_service.dependencies import get_db
from test_service.sockets_manager import ConnectionManager
from test_service.crud import get_user_by_login, get_users_examinations, create_examination_result
from test_service.errors import no_user_with_given_login, no_money
from test_service.models import Users, ExaminationResult
from test_service.tokens import check_qr_code, qr_code_data
from test_service.dataclasses import SocketMessage, SocketMessageType, QrCodeData, WalletChangeData, UsersEventType, UsersEvent, VerifiedUser, TestsEventType, TestsEvent
from test_service.schemas import Examination, AnalyzerCommand
from test_service.queue_manager import producer
from test_service.config import Config

router = APIRouter(
    prefix="/examination",
    tags=["/examination"],
    responses={404: {
        "description": "Not found"
    }},
)

manager = ConnectionManager()
config = Config()

# -------------------------
# Only for easier development

@router.post("/queue_test/")
async def send_message(message: str, key: str):
    await producer.produce_message(message=message, topic=key)
    return {"message": "Message sent", "content": message}


# ----


@router.websocket("/get_qr_code/{login}")
async def get_qr_code_with_socket(websocket: WebSocket, login: str, db: Session = Depends(get_db)):
    """
    Setup websocket connection. 
    Generate jwt for qr code generation.
    After qr code verification connection is closed.
    """
    user: Users = await get_user_by_login(db_session=db, user_login=login)

    if user is None:
        raise no_user_with_given_login

    if user.wallet - config.test_cost < 0:
        raise no_money

    await manager.connect(websocket=websocket, login=login)
    try:
        token_data = await qr_code_data(login)
        message = SocketMessage(kind=SocketMessageType.TOKEN, token=token_data)
        await manager.send_personal_message(login=login, message=str(message.model_dump_json()))
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        log(INFO, f"User {login} dissconected")


@router.put("/verify_customer", summary="Verify customer QR code")
async def put_verify_customer(qr_code_token: str, code: str,
                              db: Session = Depends(get_db)) -> AnalyzerCommand:
    """
    Check if scanned QR code is valid and user can be examined.
    If so, starts examination logic.
    """
    user_token: QrCodeData = await check_qr_code(token_body=qr_code_token)
    message = SocketMessage(kind=SocketMessageType.AWAIT_RESULT, token=None)
    await manager.send_personal_message(login=user_token["login"], message=str(message.model_dump_json()))

    result = await create_examination_result(db_session=db, fk_user=user_token["login"], analyzer=code)

    await producer.produce_message(message=str(
        UsersEvent(kind=UsersEventType.CHANGED_WALLET_STATE,
                   data=WalletChangeData(login=user_token["login"], change_amount=-config.test_cost)).model_dump_json()),
                                   topic="users")

    await manager.disconnect(login=user_token["login"])

    event = TestsEvent(kind=TestsEventType.VERIFIED_USER, data=VerifiedUser(login=user_token["login"], analyzer_code=code, examination_id=result.id)).model_dump_json()
    await producer.produce_message(topic="tests", message=str(event))

    return AnalyzerCommand(user_login=user_token["login"], id=result.id)


@router.get("/results/{login}", response_model=list[Examination], summary="List examinations")
async def get_read_my_examinations(login: str, db: Session = Depends(get_db)) -> list[Examination]:
    """
    Allows the user to list all of their examinations
    """
    return await get_users_examinations(db_session=db, login=login)


# update i delete results