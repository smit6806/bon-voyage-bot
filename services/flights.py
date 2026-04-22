# services/flights.py
# Contains logic for searching flights using SerpAPI

import os
import requests
from dotenv import load_dotenv
load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")

def search_flights(origin: str, destination: str,
                   departure_date: str, return_date: str = None,
                   adults: int = 1) -> list[dict]:
    '''
    Searches for flights using SerpAPI
    Args:
        - origin: IATA code of departure airport
        - destination: IATA code of arrival airport
        - departure_date: date of departure in YYYY-MM-DD format
        - return_date: (optional) date of return in YYYY-MM-DD format
        - adults: number of adult travelers
    Returns:
        - list of flight options with details
    '''
    is_round_trip = return_date is not None and return_date != ""
    trip_type = "1" if is_round_trip else "2"

    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": departure_date,
        "currency": "USD",
        "adults": adults,
        "api_key": SERPAPI_KEY,
        "type": trip_type,
        "deep_search": "true"
    }

    if return_date:
        params["return_date"] = return_date


    response = requests.get("https://serpapi.com/search", params=params)
    if response.status_code != 200:
        print(f"Flights API error: {response.status_code} {response.text}")
        return []

    data = response.json()
    outbound_flights = data.get("best_flights", []) or data.get("other_flights", [])

    results = []
    for f in outbound_flights[:3]:
        flight_info = f.get("flights", [{}])[0]
        stops = len(f.get("flights", [])) - 1
        results.append({
            "leg": "outbound",
            "airline": flight_info.get("airline", "Unknown"),
            "flight_number": flight_info.get("flight_number", ""),
            "departure": flight_info.get("departure_airport", {}).get("time", ""),
            "arrival": flight_info.get("arrival_airport", {}).get("time", ""),
            "duration": f.get("total_duration", ""),
            "stops": stops,
            "price": f.get("price", "N/A"),
            "return_flights": []
        })

    if is_round_trip:
        return_flights = []
        for i, f in enumerate(outbound_flights[:3]):
            return_options = f.get("return_flights", [])
            if return_options and i < len(results):
                best_return = return_options[0]
                ret_info = best_return.get("flights", [{}])[0]
                ret_stops = len(best_return.get("flights", [])) - 1
                results[i]["return_flights"] = [{
                    "airline": ret_info.get("airline", "Unknown"),
                    "flight_number": ret_info.get("flight_number", ""),
                    "departure": ret_info.get("departure_airport", {}).get("time", ""),
                    "arrival": ret_info.get("arrival_airport", {}).get("time", ""),
                    "duration": best_return.get("total_duration", ""),
                    "stops": ret_stops,
                }]
    return results