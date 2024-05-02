from datetime import datetime
from pydantic import BaseModel
from rest_api.common.data_classes import Lights
from enum import Enum, unique, auto
from rest_api.common.enums import NoValue


class LightsSetup(BaseModel):
    analyzer_code: str
    lights: Lights


class Examination(BaseModel):
    date: datetime
    leukocytes: str | None
    nitrite: str | None
    urobilinogen: str | None
    protein: str | None
    ph: str | None
    blood: str | None
    specific_gravity: str | None
    ascorbate: str | None
    ketone: str | None
    bilirubin: str | None
    glucose: str | None
    micro_albumin: str | None


class ExaminationResult(BaseModel):
    user_login: str
    examination: Examination


@unique
class FileFormat(NoValue):
    ZIP = 'zip'
    JPG = 'jpg'
    JPEG = 'jpeg'
    PNG = 'png'
    RAR = 'rar'


@unique
class FileType(NoValue):
    CUSTOMER_EXAMINATION = 'CustomerExamination'
    PHOTO_SERIES = 'PhotosSeries'
    CUT_PHOTO = 'CutPhoto'


class NewFile(BaseModel):
    fk_user: int
    fk_analyzer: int
    absolute_path: str
    fk_format: FileFormat
    fk_type: FileType


class MyFile(BaseModel):
    id: int
    analyzer_code: str
    name: str
