# app/itinerary_tab.py
# Renders the Itinerary tab in the main application.

import io
import re
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from agent.itinerary_schema import Itinerary


def itinerary_to_markdown(itinerary: Itinerary) -> str:
    '''
    Assembles the full itinerary as a single markdown string for display
    Args:
        itinerary: The current Itinerary object.
    Returns:
        A markdown string combining summary, action items, and narrative.
    '''
    lines = []

    if itinerary.summary:
        lines.append(f"_{itinerary.summary}_\n")

    if itinerary.action_items:
        lines.append("## Action Items\n")
        for item in itinerary.action_items:
            lines.append(f"- [ ] {item.task}")
        lines.append("")

    if itinerary.narrative:
        lines.append(itinerary.narrative)

    return "\n".join(lines)


def itinerary_to_pdf(itinerary: Itinerary) -> bytes:
    '''
    Converts the itinerary to a formatted PDF using reportlab.
    Args:
        itinerary: The current Itinerary object.
    Returns:
        PDF file contents as bytes for use with st.download_button.
    '''
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )
    styles = getSampleStyleSheet()
    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=6
    )
    summary_style = ParagraphStyle(
        "Summary",
        parent=styles["Italic"],
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        spaceAfter=16
    )
    h1_style = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontSize=14,
        textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=14,
        spaceAfter=6
    )
    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#333333"),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        spaceAfter=4
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        leftIndent=16,
        spaceAfter=3
    )

    story = []
    story.append(Paragraph("Bon Voyage Itinerary", title_style))

    if itinerary.summary:
        story.append(Paragraph(itinerary.summary, summary_style))

    if itinerary.action_items:
        story.append(Paragraph("Action Items", h1_style))
        for item in itinerary.action_items:
            story.append(Paragraph(f"☐  {item.task}", bullet_style))
        story.append(Spacer(1, 8))

    if itinerary.narrative:
        for line in itinerary.narrative.split("\n"):
            stripped = line.strip()
            if not stripped:
                story.append(Spacer(1, 4))
            elif stripped.startswith("## "):
                story.append(Paragraph(stripped[3:], h2_style))
            elif stripped.startswith("# "):
                story.append(Paragraph(stripped[2:], h1_style))
            elif stripped.startswith("- ") or stripped.startswith("* "):
                text = re.sub(r'\*\*(.*?)\*\*', r'\1', stripped[2:])
                text = re.sub(r'\*(.*?)\*', r'\1', text)
                story.append(Paragraph(f"•  {text}", bullet_style))
            else:
                text = re.sub(r'\*\*(.*?)\*\*', r'\1', stripped)
                text = re.sub(r'\*(.*?)\*', r'\1', text)
                story.append(Paragraph(text, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def render_itinerary_tab():
    """
    Renders the itinerary tab content.
    """
    itinerary: Itinerary = st.session_state.get("itinerary", Itinerary())
    generating: bool = st.session_state.get("itinerary_generating", False)

    has_content = bool(itinerary.summary or itinerary.action_items or itinerary.narrative)

    if generating:
        st.info("Updating your itinerary...")

    if not has_content and not generating:
        st.caption("Your itinerary will appear here as you plan your trip.")
        return

    if has_content:
        # Render markdown in the UI
        st.markdown(itinerary_to_markdown(itinerary))
        st.divider()

        # Generate PDF for download
        pdf_bytes = itinerary_to_pdf(itinerary)
        st.download_button(
            label="Download Itinerary (PDF)",
            data=pdf_bytes,
            file_name="bon_voyage_itinerary.pdf",
            mime="application/pdf"
        )