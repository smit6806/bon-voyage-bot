# services/weather.py
# Contains logic for getting historical weather using Open-Meteo's climate API

import requests
import calendar

def get_historical_weather(destination: str, month: int) :
    """
    Get average historical weather for a destination and month
    using Open-Meteo's climate API.
    """
    # Geocode the destination to lat/lng
    geo_response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": destination, "count": 1, "language": "en", "format": "json"}
    )
    if geo_response.status_code != 200:
        return None

    geo_data = geo_response.json()
    results = geo_data.get("results")
    if not results:
        return None

    lat = results[0]["latitude"]
    lng = results[0]["longitude"]
    location_name = results[0].get("name", destination)

    # Use a recent representative year for historical normals
    year = 2023
    month_str = f"{month:02d}"
    last_day = calendar.monthrange(year, month)[1]
    start_date = f"{year}-{month_str}-01"
    end_date = f"{year}-{month_str}-{last_day}"

    climate_response = requests.get(
        "https://climate-api.open-meteo.com/v1/climate",
        params={
            "latitude": lat,
            "longitude": lng,
            "start_date": start_date,
            "end_date": end_date,
            "models": "EC_Earth3P_HR",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum"
        }
    )

    if climate_response.status_code != 200:
        return None

    data = climate_response.json()
    daily = data.get("daily", {})

    temps_max = [t for t in daily.get("temperature_2m_max", []) if t is not None]
    temps_min = [t for t in daily.get("temperature_2m_min", []) if t is not None]
    precip = [p for p in daily.get("precipitation_sum", []) if p is not None]

    if not temps_max or not temps_min:
        return None

    avg_high_c = sum(temps_max) / len(temps_max)
    avg_low_c = sum(temps_min) / len(temps_min)
    avg_precip = sum(precip) / len(precip) if precip else 0

    avg_high_f = (avg_high_c * 9/5) + 32
    avg_low_f = (avg_low_c * 9/5) + 32

    if avg_precip > 5:
        condition = "Rainy"
    elif avg_precip > 2:
        condition = "Some rain expected"
    elif avg_high_c > 28:
        condition = "Hot and sunny"
    elif avg_high_c > 20:
        condition = "Warm and pleasant"
    elif avg_high_c > 12:
        condition = "Mild"
    else:
        condition = "Cool"

    return {
        "location": location_name,
        "avg_high_f": round(avg_high_f),
        "avg_low_f": round(avg_low_f),
        "avg_high_c": round(avg_high_c),
        "avg_low_c": round(avg_low_c),
        "condition": condition,
        "avg_daily_precip_mm": round(avg_precip, 1)
    }