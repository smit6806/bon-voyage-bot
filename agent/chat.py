from pyexpat.errors import messages

from config import client
import json
from services.places import search_places

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_places",
            "description": "Search for restaurants, beaches, attractions, hotels or activities in a destination",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What to search for e.g. 'best beaches' or 'local restaurants'"
                    },
                    "destination": {
                        "type": "string",
                        "description": "The destination to search in e.g. 'Amalfi Coast, Italy'"
                    }
                },
                "required": ["query", "destination"]
            }
        }
    }
]

def get_chat_response(messages: list) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    message = response.choices[0].message

    #check if GPT wants to call a tool
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        print(f"GPT calling tool: {tool_call.function.name} with args: {args}")

        #execute the search 
        places = search_places(args["query"], args["destination"])

        # Format results
        if places:
            places_text = "\n".join([
                f"- {p['displayName']['text']} ({p.get('shortFormattedAddress', 'Amalfi Coast')})"
                + (f" Rating: {p['rating']}" if 'rating' in p else "")
                for p in places
            ])
        else:
            places_text = "No results found."

        # send results back to GPT
        messages_with_result = messages + [
            {"role": "assistant", "content": None, "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
            ]},
            {"role": "tool", "content": places_text, "tool_call_id": tool_call.id}
        ]
        
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_with_result
        )
        return final_response.choices[0].message.content
    
    return message.content