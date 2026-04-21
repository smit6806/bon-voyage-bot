# agent/itinerary_schema.py
from typing import Optional
from pydantic import BaseModel

class TodoItem(BaseModel):
    task: str = ""
    completed: bool = False
    category: str = ""  # "flight", "hotel", "activity", "other"

class DayPlan(BaseModel):
    day_number: int = 0
    date: Optional[str] = None
    location: str = ""
    morning: Optional[str] = None
    afternoon: Optional[str] = None
    evening: Optional[str] = None
    accommodation: Optional[str] = None
    notes: Optional[str] = None

class Itinerary(BaseModel):
    todo_items: list[TodoItem] = []
    days: list[DayPlan] = []
    summary: Optional[str] = None