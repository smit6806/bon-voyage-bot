from typing import Optional, Union
from pydantic import BaseModel

class Origin(BaseModel):
    city: str = ""
    airport_code: str = ""

class Destination(BaseModel):
    city: str = ""
    country: str = ""
    region: str = ""

class Dates(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    month: Optional[Union[str, int]] = None
    year: Optional[int] = None
    nights: Optional[int] = None
    date_flexibility_days: Optional[int] = None

class Travelers(BaseModel):
    adults: int = 1
    children: int = 0

class Budget(BaseModel):
    total_usd: Optional[float] = None
    flight_max_usd: Optional[float] = None
    lodging_per_night_max_usd: Optional[float] = None

class Preferences(BaseModel):
    trip_type: list[str] = []
    pace: Optional[str] = None
    food_focus: Optional[str] = None
    luxury_level: Optional[str] = None

class TripSpec(BaseModel):
    origin: Origin = Origin()
    destination: Destination = Destination() 
    dates: Dates = Dates()
    travelers: Travelers = Travelers()
    budget: Budget = Budget()
    preferences: Preferences = Preferences()
    must_haves: list[str] = []
    dealbreakers: list[str] = []
    notes: Optional[str] = None