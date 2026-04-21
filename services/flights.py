# services/flights.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")

def search_flights(origin: str, destination: str,
                   departure_date: str, return_date: str = None,
                   adults: int = 1) -> list[dict]:
    
    trip_type = "1" if (return_date is not None and return_date != "") else "2"
    
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": departure_date,
        "currency": "USD",
        "adults": adults,
        "api_key": SERPAPI_KEY,
        "type": trip_type
    }
    
    if return_date:
        params["return_date"] = return_date
    
    print("PARAMS:", params)  # debug - remove later
    
    response = requests.get("https://serpapi.com/search", params=params)
    
    if response.status_code == 200:
        data = response.json()
        flights = data.get("best_flights", []) or data.get("other_flights", [])
        results = []
        for f in flights[:3]:
            flight_info = f.get("flights", [{}])[0]
            stops = len(f.get("flights", [])) - 1
            results.append({
                "airline": flight_info.get("airline", "Unknown"),
                "flight_number": flight_info.get("flight_number", ""),
                "departure": flight_info.get("departure_airport", {}).get("time", ""),
                "arrival": flight_info.get("arrival_airport", {}).get("time", ""),
                "duration": f.get("total_duration", ""),
                "stops": stops,
                "price": f.get("price", "N/A")
            })
        return results
    else:
        print(f"Flights API error: {response.status_code} {response.text}")
        return []