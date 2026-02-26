import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import ValidationError
import os
import json
import sys

# Add parent directory to path so we can import from agent/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.spec_schema import TripSpec
from agent.prompts import SYSTEM_PROMPT, EXTRACTION_PROMPT

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page config
st.set_page_config(page_title="Bon Voyage Bot", page_icon="✈️")
st.title("✈️ Bon Voyage Bot")
st.caption("Your personal AI travel planner")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Hi! I'm Bon Voyage Bot 🌍 Where are you dreaming of traveling to?"}
    ]
if "trip_spec" not in st.session_state:
    st.session_state.trip_spec = TripSpec()

def extract_trip_spec(messages, current_spec: TripSpec) -> TripSpec:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages + [{"role": "system", "content": EXTRACTION_PROMPT}],
            response_format={"type": "json_object"}
        )
        extracted = json.loads(response.choices[0].message.content)
        updated = current_spec.model_dump()
        updated.update(extracted)
        return TripSpec(**updated)
    except (ValidationError, Exception):
        return current_spec

# Sidebar
with st.sidebar:
    st.header("🗺️ Your Trip So Far")
    spec = st.session_state.trip_spec

    if spec.origin.city:
        st.write(f"📍 **From:** {spec.origin.city}")
    if spec.dates.nights:
        st.write(f"🌙 **Nights:** {spec.dates.nights}")
    if spec.dates.month:
        st.write(f"📅 **Month:** {spec.dates.month}")
    if spec.travelers.adults:
        st.write(f"👤 **Travelers:** {spec.travelers.adults} adults")
        if spec.travelers.children > 0:
            st.write(f"👶 **Children:** {spec.travelers.children}")

    st.divider()
    st.subheader("💰 Budget Tracker")
    if spec.budget.total_usd:
        st.metric("Total Budget", f"${spec.budget.total_usd:,.0f}")
    if spec.budget.flight_max_usd:
        st.metric("Flight Budget", f"${spec.budget.flight_max_usd:,.0f}")
    if spec.budget.lodging_per_night_max_usd:
        st.metric("Hotel/Night", f"${spec.budget.lodging_per_night_max_usd:,.0f}")
    if not spec.budget.total_usd:
        st.caption("Budget details will appear as you chat!")

    if spec.preferences.trip_type:
        st.divider()
        st.subheader("✨ Preferences")
        st.write(", ".join(spec.preferences.trip_type))
    if spec.must_haves:
        st.subheader("✅ Must Haves")
        for item in spec.must_haves:
            st.write(f"• {item}")
    if spec.dealbreakers:
        st.subheader("🚫 Dealbreakers")
        for item in spec.dealbreakers:
            st.write(f"• {item}")

# Chat interface
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Tell me about your dream trip..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )
        reply = response.choices[0].message.content
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.trip_spec = extract_trip_spec(
        st.session_state.messages, 
        st.session_state.trip_spec
    )
    st.rerun()