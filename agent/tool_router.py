# agent/tool_router.py
from agent.spec_schema import TripSpec

def get_required_tools(spec: TripSpec) -> list[str]:
    tools = []
    
    has_origin = bool(spec.origin.city)
    has_destination = bool(spec.destination.city)
    has_dates = spec.dates.nights is not None
    has_budget = spec.budget.total_usd is not None
    has_travelers = spec.travelers.adults > 0

    # Google Places API - only needs destination
    if has_destination:
        tools.append("search_places")
    
    # OpenWeatherMap API - needs destination and dates
    if has_destination and has_dates:
        tools.append("weather")
    
    # Flights - needs origin, destination, dates, budget, travelers
    if has_origin and has_destination and has_dates and has_budget and has_travelers:
        tools.append("search_flights")
    
    # Hotels - needs destination, dates, and budget
    if has_destination and has_dates and has_budget:
        tools.append("search_hotels")
    
    return tools