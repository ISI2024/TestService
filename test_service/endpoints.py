from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from test_service.dependencies import get_db, get_rabbitmq_channel
from test_service.sockets_manager import ConnectionManager
from test_service.crud import get_user_by_login, get_users_examinations, create_examination_result
from test_service.errors import no_user_with_given_login, no_money
from test_service.models import Users, ExaminationResult
from test_service.tokens import check_qr_code, qr_code_data
from test_service.dataclasses import SocketMessage, SocketMessageType, QrCodeData, WalletChangeData, UsersMessage, UsersMessageType, AnalyzerCommand
from test_service.schemas import Examination

router = APIRouter(
    prefix="/examination",
    tags=["/examination"],
    responses={404: {
        "description": "Not found"
    }},
)

manager = ConnectionManager()

# -------------------------


@router.post("/queue_test/")
async def send_message(message: str, key: str, channel=Depends(get_rabbitmq_channel)):
    channel.basic_publish(exchange='', routing_key=key, body=message)
    return {"message": "Message sent", "content": message}


# ----


@router.websocket("/get_qr_code/{login}")
async def get_qr_code_with_socket(websocket: WebSocket, login: str, db: Session = Depends(get_db)):
    user: Users = await get_user_by_login(db_session=db, user_login=login)

    if user is None:
        raise no_user_with_given_login

    if user.wallet - 5 < 0:
        raise no_money

    await manager.connect(websocket=websocket, login=login)
    try:
        token_data = await qr_code_data(login)
        message = SocketMessage(kind=SocketMessageType.TOKEN, token=token_data)
        await manager.send_personal_message(login=login, message=str(message.model_dump_json()))
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"User {login} dissconected")


@router.put("/verify_customer", summary="Verify customer QR code")
async def put_verify_customer(
    qr_code_token: str, code: str, db: Session = Depends(get_db),
    channel=Depends(get_rabbitmq_channel)) -> None:
    """
    Check if scanned QR code is valid and user can be examined.
    """
    user_token: QrCodeData = await check_qr_code(token_body=qr_code_token)
    message = SocketMessage(kind=SocketMessageType.AWAIT_RESULT, token=None)
    await manager.send_personal_message(login=user_token["login"], message=str(message.model_dump_json()))

    result = await create_examination_result(db_session=db,
                                             fk_user=user_token["login"],
                                                analyzer=code)
    channel.basic_publish(exchange='', 
                          routing_key="tests2analyzer", 
                          body=str(
                            AnalyzerCommand(user_login=user_token["login"],id=result.id).model_dump_json()))
    channel.basic_publish(exchange='',
                          routing_key="tests2users",
                          body=str(
                              UsersMessage(kind=UsersMessageType.CHANGE_WALLET,
                                           data=WalletChangeData(login=user_token["login"],
                                                                 wallet=-5.0)).model_dump_json()))

    # manager.disconnect(login=user_token.login)


@router.get("/results/{login}", response_model=list[Examination], summary="List examinations")
async def get_read_my_examinations(login: str, db: Session = Depends(get_db)) -> list[Examination]:
    """
    Allows the user to list all of their examinations
    """
    return await get_users_examinations(db_session=db, login=login)
