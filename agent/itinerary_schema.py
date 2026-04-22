# agent/itinerary_schema.py
# Defines the Itinerary schema which represents the structured itinerary information


from typing import Optional, Literal
from pydantic import BaseModel


class ActionItem(BaseModel):
    '''
    A single booking or task that the user needs to complete as part of their trip planning
    '''
    task: str = ""
    category: Literal["flight", "hotel", "activity", "other"] = "other"


class Itinerary(BaseModel):
    '''
    The fulll itinerary document, including a list of action items and a free-form narrative description
    '''
    action_items: list[ActionItem] = []
    narrative: Optional[str] = None
    summary: Optional[str] = None