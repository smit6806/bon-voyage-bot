# agent/itinerary_builder.py
# Contains logic for extracting structured itinerary information from conversation history

import json
import re
from config import client
from agent.itinerary_schema import Itinerary, ActionItem
from agent.prompts import ACTION_ITEMS_PROMPT, NARRATIVE_PROMPT
from pydantic import ValidationError


def update_itinerary(messages: list, current_itinerary: Itinerary) -> Itinerary:
    '''
    Rebuilds the itinerary from the full conversation history 
    Args:
        - messages: full conversation history as list of dicts with 'role' and 'content'
        - current_itinerary: the current Itinerary object to update
    Returns:
        - updated Itinerary object with new action items and narrative extracted from conversation
    '''
    try:
        # Call 1: extract action items and summary as JSON
        action_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages + [{"role": "system", "content": ACTION_ITEMS_PROMPT}],
            response_format={"type": "json_object"}
        )
        extracted = json.loads(action_response.choices[0].message.content)
        action_items = [ActionItem(**item) for item in extracted.get("action_items", [])]
        summary = extracted.get("summary")

        # Call 2: generate free-form narrative markdown
        narrative_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages + [{"role": "system", "content": NARRATIVE_PROMPT}]
        )
        narrative = narrative_response.choices[0].message.content
        narrative = re.sub(r'^```\w*\s*\n?', '', narrative)
        narrative = re.sub(r'```\s*$', '', narrative)
        narrative = narrative.strip()

        return Itinerary(
            action_items=action_items,
            summary=summary,
            narrative=narrative
        )

    except (ValidationError, Exception) as e:
        print(f"Itinerary update error: {e}")
        return current_itinerary