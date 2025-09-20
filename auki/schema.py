from pydantic import BaseModel, Field
from typing import Optional, List


class PhotoSizes(BaseModel):
    """Photo size variants from Kirjastot.fi"""

    url: str
    size: int
    resolution: str


class CoverPhoto(BaseModel):
    """Library cover photo in multiple sizes"""

    huge: PhotoSizes
    large: PhotoSizes
    small: PhotoSizes
    medium: PhotoSizes


class Address(BaseModel):
    """Library address information"""

    area: str
    city: str
    info: Optional[str]
    street: str
    zipcode: str
    boxNumber: Optional[str]


class Coordinates(BaseModel):
    """GPS coordinates"""

    lat: float
    lon: float


class OpeningTime(BaseModel):
    """Individual opening time slot"""

    to: str  # HH:MM format
    from_: str = Field(alias="from")  # HH:MM format (using from_ to avoid Python keyword)
    status: int


class DaySchedule(BaseModel):
    """Opening hours for a single day"""

    period: int
    date: str  # YYYY-MM-DD format
    info: Optional[str]
    closed: bool
    times: List[OpeningTime]


class LibraryData(BaseModel):
    """Complete library information from Kirjastot.fi API"""

    id: int
    city: int
    name: str
    slug: str
    type: str
    slogan: str
    address: Address
    created: str  # ISO datetime string
    founded: Optional[str]
    modified: str  # ISO datetime string
    shortName: str
    consortium: int
    coverPhoto: CoverPhoto
    coordinates: Coordinates
    description: Optional[str]
    mainLibrary: bool
    schedules: List[DaySchedule]


class RawData(BaseModel):
    """Combined raw data from multiple sources"""

    library: Optional[LibraryData] = None
    pharmacy: Optional[str] = None
    krauta: Optional[dict] = None
