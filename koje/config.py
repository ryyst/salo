from typing import List
from pydantic import BaseModel
from utils.schema import JSONModel


class IFrame(BaseModel):
    id: str
    src: str
    title: str


class KojeConfig(JSONModel):
    iframes: List[IFrame]
    title: str = "Salo"
    description: str = "Dashboard for local Salo services"
