import streamlit as st
import pandas as pd
from db.connection import execute_query

st.title("Clients")

clients = execute_query("""
    SELECT c.*,
           (SELECT COUNT(*) FROM bookings b WHERE b.client_id = c.id) AS booking_count,
           (SELECT COUNT(*) FROM passports p WHERE p.client_id = c.id) AS passport_count
    FROM clients c ORDER BY c.created_at DESC
""")

if clients:
    df = pd.DataFrame(clients)
    st.dataframe(
        df[["id", "full_name", "phone", "email", "preferred_language", "profile_type", "budget_preference", "booking_count", "passport_count"]],
        use_container_width=True, hide_index=True,
    )

    # Detail view
    st.markdown("### Détail client")
    client_opts = {f"{c['id']} - {c['full_name'] or c['phone'] or c['email']}": c for c in clients}
    selected = st.selectbox("Sélectionner un client", list(client_opts.keys()))
    client = client_opts[selected]

    col1, col2 = st.columns(2)
    col1.markdown(f"**Nom:** {client['full_name'] or 'N/A'}")
    col1.markdown(f"**Téléphone:** {client['phone'] or 'N/A'}")
    col1.markdown(f"**Email:** {client['email'] or 'N/A'}")
    col2.markdown(f"**Langue:** {client['preferred_language']}")
    col2.markdown(f"**Profil:** {client['profile_type'] or 'N/A'}")
    col2.markdown(f"**Budget:** {client['budget_preference'] or 'N/A'}")

    # Client bookings
    bookings = execute_query("""
        SELECT b.id, p.title_fr, b.status, b.total_price, b.booking_date
        FROM bookings b JOIN programs p ON b.program_id = p.id
        WHERE b.client_id = %s ORDER BY b.booking_date DESC
    """, (client["id"],))

    if bookings:
        st.markdown("#### Réservations")
        st.dataframe(pd.DataFrame(bookings), use_container_width=True, hide_index=True)

    # Edit profile
    with st.form("edit_client"):
        PROFILES = ["unknown", "student", "business", "family", "young", "senior", "couple"]
        BUDGETS = ["unknown", "budget", "standard", "luxury"]

        col3, col4 = st.columns(2)
        ed_profile = col3.selectbox("Profil", PROFILES,
            index=PROFILES.index(client["profile_type"]) if client["profile_type"] in PROFILES else 0)
        ed_budget = col4.selectbox("Budget", BUDGETS,
            index=BUDGETS.index(client["budget_preference"]) if client["budget_preference"] in BUDGETS else 0)
        ed_notes = st.text_area("Notes", client["notes"] or "")

        if st.form_submit_button("Mettre à jour"):
            execute_query(
                "UPDATE clients SET profile_type=%s, budget_preference=%s, notes=%s, updated_at=NOW() WHERE id=%s",
                (ed_profile, ed_budget, ed_notes, client["id"]),
                fetch=False,
            )
            st.success("Client mis à jour !")
            st.rerun()
else:
    st.info("Aucun client pour le moment. Les clients sont créés automatiquement lorsqu'ils contactent l'agent.")
