from utils.schema import JSONModel


class SaaConfig(JSONModel):
    place: str = "salo"
    future_days: int = 1
    output_dir: str = "_out/saa"
