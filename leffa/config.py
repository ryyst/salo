from utils.schema import JSONModel


class LeffaConfig(JSONModel):
    location_id: int = 1
    content_type_id: int = 1
    language: str = "fi"
    upcoming_only: bool = True
    days_ahead: int = 14
    output_dir: str = "leffa"
