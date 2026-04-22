# services/hotels.py
# Contains logic for searching hotels using SerpAPI

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")

# Amenity codes for Google Hotels
AMENITY_CODES = {
    "pool": 35,
    "spa": 9,
    "free breakfast": 19,
    "gym": 11,
    "free wifi": 4,
    "parking": 16,
    "air conditioning": 2,
    "restaurant": 6,
    "beach access": 45,
}

LUXURY_TO_CLASS = {
    "budget": 2,
    "mid": 3,
    "high": 4,
    "luxury": 5
}

def search_hotels(destination: str, check_in_date: str,
                  check_out_date: str, adults: int = 1,
                  max_price: float = None,
                  luxury_level: str = None,
                  must_haves: list = None) -> list[dict]:
    '''
    Searches for hotels using SerpAPI
    Args:
    - destination: city or location to search in
    - check_in_date: date of check-in in YYYY-MM-DD format
    - check_out_date: date of check-out in YYYY-MM-DD format
    - adults: number of adult travelers
    - max_price: (optional) maximum price per night in USD
    - luxury_level: (optional) one of "budget", "mid", "high", "luxury"
    - must_haves: (optional) list of amenity keywords to filter by (e.g. "pool", "free breakfast")
    Returns:
    - list of hotel options with details
    '''
    params = {
        "engine": "google_hotels",
        "q": destination,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "adults": adults,
        "currency": "USD",
        "api_key": SERPAPI_KEY
    }

    # Add max price filter if budget is known
    if max_price:
        params["max_price"] = int(max_price)

    # Add hotel class based on luxury level
    if luxury_level and luxury_level in LUXURY_TO_CLASS:
        params["hotel_class"] = LUXURY_TO_CLASS[luxury_level]

    # Add amenity filters based on must haves
    if must_haves:
        amenity_ids = []
        for item in must_haves:
            for keyword, code in AMENITY_CODES.items():
                if keyword.lower() in item.lower():
                    amenity_ids.append(str(code))
        if amenity_ids:
            params["amenities"] = ",".join(amenity_ids)

    response = requests.get("https://serpapi.com/search", params=params)

    if response.status_code == 200:
        data = response.json()
        properties = data.get("properties", [])
        results = []
        for h in properties[:3]:
            results.append({
                "name": h.get("name", "Unknown"),
                "rating": h.get("overall_rating", "N/A"),
                "reviews": h.get("reviews", "N/A"),
                "price_per_night": h.get("rate_per_night", {}).get("lowest", "N/A"),
                "total_price": h.get("total_rate", {}).get("lowest", "N/A"),
                "amenities": h.get("amenities", [])[:5],
                "description": h.get("description", "")
            })
        return results
    else:
        print(f"Hotels API error: {response.status_code} {response.text}")
        return []