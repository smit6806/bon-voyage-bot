# agent/itinerary_builder.py
import json
from config import client
from agent.itinerary_schema import Itinerary
from agent.prompts import ITINERARY_PROMPT
from pydantic import ValidationError

def update_itinerary(messages: list, current_itinerary: Itinerary) -> Itinerary:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages + [{"role": "system", "content": ITINERARY_PROMPT}],
            response_format={"type": "json_object"}
        )
        extracted = json.loads(response.choices[0].message.content)
        updated = current_itinerary.model_dump()
        updated.update(extracted)
        return Itinerary(**updated)
    except (ValidationError, Exception) as e:
        print(f"Itinerary update error: {e}")
        return current_itinerary