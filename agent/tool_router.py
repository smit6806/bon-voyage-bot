# agent/tool_router.py
from agent.spec_schema import TripSpec

def get_required_tools(spec: TripSpec) -> list[str]:
    tools = []
    
    has_destination = spec.destination.city != ""
    has_dates = spec.dates.nights is not None
    has_budget = spec.budget.total_usd is not None
    has_travelers = spec.travelers.adults > 0

    # Google Places — just needs a destination
    if has_destination:
        tools.append("google_places")
    
    # Weather — needs destination and dates
    if has_destination and has_dates:
        tools.append("weather")
    
    # Flights — needs origin, dates, budget, and travelers
    if has_destination and has_dates and has_budget and has_travelers:
        tools.append("flights")
    
    # Hotels — needs destination, dates, and budget
    if has_destination and has_dates and has_budget:
        tools.append("hotels")
    
    return tools
