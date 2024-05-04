from test_service.database import SessionLocal
import os
import pika

QR_CODE_ENCRYPT_KEY = os.environ.get("QR_CODE_ENCRYPT_KEY")
QR_CODE_TOKEN_LIFE_TIME = int(os.environ.get("QR_CODE_TOKEN_LIFE_TIME"))
QR_CODE_ALGORITHM = os.environ.get("QR_CODE_ALGORITHM")

rabbitmq_params = pika.ConnectionParameters(host=os.environ.get("RABBITMQ_HOST", "localhost"),
                                            port=int(os.environ.get("RABBITMQ_PORT", 5672)),
                                            credentials=pika.PlainCredentials(
                                                os.environ.get("RABBITMQ_USER", "guest"),
                                                os.environ.get("RABBITMQ_PASSWORD", "guest")))


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_rabbitmq_channel():
    try:
        connection = pika.BlockingConnection(rabbitmq_params)
        channel = connection.channel()
        yield channel
    finally:
        channel.close()
        connection.close()
