# services/places.py
# Contains logic for searching places using Google Places API

import requests
import os
from dotenv import load_dotenv

load_dotenv()

PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
PLACES_BASE_URL = "https://places.googleapis.com/v1/places:searchText"

def search_places(query: str, destination: str) -> list[dict]:
    '''
    Searches for places using Google Places API
    Args:
        - query: search query (e.g., "restaurants", "museums")
        - destination: city or location to search in
    Returns:
        - list of place options with details
    '''
    full_query = f"{query} in {destination}"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": PLACES_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.shortFormattedAddress,places.rating,places.priceLevel"
    }

    payload = {
        "textQuery": full_query,
        "maxResultCount": 5
    }

    response = requests.post(PLACES_BASE_URL, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get("places", [])
    
    else:
        print(f"Google Places API error: {response.status_code} - {response.text}")
        return []