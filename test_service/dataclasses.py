from enum import unique
from typing import Optional
from pydantic import BaseModel
from test_service.common.enums import NoValue

@unique
class SocketMessageType(NoValue):
    TOKEN = 'TOKEN'
    AWAIT_RESULT = 'AWAIT_RESULT'


class SocketMessage(BaseModel):
    kind: SocketMessageType
    token: Optional[str]