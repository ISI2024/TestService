# @router.put("/send_result", summary="Send examination result")
# async def put_examination_result(result: ExaminationResult, db: Session = Depends(get_db)) -> None:

from aio_pika import connect, IncomingMessage
from test_service.crud import get_examination_result_by_id, update_examination_result, get_user_by_login, create_user, update_user, delete_user, update_wallet
from test_service.database import SessionLocal
from test_service.dataclasses import ExaminationResult, EmailExaminationResult, UsersMessage, UsersMessageType
from test_service.dependencies import get_rabbitmq_channel
import json


class QueueManager():

    async def setup(self):
        self.connection = await connect("amqp://guest:guest@localhost/")
        self.channel = await self.connection.channel()
        self.test2users = await self.channel.declare_queue("tests2users")
        self.test2analyzer = await self.channel.declare_queue("tests2analyzer")
        await self.channel.declare_queue("email_service")

    async def on_users_message(self, message: IncomingMessage):
        async with message.process():
            try:
                message = json.loads(message.body.decode())
                decoded = UsersMessage(**message)

                db_session = SessionLocal()

                match decoded.kind:
                    case UsersMessageType.CREATE:
                        # {"kind": "CREATE","data": {"login":"kutacz","email":"ur@mo.m","wallet":21.37}}
                        await create_user(db_session=db_session, user_data=decoded.data.model_dump())
                    case UsersMessageType.UPDATE:
                        # {"kind": "UPDATE","data": {"login":"kutacz","email":"ur4@mo.m","wallet":421.37}}
                        await update_user(db_session=db_session,
                                          user_login=decoded.data.login,
                                          update_data=decoded.data.model_dump())
                    case UsersMessageType.DELETE:
                        # {"kind": "DELETE","data": {"login":"kutacz","email":"ur@mo.m","wallet":21.37}}
                        await delete_user(db_session=db_session, login=decoded.data.login)
                    case UsersMessageType.CHANGE_WALLET:
                        # {"kind": "CHANGE_WALLET","data": {"login":"kutacz","email":"ur2@mo.m","wallet":-11.37}}
                        await update_wallet(db_session=db_session,
                                            user_login=decoded.data.login,
                                            change=decoded.data.wallet)
                    case _:
                        raise Exception("Unsupported users command")

            except Exception as e:
                print(f"Unable to update examination from analyzer message: {e}")

    async def on_analyzers_message(self, message: IncomingMessage):
        async with message.process():
            try:
                message = json.loads(message.body.decode())
                decoded = ExaminationResult(**message)

                db_session = SessionLocal()

                current_examination = await get_examination_result_by_id(db_session=db_session,
                                                                         result_id=decoded.id)

                if current_examination and current_examination.examination_date is None:
                    await update_examination_result(db_session=db_session,
                                                    result_id=decoded.id,
                                                    update_data=decoded.model_dump())
                    # {"fk_user":"kutacz","analyzer":"121121","id":5,"examination_date":"2024-05-03 23:54:48.197062","leukocytes":"2137","nitrite":null,"urobilinogen":null,"protein":null,"ph":null,"blood":null,"specific_gravity":null,"ascorbate":null,"ketone":null,"bilirubin":null,"glucose":null,"micro_albumin":null}

                    user = await get_user_by_login(db_session=db_session, user_login=decoded.fk_user)
                    email_result = EmailExaminationResult(email=user.email, result=decoded)

                    chanel_gen = get_rabbitmq_channel()
                    next(chanel_gen).basic_publish(exchange='',
                                                   routing_key="email_service",
                                                   body=str(email_result.model_dump_json()))

            except Exception as e:
                print(f"Unable to update examination from analyzer message: {e}")

    async def consume(self):
        users2tests = await self.channel.declare_queue("users2tests")

        analyzers2tests = await self.channel.declare_queue("analyzers2tests")

        await users2tests.consume(self.on_users_message)
        await analyzers2tests.consume(self.on_analyzers_message)