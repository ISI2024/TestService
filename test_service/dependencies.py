from rest_api.database import SessionLocal
import os
import redis

QR_CODE_ENCRYPT_KEY = os.environ.get("QR_CODE_ENCRYPT_KEY")
QR_CODE_TOKEN_LIFE_TIME = int(os.environ.get("QR_CODE_TOKEN_LIFE_TIME"))
QR_CODE_ALGORITHM = os.environ.get("QR_CODE_ALGORITHM")

redis_pool = redis.ConnectionPool(host=str(os.environ.get("REDIS_LINK")), port=6379, db=0)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_redis():
    try:
        redis_client = redis.Redis(connection_pool=redis_pool)
        yield redis_client
    finally:
        redis_client.close()
