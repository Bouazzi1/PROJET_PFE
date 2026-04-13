import streamlit as st
import pandas as pd
from db.connection import execute_query

st.title("Réservations")

STATUSES = ["pending", "confirmed", "paid", "cancelled"]

# Filters
col1, col2 = st.columns(2)
status_filter = col1.selectbox("Filtrer par statut", ["Tous"] + STATUSES)
date_filter = col2.date_input("Depuis", value=None)

# Build query
query = """
    SELECT b.id, c.full_name, c.phone, p.title_fr AS programme,
           b.status, b.num_travelers, b.total_price, b.currency, b.booking_date, b.notes
    FROM bookings b
    LEFT JOIN clients c ON b.client_id = c.id
    LEFT JOIN programs p ON b.program_id = p.id
    WHERE 1=1
"""
params = []
if status_filter != "Tous":
    query += " AND b.status = %s"
    params.append(status_filter)
if date_filter:
    query += " AND b.booking_date >= %s"
    params.append(date_filter)
query += " ORDER BY b.booking_date DESC"

bookings = execute_query(query, tuple(params) if params else None)

# Stats
if bookings:
    total = len(bookings)
    pending = sum(1 for b in bookings if b["status"] == "pending")
    confirmed = sum(1 for b in bookings if b["status"] == "confirmed")
    paid = sum(1 for b in bookings if b["status"] == "paid")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", total)
    col2.metric("En attente", pending)
    col3.metric("Confirmées", confirmed)
    col4.metric("Payées", paid)

    df = pd.DataFrame(bookings)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Update status
    st.markdown("### Modifier le statut")
    booking_opts = {f"{b['id']} - {b['full_name'] or 'N/A'} - {b['programme'] or 'N/A'}": b for b in bookings}
    selected = st.selectbox("Sélectionner une réservation", list(booking_opts.keys()))
    booking = booking_opts[selected]

    with st.form("edit_booking"):
        new_status = st.selectbox("Nouveau statut", STATUSES,
            index=STATUSES.index(booking["status"]) if booking["status"] in STATUSES else 0)
        notes = st.text_area("Notes", booking["notes"] or "")

        if st.form_submit_button("Mettre à jour"):
            execute_query(
                "UPDATE bookings SET status=%s, notes=%s, updated_at=NOW() WHERE id=%s",
                (new_status, notes, booking["id"]),
                fetch=False,
            )
            st.success("Réservation mise à jour !")
            st.rerun()
else:
    st.info("Aucune réservation.")
