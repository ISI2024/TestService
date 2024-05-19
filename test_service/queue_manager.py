from test_service.crud import create_user, get_user_by_login, update_user, delete_user, update_wallet, get_examination_result_by_id, update_examination_result
from test_service.database import SessionLocal
from test_service.dataclasses import UsersEvent, UsersEventType, ExaminationResult, TestsEvent, TestsEventType, FinishedTest
from test_service.config import Config

import json

import asyncio
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
from logging import log, INFO, ERROR

config = Config()

kafka_conf_producer = {'bootstrap.servers': config.kafka_host, 'client.id': 'tests-producer'}
kafka_conf_consumer = {
    'bootstrap.servers': config.kafka_host,
    'group.id': 'tests',
    'auto.offset.reset': 'latest'
}

class KafkaConsumer:

    def __init__(self, topic: str) -> None:
        self.topic = topic
        self.consumer = None

    async def setup(self):
        self.consumer = Consumer(kafka_conf_consumer)

    async def consume_messages(self):
        if self.consumer is None:
            await self.setup()

        self.consumer.subscribe([self.topic])

        try:
            while True:
                msg = self.consumer.poll(1.0)

                if msg is None:
                    await asyncio.sleep(1)
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        log(ERROR, msg.error())
                        raise KafkaException(msg.error())

                if self.topic == "users":
                    await self.on_users_message(message=msg.value().decode("utf-8"))
                else:
                    await self.on_tests_message(message=msg.value().decode("utf-8"))

                await asyncio.sleep(1)

        except Exception as e:
            log(ERROR, f'Błąd podczas konsumpcji wiadomości: {e}')

        finally:
            self.consumer.close()

    async def on_users_message(self, message: str):
        try:
            message_json = json.loads(message)
            decoded = UsersEvent(**message_json)

            with SessionLocal() as db_session:
                match decoded.kind:
                    case UsersEventType.NEW_USER:
                        await create_user(db_session=db_session, user_data=decoded.data.model_dump())
                    case UsersEventType.UPDATED_INFO:
                        await update_user(db_session=db_session,
                                          user_login=decoded.data.login,
                                          update_data=decoded.data.model_dump())
                    case UsersEventType.DELETED:
                        await delete_user(db_session=db_session, login=decoded.data.login)
                    case UsersEventType.CHANGED_WALLET_STATE:
                        await update_wallet(db_session=db_session,
                                            user_login=decoded.data.login,
                                            change=decoded.data.change_amount)
                    case _:
                        log(ERROR, f"Unsupported users command: {decoded.kind}")

        except Exception as e:
            log(ERROR, f"Unable to process user event message: {e}")

    async def on_tests_message(self, message: str):
        try:
            message = json.loads(message)
            decoded = TestsEvent(**message)


            with SessionLocal() as db_session:
                match decoded.kind:
                    case TestsEventType.FINISHED_ANALYZE:
                        current_examination = await get_examination_result_by_id(db_session=db_session,
                                                                                    result_id=decoded.data.id)
                        if current_examination and current_examination.examination_date is None:
                            examination =  await update_examination_result(db_session=db_session,
                                                                result_id=decoded.data.id,
                                                                update_data=decoded.model_dump())
                            user = await get_user_by_login(db_session=db_session, user_login=decoded.data.fk_user)

                            if user:
                                response = TestsEvent(kind=TestsEventType.FINISHED_TEST, data=FinishedTest(email=str(user.email))).model_dump_json()
                                await producer.produce_message(topic="tests", message=str(response))
                            
                    case TestsEventType.VERIFIED_USER:
                        pass
                    case TestsEventType.FINISHED_TEST:
                        pass
                    case _:
                        log(ERROR, f"Unsupported tests command: {decoded.kind}")

            
        except Exception as e:
            log(ERROR, f"Unable to process tests event message: {e}")       
        

# ----

class KafkaProducer:

    def __init__(self):
        self.producer = None

    async def setup(self):
        self.producer = Producer(kafka_conf_producer)
        log(INFO, f"Created producer")

    async def produce_message(self, message: str, topic: str):
        if self.producer is None:
            await self.setup()
        try:
            self.producer.produce(topic, value=message)
            self.producer.flush()
            log(INFO, f"Produced event: {topic}")

        except KafkaException as e:
            log(ERROR, f"Unable to produce event: {e}")

producer = KafkaProducer()

# ----



# {"kind": "NEW_USER","data": {"login":"kutacz10","email":"ur10@mo.m","wallet":21.37}}
# {"kind": "UPDATE","data": {"login":"kutacz","email":"ur4@mo.m","wallet":421.37}}
# {"kind": "DELETE","data": {"login":"kutacz","email":"ur@mo.m","wallet":21.37}}
# {"kind": "CHANGE_WALLET","data": {"login":"kutacz","email":"ur2@mo.m","wallet":-11.37}}

# {"kind": "FINISHED_ANALYZE","data": {"id": 5, "fk_user":"adamozo","analyzer":"121121","examination_date":"2024-05-03 23:54:48.197062","leukocytes":"2137","nitrite":null,"urobilinogen":null,"protein":null,"ph":null,"blood":null,"specific_gravity":null,"ascorbate":null,"ketone":null,"bilirubin":null,"glucose":null,"micro_albumin":null}}