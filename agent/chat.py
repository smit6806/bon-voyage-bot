# agent/chat.py
import json
from config import client
from services.places import search_places
from services.flights import search_flights
from services.hotels import search_hotels

TOOLS = [
    {"type": "function", "function": {
        "name": "search_places",
        "description": "Search for restaurants, beaches, attractions or activities in a destination",
        "parameters": {"type": "object",
            "properties": {
                "query": {"type": "string"},
                "destination": {"type": "string"}
            },
            "required": ["query", "destination"]
        }
    }},
    {"type": "function", "function": {
        "name": "search_flights",
        "description": "Search for flights between two airports given dates and number of travelers",
        "parameters": {"type": "object",
            "properties": {
                "origin": {"type": "string", "description": "Origin airport code e.g. BNA"},
                "destination": {"type": "string", "description": "Destination airport code e.g. FCO"},
                "departure_date": {"type": "string", "description": "Departure date in YYYY-MM-DD format"},
                "return_date": {"type": "string", "description": "Return date in YYYY-MM-DD format"},
                "adults": {"type": "integer", "description": "Number of adult travelers"}
            },
            "required": ["origin", "destination", "departure_date"]
        }
    }},
    {"type": "function", "function": {
        "name": "search_hotels",
        "description": "Search for hotels at a destination given check-in and check-out dates",
        "parameters": {"type": "object",
            "properties": {
                "destination": {"type": "string", "description": "Hotel search location e.g. Rome Italy"},
                "check_in_date": {"type": "string", "description": "Check-in date in YYYY-MM-DD format"},
                "check_out_date": {"type": "string", "description": "Check-out date in YYYY-MM-DD format"},
                "adults": {"type": "integer", "description": "Number of adult travelers"},
                "max_price": {"type": "number", "description": "Maximum price per night in USD"},
                "luxury_level": {"type": "string", "description": "Luxury level: budget, mid, high, or luxury"}
            },
            "required": ["destination", "check_in_date", "check_out_date"]
        }
    }}
]

def execute_tool(tool_name: str, args: dict) -> str:
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
        results = search_flights(
            origin=args["origin"],
            destination=args["destination"],
            departure_date=args["departure_date"],
            return_date=args.get("return_date"),
            adults=args.get("adults", 1)
        )
        if results:
            return "\n".join([
                f"- {r['airline']} {r['flight_number']} | "
                f"Departs: {r['departure']} | "
                f"Stops: {r['stops']} | "
                f"Duration: {r['duration']} mins | "
                f"Price: ${r['price']}"
                for r in results
            ])
        return "No flights found."

    elif tool_name == "search_hotels":
        results = search_hotels(
            destination=args["destination"],
            check_in_date=args["check_in_date"],
            check_out_date=args["check_out_date"],
            adults=args.get("adults", 1),
            max_price=args.get("max_price"),
            luxury_level=args.get("luxury_level")
        )
        if results:
            return "\n".join([
                f"- {r['name']} | "
                f"Rating: {r['rating']} | "
                f"Per night: {r['price_per_night']} | "
                f"Total: {r['total_price']}"
                for r in results
            ])
        return "No hotels found."

    return "Tool not found."

def get_chat_response(messages: list, tools: list = None) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools if tools else None,
        tool_choice="auto" if tools else None
    )

    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        tool_name = tool_call.function.name

        print(f"GPT calling tool: {tool_name} with args: {args}")

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
            model="gpt-4o-mini",
            messages=messages_with_result
        )
        return final_response.choices[0].message.content

    return message.content