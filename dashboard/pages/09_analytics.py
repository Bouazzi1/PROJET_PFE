import streamlit as st
import pandas as pd
import plotly.express as px
from db.connection import execute_query

st.title("Analytiques")

# --- Revenue by destination ---
st.markdown("### Revenus par destination")
revenue_data = execute_query("""
    SELECT d.name_fr AS destination, COALESCE(SUM(b.total_price), 0) AS revenue, COUNT(b.id) AS bookings
    FROM destinations d
    LEFT JOIN programs p ON d.id = p.destination_id
    LEFT JOIN bookings b ON p.id = b.program_id AND b.status != 'cancelled'
    GROUP BY d.name_fr ORDER BY revenue DESC
""")
if revenue_data:
    df = pd.DataFrame(revenue_data)
    fig = px.bar(df, x="destination", y="revenue", color="destination",
                 title="Revenus par destination (TND)", text="bookings")
    st.plotly_chart(fig, use_container_width=True)

# --- Bookings by status ---
st.markdown("### Réservations par statut")
status_data = execute_query("""
    SELECT status, COUNT(*) AS count FROM bookings GROUP BY status
""")
if status_data:
    df = pd.DataFrame(status_data)
    fig = px.pie(df, values="count", names="status", title="Répartition des réservations")
    st.plotly_chart(fig, use_container_width=True)

# --- Popular programs ---
st.markdown("### Programmes les plus réservés")
prog_data = execute_query("""
    SELECT p.title_fr, COUNT(b.id) AS bookings
    FROM programs p LEFT JOIN bookings b ON p.id = b.program_id
    GROUP BY p.title_fr ORDER BY bookings DESC LIMIT 10
""")
if prog_data:
    df = pd.DataFrame(prog_data)
    fig = px.bar(df, x="title_fr", y="bookings", title="Top programmes")
    st.plotly_chart(fig, use_container_width=True)

# --- Client profiles ---
st.markdown("### Profils clients")
profile_data = execute_query("""
    SELECT COALESCE(profile_type, 'unknown') AS profile, COUNT(*) AS count
    FROM clients GROUP BY profile_type
""")
if profile_data:
    df = pd.DataFrame(profile_data)
    fig = px.pie(df, values="count", names="profile", title="Types de profils clients")
    st.plotly_chart(fig, use_container_width=True)

# --- Conversations by channel ---
st.markdown("### Conversations par canal")
conv_data = execute_query("""
    SELECT channel, COUNT(*) AS count FROM conversations GROUP BY channel
""")
if conv_data:
    df = pd.DataFrame(conv_data)
    fig = px.pie(df, values="count", names="channel", title="Répartition WhatsApp vs Email")
    st.plotly_chart(fig, use_container_width=True)

# --- Daily conversation volume ---
st.markdown("### Volume de conversations (30 derniers jours)")
daily_data = execute_query("""
    SELECT DATE(started_at) AS date, COUNT(*) AS count
    FROM conversations
    WHERE started_at >= NOW() - INTERVAL '30 days'
    GROUP BY DATE(started_at) ORDER BY date
""")
if daily_data:
    df = pd.DataFrame(daily_data)
    fig = px.line(df, x="date", y="count", title="Conversations par jour")
    st.plotly_chart(fig, use_container_width=True)
