from utils.schema import JSONModel


class SaaConfig(JSONModel):
    place: str = "salo"
    future_hours: int = 28
    output_dir: str = "_out/saa"
