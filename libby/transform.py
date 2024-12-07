from libby.config import LibbyConfig


def transform_schedule(data, params: LibbyConfig):
    return data.data["schedules"]
