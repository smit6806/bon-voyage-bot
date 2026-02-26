import json
from pydantic import ValidationError
from agent.spec_schema import TripSpec
from agent.prompts import EXTRACTION_PROMPT
from config import client

def extract_trip_spec(messages, current_spec: TripSpec) -> TripSpec:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages + [{"role": "system", "content": EXTRACTION_PROMPT}],
            response_format={"type": "json_object"}
        )
        extracted = json.loads(response.choices[0].message.content)
        print("EXTRACTED:", extracted)  # debug
        updated = current_spec.model_dump()
        updated.update(extracted)
        result = TripSpec(**updated)
        print("RESULT:", result.model_dump())  # debug
        return result
    except (ValidationError, Exception) as e:
        print("ERROR:", e)  # debug
        return current_spec