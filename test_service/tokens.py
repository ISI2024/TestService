from lib2to3.pgen2 import token
from test_service.errors import credentials_exception, qr_code_expired
from jose import JWTError, jwt
from datetime import datetime, timedelta
from test_service.dependencies import QR_CODE_ALGORITHM, QR_CODE_ENCRYPT_KEY, QR_CODE_TOKEN_LIFE_TIME
from test_service.dataclasses import QrCodeData


async def check_qr_code(token_body: str) -> QrCodeData:
    try:
        data = jwt.decode(token=token_body, key=QR_CODE_ENCRYPT_KEY, algorithms=QR_CODE_ALGORITHM)

        if data is None:
            raise credentials_exception

    except JWTError:
        raise qr_code_expired

    return data


async def qr_code_data(login: str) -> str:
    expire: datetime = datetime.now() + timedelta(0, QR_CODE_TOKEN_LIFE_TIME * 60)
    to_encode: dict = {"login": login, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, QR_CODE_ENCRYPT_KEY, algorithm=QR_CODE_ALGORITHM)

    return str(encoded_jwt)
