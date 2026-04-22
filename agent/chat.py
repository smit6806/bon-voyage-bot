# agent/chat.py
# Core chat engine for Bon Voyage Bot

import json
from datetime import datetime
from config import client
from services.places import search_places
from services.flights import search_flights
from services.hotels import search_hotels

# used in tool descriptions to prevent LLM from using past dates
TODAY = datetime.now().strftime("%Y-%m-%d")

# tool definitions passed to the LLM on every chat request, based on availability defined in tool_router
TOOLS = [
    {"type": "function", "function": {
        "name": "search_places",
        "description": "Search for restaurants, beaches, attractions or activities. Always include the country in the destination",
        "parameters": {"type": "object",
            "properties": {
                "query": {"type": "string"},
                "destination": {"type": "string", "description": "Always include country"}
            },
            "required": ["query", "destination"]
        }
    }},
    {"type": "function", "function": {
        "name": "search_flights",
        "description": (
            f"Search for flights. Today is {TODAY}. Never use a past departure date. "
            "Always assume a round trip flight, unless the user specifies one way, always make a SINGLE call with both departure_date AND return_date. "
            "Never call this tool twice for the two legs of a round trip."
        ),
        "parameters": {"type": "object",
            "properties": {
                "origin": {"type": "string", "description": "Origin airport code e.g. BNA"},
                "destination": {"type": "string", "description": "Destination airport code e.g. SAN"},
                "departure_date": {"type": "string", "description": f"Outbound departure date YYYY-MM-DD. Must be {TODAY} or later."},
                "return_date": {"type": "string", "description": "Return date YYYY-MM-DD. Always include unless user specfies one way trip."},
                "adults": {"type": "integer", "description": "Number of adult travelers"}
            },
            "required": ["origin", "destination", "departure_date"]
        }
    }},
    {"type": "function", "function": {
        "name": "search_hotels",
        "description": f"Search for hotels at a single specific location. Always include the country. Search one location at a time only. Today is {TODAY}. Never use a check-in date in the past.",
        "parameters": {"type": "object",
            "properties": {
                "destination": {"type": "string", "description": "Single hotel location including country"},
                "check_in_date": {"type": "string", "description": f"Check-in date YYYY-MM-DD. Must be {TODAY} or later."},
                "check_out_date": {"type": "string", "description": "Check-out date YYYY-MM-DD"},
                "adults": {"type": "integer", "description": "Number of adult travelers"},
                "max_price": {"type": "number", "description": "Maximum price per night in USD"},
                "luxury_level": {"type": "string", "description": "Luxury level: budget, mid, high, or luxury"}
            },
            "required": ["destination", "check_in_date", "check_out_date"]
        }
    }}
]


def is_past_date(date_str: str) -> bool:
    '''
    returns True if given YYYY-MM-DD date string is in the past relative to today
    '''
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date() < datetime.now().date()
    except Exception:
        return False


def clean_price(price) -> str:
    '''
    Cleans a price string by removing dollar signs and commas, and trimming whitespace
    Error handling for LaTeX / markdown formatting
    '''
    return str(price).replace("$", "").replace(",", "").strip()


def execute_tool(tool_name: str, args: dict) -> str:
    '''
    Executes the specified tool
    Args:
        - tool_name: name of the tool to execute
        - args: dictionary of arguments to pass to the tool
    Returns:
        - string result to return to the LLM after executing the tool
    '''
    if tool_name == "search_places":
        results = search_places(args["query"], args["destination"])
        if results:
            return "\n".join([
                f"- {p['displayName']['text']} ({p.get('shortFormattedAddress', '')})"
                + (f" Rating: {p['rating']}" if 'rating' in p else "")
                for p in results
            ])
        return "No places found."

    elif tool_name == "search_flights":
        departure_date = args["departure_date"]
        if is_past_date(departure_date):
            return f"Error: departure_date {departure_date} is in the past. Please use a future date."
        results = search_flights(
            origin=args["origin"],
            destination=args["destination"],
            departure_date=departure_date,
            return_date=args.get("return_date"),
            adults=args.get("adults", 1)
        )
        if results:
            is_round_trip = bool(args.get("return_date"))
            trip_type = "Round trip" if is_round_trip else "One way"
            flights_text = f"Trip type: {trip_type}\n"
            for r in results:
                flights_text += (
                    f"- Outbound: {r['airline']} {r['flight_number']} | "
                    f"Departs: {r['departure']} | "
                    f"Arrives: {r['arrival']} | "
                    f"Stops: {r['stops']} | "
                    f"Duration: {r['duration']} mins | "
                    f"Price: USD {clean_price(r['price'])}\n"
                )
                for ret in r.get("return_flights", []):
                    flights_text += (
                        f"  Return: {ret['airline']} {ret['flight_number']} | "
                        f"Departs: {ret['departure']} | "
                        f"Arrives: {ret['arrival']} | "
                        f"Stops: {ret['stops']} | "
                        f"Duration: {ret['duration']} mins\n"
                    )
            flights_text += (
                "\nINSTRUCTIONS: You MUST present both outbound AND return flight details "
                "for every option in your very first response. Never omit return flight details. "
                "All times are in origin city local timezone, convert arrival times to destination timezone."
                "Present prices as 'USD X' not '$X'. Price is total round trip cost per person."
            )
            return flights_text
        return "No flights found."

    elif tool_name == "search_hotels":
        check_in_date = args["check_in_date"]
        if is_past_date(check_in_date):
            return f"Error: check_in_date {check_in_date} is in the past. Please use a future date."
        results = search_hotels(
            destination=args["destination"],
            check_in_date=check_in_date,
            check_out_date=args["check_out_date"],
            adults=args.get("adults", 1),
            max_price=args.get("max_price"),
            luxury_level=args.get("luxury_level")
        )
        if results:
            hotels_text = "\n".join([
                f"- {r['name']} | "
                f"Rating: {r['rating']} | "
                f"Per night: USD {clean_price(r['price_per_night'])} | "
                f"Total: USD {clean_price(r['total_price'])} | "
                f"Amenities: {', '.join(r['amenities'][:3]) if r['amenities'] else 'N/A'}"
                for r in results
            ])
            hotels_text += "\n\nPresent all prices as 'USD X' not '$X'."
            return hotels_text
        return "No hotels found."

    return "Tool not found."


def get_chat_response(messages: list, tools: list = None) -> str:
    '''
    Sends the conversation to GPT-4o and returns the response
    If the LLM decides to call a tool, executes the tool and sends the result back to the LLM for a final response
    '''
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools if tools else None,
        tool_choice="auto" if tools else None
    )

    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        tool_name = tool_call.function.name

        result = execute_tool(tool_name, args)

        messages_with_result = messages + [
            {"role": "assistant", "content": None, "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": tool_call.function.arguments
                    }
                }
            ]},
            {"role": "tool", "content": result, "tool_call_id": tool_call.id}
        ]

        final_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages_with_result
        )
        return final_response.choices[0].message.content

    return message.content