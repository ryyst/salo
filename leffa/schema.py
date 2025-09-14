from typing import List, Dict, Optional
from pydantic import BaseModel


class MovieShow(BaseModel):
    id: str
    title: str
    start_time: str
    klo: str
    room_title: str
    duration: str
    age_limit: str
    price: str
    genre: Optional[str] = None
    director: Optional[str] = None
    intro: Optional[str] = None
    poster_url: Optional[str] = None
    note: Optional[str] = None
    release_year: Optional[str] = None


class Movie(BaseModel):
    id: str
    title: str
    shows: List[MovieShow]
    genre: Optional[str] = None
    director: Optional[str] = None
    intro: Optional[str] = None
    poster_url: Optional[str] = None
    duration: Optional[str] = None
    age_limit: Optional[str] = None
    release_year: Optional[str] = None


class LeffaData(BaseModel):
    movies: List[Movie]
    updated_timestamp: str
