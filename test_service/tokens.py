from test_service.errors import credentials_exception, qr_code_expired
from jose import JWTError, jwt
from datetime import datetime, timedelta
from test_service.config import Config
from test_service.common.users import QrCodeData

config = Config()


async def check_qr_code(token_body: str) -> QrCodeData:
    try:
        data = jwt.decode(token=token_body, key=config.qr_code.key, algorithms=config.qr_code.algorithm)

        if data is None:
            raise credentials_exception

    except JWTError:
        raise qr_code_expired

    return data


async def qr_code_data(login: str) -> str:
    expire: datetime = datetime.now() + timedelta(0, config.qr_code.token_life_time * 60)
    to_encode: dict = {"login": login, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, config.qr_code.key, algorithm=config.qr_code.algorithm)

    return str(encoded_jwt)
