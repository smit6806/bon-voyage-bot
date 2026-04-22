# app/main.py
# Entry point for the Bon Voyage Bot Streamlit application.

import streamlit as st
import streamlit.components.v1 as components
import os
import sys
import threading
import queue

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.spec_schema import TripSpec
from agent.spec_builder import extract_trip_spec
from agent.chat import get_chat_response, TOOLS
from agent.prompts import SYSTEM_PROMPT
from agent.tool_router import get_required_tools
from agent.itinerary_schema import Itinerary
from agent.itinerary_builder import update_itinerary
from app.sidebar import render_sidebar
from app.itinerary_tab import render_itinerary_tab


st.set_page_config(page_title="Bon Voyage Bot", page_icon="✈️")

header_col, reset_col = st.columns([6, 1])
with header_col:
    st.title("✈️ Bon Voyage Bot")
    st.caption("Your personal AI travel planner")
with reset_col:
    st.write("") 
    if st.button("Reset", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


if "itinerary_queue" not in st.session_state:
    st.session_state.itinerary_queue = queue.Queue()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Hi! I'm Bon Voyage Bot. Where are you dreaming of traveling to?"}
    ]
if "trip_spec" not in st.session_state:
    st.session_state.trip_spec = TripSpec()
if "itinerary" not in st.session_state:
    st.session_state.itinerary = Itinerary()
if "itinerary_generating" not in st.session_state:
    st.session_state.itinerary_generating = False


def run_itinerary_update(messages: list, current_itinerary: Itinerary, result_queue: queue.Queue):
    '''
    Runs in a background daemon thread after every user message
    Generates an updated Itinerary and puts it in the result queue
    '''
    result = update_itinerary(messages, current_itinerary)
    result_queue.put(result)


def scroll_to_bottom():
    '''
    Injects a small JavaScript snippet to scroll the chat container
    to the latest message after each rerun (error handling)
    '''
    components.html(
        """
        <script>
            window.parent.document.querySelectorAll('[data-testid="stChatMessageContainer"]').forEach(el => {
                el.scrollTop = el.scrollHeight;
            });
            const blocks = window.parent.document.querySelectorAll('.main .block-container');
            blocks.forEach(el => { el.scrollTop = el.scrollHeight; });
        </script>
        """,
        height=0
    )


try:
    result = st.session_state.itinerary_queue.get_nowait()
    st.session_state.itinerary = result
    st.session_state.itinerary_generating = False
except queue.Empty:
    pass

render_sidebar(st.session_state.trip_spec, st.session_state.itinerary)


chat_tab, itinerary_tab = st.tabs(["Chat", "Itinerary"])

with chat_tab:
    # Render full conversation history, skipping the system prompt
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                if message["content"]:
                    st.markdown(message["content"])
    scroll_to_bottom()

with itinerary_tab:
    render_itinerary_tab()


if prompt := st.chat_input("Tell me about your dream trip..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with chat_tab:
        with st.chat_message("user"):
            st.markdown(prompt)

        # Update TripSpec from the latest conversation
        new_spec = extract_trip_spec(
            st.session_state.messages,
            st.session_state.trip_spec
        )
        st.session_state.trip_spec = new_spec

        # Determine which tools are available given the current TripSpec
        ready_tools = get_required_tools(st.session_state.trip_spec)

        # Filter TOOLS list to only those that are ready
        active_tools = [tool for tool in TOOLS
                        if tool["function"]["name"] in ready_tools]

        # Get and display assistant response
        with st.chat_message("assistant"):
            reply = get_chat_response(st.session_state.messages, active_tools)
            st.markdown(reply)

        scroll_to_bottom()

    st.session_state.messages.append({"role": "assistant", "content": reply})

    
    st.session_state.itinerary_generating = True
    messages_snapshot = list(st.session_state.messages)
    itinerary_snapshot = st.session_state.itinerary
    thread = threading.Thread(
        target=run_itinerary_update,
        args=(messages_snapshot, itinerary_snapshot, st.session_state.itinerary_queue),
        daemon=True
    )
    thread.start()

    st.rerun()