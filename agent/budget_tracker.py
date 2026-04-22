# agent/budget_tracker.py
# Contains logic for extracting confirmed spend information from the itinerary

import re
from agent.itinerary_schema import Itinerary


def extract_price_from_text(text: str):
    '''
    Extracts a price from a given text string
    Returns the price as a float, or None if no price is found
    '''
    match = re.search(r'USD\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
    if not match:
        match = re.search(r'\$\s*([\d,]+\.?\d*)', text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None


def get_confirmed_spend(itinerary: Itinerary) -> dict:
    '''
    sums confirmed flight and hotel spend from itinerary action items

    Args:
        itinerary: the Itinerary object containing action items with task descriptions and categories
    Returns:
        dict with total spend for flights, hotels, activities, and overall total
    '''
    flight_spend = 0.0
    hotel_spend = 0.0
    activities_spend = 0.0

    for item in itinerary.action_items:
        price = extract_price_from_text(item.task)
        if price:
            if item.category == "flight":
                flight_spend += price
            elif item.category == "hotel":
                hotel_spend += price
            else:
                activities_spend += price

    return {
        "flights": flight_spend,
        "hotels": hotel_spend,
        "activities": activities_spend,
        "total": flight_spend + hotel_spend + activities_spend
    }