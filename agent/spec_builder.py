#agent/spec_builder.py
# Contains logic for extracting and updating TripSpec from conversation history

import json
from pydantic import ValidationError
from agent.spec_schema import TripSpec
from agent.prompts import EXTRACTION_PROMPT
from config import client

def extract_trip_spec(messages, current_spec: TripSpec) -> TripSpec:
    '''
    Extracts updated trip details from conversation history and merges with current TripSpec schema

    Args:
        - messages: full conversation history as list of dicts with 'role' and 'content'
        - current_spec: the current TripSpec object to update
    Returns:
        - Updated TripSpec object with new details extracted from conversation

    Falls back to current trip spec unchanged if extraction fails
    '''
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages + [{"role": "system", "content": EXTRACTION_PROMPT}],
            response_format={"type": "json_object"}
        )
        extracted = json.loads(response.choices[0].message.content)
        updated = current_spec.model_dump()
        updated.update(extracted)
        result = TripSpec(**updated)
        return result
    except (ValidationError, Exception) as e:
        return current_spec