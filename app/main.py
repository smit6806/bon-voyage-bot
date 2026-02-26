# imports and installs
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# load API key from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page config
st.set_page_config(page_title="Bon Voyage Bot", page_icon="✈️")
st.title("Bon Voyage Bot")
st.caption("Your personal AI travel planner")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful travel planning assistant called Bon Voyage Bot. Help users plan personalized trips by asking about their destination, trip length, budget, and interests. Generate detailed day-by-day itineraries."},
        {"role": "assistant", "content": "Hi! I'm Bon Voyage Bot 🌍 Where are you dreaming of traveling to?"}
    ]

# Display chat history
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