from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum, unique, auto
from typing import Optional
import datetime
from pydantic import BaseModel

# -----


class NoValue(Enum):

    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)


# -----


class AnalyzerCommand(BaseModel):
    id: int
    user_login: Optional[str]

# -----


class QrCodeData(BaseModel):
    login: str
    exp: int


# -----
@unique
class SocketMessageType(NoValue):
    TOKEN = 'TOKEN'
    AWAIT_RESULT = 'AWAIT_RESULT'


class SocketMessage(BaseModel):
    kind: SocketMessageType
    token: Optional[str]


# ----


class ExaminationResult(BaseModel):
    fk_user: str
    analyzer: str
    id: int
    examination_date: str
    leukocytes: Optional[str] = None
    nitrite: Optional[str] = None
    urobilinogen: Optional[str] = None
    protein: Optional[str] = None
    ph: Optional[str] = None
    blood: Optional[str] = None
    specific_gravity: Optional[str] = None
    ascorbate: Optional[str] = None
    ketone: Optional[str] = None
    bilirubin: Optional[str] = None
    glucose: Optional[str] = None
    micro_albumin: Optional[str] = None


class EmailExaminationResult(BaseModel):
    email: str
    result: ExaminationResult


# ----
@unique
class EmailMessageType(NoValue):
    RESULT = 'RESULT'


class EmailMessage(BaseModel):
    kind: EmailMessageType
    data: EmailExaminationResult


# -----


@unique
class UsersMessageType(NoValue):
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    CHANGE_WALLET = 'CHANGE_WALLET'


class WalletChangeData(BaseModel):
    login: str
    wallet: float


class UserData(WalletChangeData):
    email: str


class UsersMessage(BaseModel):
    kind: UsersMessageType
    data: UserData | WalletChangeData
