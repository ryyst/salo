from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class JSONModel(BaseModel):
    """Pydantic schema which automatically converts between camel and snake cases.

    Useful for parsing JSON configs.
    """

    class Config:
        populate_by_name = False
        alias_generator = to_camel
        extra = "forbid"
