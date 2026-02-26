import streamlit as st
from agent.spec_schema import TripSpec

def render_sidebar(spec: TripSpec):
    with st.sidebar:
        st.header("Your Trip So Far")

        if spec.origin.city:
            st.write(f"**From:** {spec.origin.city}")
        if spec.dates.nights:
            st.write(f"**Nights:** {spec.dates.nights}")
        if spec.dates.month:
            st.write(f"**Month:** {spec.dates.month}")
        if spec.travelers.adults:
            st.write(f"**Travelers:** {spec.travelers.adults} adults")
            if spec.travelers.children > 0:
                st.write(f"**Children:** {spec.travelers.children}")

        st.divider()
        st.subheader("Budget Tracker")
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