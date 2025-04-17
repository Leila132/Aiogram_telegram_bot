from pydantic import BaseModel, validator
from urllib.parse import urlparse
from typing import List


class TableRowBase(BaseModel):
    title: str
    url: str
    xpath: str

    @validator("url")
    def validate_url(cls, v):
        parsed = urlparse(v)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValueError("Uncorrect URL.")
        return v


class TableRow(TableRowBase):
    class Config:
        from_attributes = True


class TableDataBase(BaseModel):
    rows: List[TableRowBase]


class TableData(TableDataBase):
    class Config:
        from_attributes = True


class UserDataBase(BaseModel):
    tg_id: str
    status_name: str


class UserData(TableDataBase):
    class Config:
        from_attributes = True
