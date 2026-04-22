# agent/tool_router.py
# Contains logic for determining which tools to call based on the current trip specification

from agent.spec_schema import TripSpec


def get_required_tools(spec: TripSpec) -> list[str]:
    '''
    Function to determine which tools to call based on the current trip specification. 
    Args:
        spec: The current trip specification object

    Returns:
        A list of tool names that can be passed to the LLM
    '''
    tools = []
    has_origin = bool(spec.origin.city)
    has_destination = bool(spec.destination.city)
    has_dates = spec.dates.start_date is not None or spec.dates.nights is not None
    has_travelers = spec.travelers.adults > 0

    # Google Places - only needs destination
    if has_destination:
        tools.append("search_places")

    # Weather - needs destination and dates
    if has_destination and has_dates:
        tools.append("weather")

    # Flights - needs origin, destination, dates, and travelers
    if has_origin and has_destination and has_dates and has_travelers:
        tools.append("search_flights")

    # Hotels - needs destination and dates
    if has_destination and has_dates:
        tools.append("search_hotels")

    return tools