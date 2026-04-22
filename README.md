# Bon Voyage Bot 

An AI-powered travel planning assistant built with Streamlit and GPT-4o-mini. Bon Voyage Bot helps users plan personalized trips through natural language conversation by gathering trip details, searching for real flights and hotels, and generating a downloadable itinerary document

## Access Application
[Launch Bon Voyage Bot](https://bon-voyage-bot.streamlit.app)

## Features
- Conversational trip planning with a context-aware AI assistant
- Real-time flight search via SerpAPI (Google Flights)
- Real-time hotel search via SerpAPI (Google Hotels)
- Place and restaurant recommendations via Google Places API
- Historical weather data for travel dates via Open-Meteo
- Live itinerary document that bulids in the background as user chats
- Budget tracker that updates as flights, hotels, and activities are added to itinerary
- Downloadable itinerary as a PDF file
- Multi-city trip support

## Project Structure
```
bon-voyage-bot/
├── app/
│   ├── main.py              # App entry point, chat loop, session state, tab layout
│   ├── sidebar.py           # Sidebar rendering (trip summary, weather, budget, bookings)
│   └── itinerary_tab.py     # Itinerary tab rendering and PDF download
├── agent/
│   ├── chat.py              # LLM chat response, tool definitions, tool execution
│   ├── prompts.py           # System prompt and extraction prompts
│   ├── spec_schema.py       # Pydantic schema for TripSpec (structured trip data)
│   ├── spec_builder.py      # Extracts and updates TripSpec from conversation
│   ├── tool_router.py       # Determines which tools are available based on TripSpec
│   ├── itinerary_schema.py  # Pydantic schema for Itinerary (action items + narrative)
│   ├── itinerary_builder.py # Generates itinerary document from conversation in background
│   └── budget_tracker.py    # Parses confirmed spend from itinerary action items
├── services/
│   ├── flights.py           # SerpAPI Google Flights integration
│   ├── hotels.py            # SerpAPI Google Hotels integration
│   ├── places.py            # Google Places API integration
│   └── weather.py           # Open-Meteo climate API integration
├── config.py                # OpenAI client initialization
├── requirements.txt         # Python dependencies
└── .env                     # API keys (not committed to version control)
```
## How it Works
Bon Voyage Bot is built around two data structures that get updated throughout the conversation:

**TripSpec** - A structured Pydantic model that tracks the key logistics of the trip: origin, destination, dates, travelers, budget, and preferences. After every user message, a lightweight LLM call extracts and updates the spec from the conversation. The spec determines which external API tools are available to the assistant.

**Itinerary** - A document that builds in the background as the user chats. After every user message, a background thread runs two LLM calls: one to extract confirmed action items including flights, hotels, and activities as structured data for budget tracking, and one to write a free-form markdown of the itinerary based on everything discussed so far in the conversation. The user does not wait for this, it updates silently in the background and is ready when they switch to the Itinerary tab.

## Setup

### 1. Clone the repository 
```bash
git clone https://github.com/yourusername/bon-voyage-bot.git
cd bon-voyage-bot
```
 
### 2. Create a virtual environment and install dependencies
 
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
 
### 3. Set up environment variables
 
Create a `.env` file in the project root:
 
```
OPENAI_API_KEY=your_openai_api_key
SERPAPI_API_KEY=your_serpapi_api_key
GOOGLE_PLACES_API_KEY=your_google_places_api_key
```
 
### 4. Run the app
 
```bash
streamlit run app/main.py
```
 

## API Keys Required
| Service | Used For | Get It |
|---|---|---|
| OpenAI | Chat responses and data extraction | platform.openai.com |
| SerpAPI | Flight and hotel search | serpapi.com |
| Google Places | Restaurant and activity search | console.cloud.google.com |

## Deployment
This app is deployed on Streamlit Community Cloud. To deploy your own instance:

1. Push the repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set the main file path to `app/main.py`
5. Add your API keys as secrets in the Streamlit Cloud dashboard
 
## Tech Stack
 
 - **Frontend:** Streamlit
- **LLM:** GPT-4o-mini via OpenAI API
- **Flight & Hotel Search:** SerpAPI (Google Flights, Google Hotels)
- **Place Search:** Google Places API (New)
- **Weather:** Open-Meteo Climate API
- **Data Validation:** Pydantic v2
- **Language:** Python 3.9+
