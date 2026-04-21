import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.spec_schema import TripSpec
from agent.spec_builder import extract_trip_spec
from agent.chat import get_chat_response, TOOLS
from agent.prompts import SYSTEM_PROMPT
from agent.tool_router import get_required_tools
from app.sidebar import render_sidebar

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

# Render sidebar
render_sidebar(st.session_state.trip_spec)

# Chat interface
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            if message["content"]:
                st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Tell me about your dream trip..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Update TripSpec
    new_spec = extract_trip_spec(
        st.session_state.messages,
        st.session_state.trip_spec
    )
    st.session_state.trip_spec = new_spec
    print("TRIPSPEC:", new_spec.model_dump())  # debug

    # Check which tools are ready
    ready_tools = get_required_tools(st.session_state.trip_spec)
    print("READY TOOLS:", ready_tools)  # debug

    # Build active tools list
    active_tools = [tool for tool in TOOLS
                    if tool["function"]["name"] in ready_tools]

    # Get chat response
    with st.chat_message("assistant"):
        reply = get_chat_response(st.session_state.messages, active_tools)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()