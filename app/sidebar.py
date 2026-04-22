# app/sidebar.py
# Contains logic for rendering the sidebar with trip summary, weather, and budget info

import streamlit as st
from agent.spec_schema import TripSpec
from agent.itinerary_schema import Itinerary
from agent.budget_tracker import get_confirmed_spend
from services.weather import get_historical_weather


MONTH_TO_INT = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12
}

def get_month_int(spec: TripSpec) :
    if spec.dates.start_date:
        try:
            return int(spec.dates.start_date.split("-")[1])
        except Exception:
            pass
    if spec.dates.month:
        return MONTH_TO_INT.get(spec.dates.month.lower())
    return None


def render_sidebar(spec: TripSpec, itinerary: Itinerary = None):
    with st.sidebar:
        st.header("Your Trip So Far")

        # Origin and destination
        if spec.origin.city:
            st.write(f"**From:** {spec.origin.city}")

        if spec.destination.city:
            dest = spec.destination.city
            if spec.destination.country:
                dest += f", {spec.destination.country}"
            st.write(f"**To:** {dest}")

        # Dates and travelers
        if spec.dates.start_date and spec.dates.end_date:
            st.write(f"**Dates:** {spec.dates.start_date} to {spec.dates.end_date}")
        elif spec.dates.month:
            month_str = spec.dates.month
            if spec.dates.year:
                month_str += f" {spec.dates.year}"
            st.write(f"**Month:** {month_str}")

        if spec.dates.nights:
            st.write(f"**Nights:** {spec.dates.nights}")

        if spec.travelers.adults:
            traveler_str = f"{spec.travelers.adults} adult{'s' if spec.travelers.adults > 1 else ''}"
            if spec.travelers.children > 0:
                traveler_str += f", {spec.travelers.children} child{'ren' if spec.travelers.children > 1 else ''}"
            st.write(f"**Travelers:** {traveler_str}")

        # Multi-city segments - only show if more than one location
        if len(spec.stay_segments) > 1:
            st.divider()
            st.subheader("Destinations")
            for segment in spec.stay_segments:
                if segment.location:
                    line = f"**{segment.location}**"
                    if segment.nights:
                        line += f" — {segment.nights} nights"
                    st.write(line)
                    if segment.check_in and segment.check_out:
                        st.caption(f"{segment.check_in} → {segment.check_out}")

        # Weather
        if spec.destination.city:
            month_int = get_month_int(spec)
            if month_int:
                weather_key = f"weather_{spec.destination.city}_{month_int}"
                if weather_key not in st.session_state:
                    with st.spinner("Loading weather..."):
                        st.session_state[weather_key] = get_historical_weather(
                            spec.destination.city, month_int
                        )
                weather = st.session_state.get(weather_key)
                if weather:
                    st.divider()
                    st.subheader("Typical Weather")
                    st.caption(weather['condition'])
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("High", f"{weather['avg_high_f']}F")
                    with col2:
                        st.metric("Low", f"{weather['avg_low_f']}F")
                    if weather['avg_daily_precip_mm'] > 0:
                        st.caption(f"Avg daily rainfall: {weather['avg_daily_precip_mm']}mm")

        # Budget
        st.divider()
        st.subheader("Budget")
        spend = get_confirmed_spend(itinerary) if itinerary else {"flights": 0, "hotels": 0, "activities": 0, "total": 0}

        if spec.budget.total_usd:
            remaining = spec.budget.total_usd - spend["total"]
            st.metric("Total Budget", f"${spec.budget.total_usd:,.0f}")
            if spend["total"] > 0:
                st.metric("Planned", f"${spend['total']:,.0f}", delta=f"-${spend['total']:,.0f}", delta_color="inverse")
                st.metric("Remaining", f"${remaining:,.0f}")
                if spend["flights"] > 0:
                    st.caption(f"Flights: ${spend['flights']:,.0f}")
                if spend["hotels"] > 0:
                    st.caption(f"Hotels: ${spend['hotels']:,.0f}")
                if spend["activities"] > 0:
                    st.caption(f"Activities: ${spend['activities']:,.0f}")
        elif spend["total"] > 0:
            st.metric("Planned so far", f"${spend['total']:,.0f}")
        else:
            st.caption("Budget details will appear as you chat!")

        # Preferences
        if spec.preferences.trip_type:
            st.divider()
            st.subheader("Preferences")
            st.write(", ".join(spec.preferences.trip_type))

        if spec.must_haves:
            st.subheader("Must Haves")
            for item in spec.must_haves:
                st.write(f"• {item}")

        if spec.dealbreakers:
            st.subheader("Dealbreakers")
            for item in spec.dealbreakers:
                st.write(f"• {item}")