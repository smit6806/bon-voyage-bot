#agent/spec_schema.py
# Defines the data models for the trip specification using Pydantic for validation and parsing.

from typing import Optional, Union
from pydantic import BaseModel

class Origin(BaseModel):
    '''
    Where the user is traveling from
    '''
    city: str = ""
    airport_code: str = ""

class Destination(BaseModel):
    '''
    Where the user is traveling to
    '''
    city: str = ""
    country: str = ""
    region: str = ""

class StaySegment(BaseModel):
    '''
    Represents one stop in a multi-city trip
    '''
    location: str = ""
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    nights: Optional[int] = None

class Dates(BaseModel):
    '''
    Travel date information
    '''
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    month: Optional[Union[str, int]] = None
    year: Optional[int] = None
    nights: Optional[int] = None
    date_flexibility_days: Optional[int] = None

class Travelers(BaseModel):
    '''
    Number and type of travelers
    '''
    adults: int = 1
    children: int = 0

class Budget(BaseModel):
    '''
    Budget constraints. All values in USD. Fields None if not specified.
    '''
    total_usd: Optional[float] = None
    flight_max_usd: Optional[float] = None
    lodging_per_night_max_usd: Optional[float] = None

class Preferences(BaseModel):
    '''
    User preferences and priorities
    '''
    trip_type: list[str] = []
    pace: Optional[str] = None
    food_focus: Optional[str] = None
    luxury_level: Optional[str] = None

class TripSpec(BaseModel):
    '''
    Full structured representation of user's trip
    Populated incrementally as the user shares details in conversation
    '''
    origin: Origin = Origin()
    destination: Destination = Destination()
    dates: Dates = Dates()
    travelers: Travelers = Travelers()
    budget: Budget = Budget()
    preferences: Preferences = Preferences()
    stay_segments: list[StaySegment] = []
    must_haves: list[str] = []
    dealbreakers: list[str] = []
    notes: Optional[str] = None