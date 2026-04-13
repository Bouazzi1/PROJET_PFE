import streamlit as st
import pandas as pd
from db.connection import execute_query, execute_returning

st.title("Programmes de voyage")

# Get dependencies
destinations = execute_query("SELECT id, name_fr FROM destinations ORDER BY name_fr")
hotels = execute_query("SELECT id, name FROM hotels ORDER BY name")
flights = execute_query("SELECT id, origin, airline, flight_number FROM flights ORDER BY id")

dest_options = {d["name_fr"]: d["id"] for d in destinations} if destinations else {}
hotel_options = {"Aucun": None} | ({h["name"]: h["id"] for h in hotels} if hotels else {})
flight_options = {"Aucun": None} | ({f"{f['airline']} {f['flight_number']} ({f['origin']})": f["id"] for f in flights} if flights else {})

CATEGORIES = ["budget", "standard", "luxury", "adventure", "religious"]
AUDIENCES = ["student", "family", "couple", "business", "young", "senior", "all"]

# --- Add program ---
with st.expander("Ajouter un programme", expanded=False):
    with st.form("add_program"):
        col1, col2 = st.columns(2)
        title_fr = col1.text_input("Titre (FR)")
        title_ar = col2.text_input("Titre (AR)")

        dest_sel = st.selectbox("Destination", list(dest_options.keys()) if dest_options else ["Aucune destination"])
        desc_fr = st.text_area("Description (FR)")
        desc_ar = st.text_area("Description (AR)")

        col3, col4, col5 = st.columns(3)
        duration = col3.number_input("Durée (jours)", 1, 60, 7)
        price = col4.number_input("Prix (TND)", 0, 10000000, 50000)
        max_part = col5.number_input("Max participants", 1, 500, 30)

        col6, col7 = st.columns(2)
        category = col6.selectbox("Catégorie", CATEGORIES)
        audience = col7.selectbox("Public cible", AUDIENCES)

        hotel_sel = st.selectbox("Hôtel", list(hotel_options.keys()))
        flight_sel = st.selectbox("Vol", list(flight_options.keys()))

        col8, col9 = st.columns(2)
        start_date = col8.date_input("Date début")
        end_date = col9.date_input("Date fin")

        includes_text = st.text_input("Inclus (séparés par virgule)", "vol aller-retour, hébergement, petit-déjeuner")
        is_active = st.checkbox("Actif", True)

        if st.form_submit_button("Ajouter"):
            if title_fr and dest_sel in dest_options:
                includes_list = [i.strip() for i in includes_text.split(",") if i.strip()]
                execute_returning(
                    """INSERT INTO programs (title_fr, title_ar, destination_id, description_fr, description_ar,
                    duration_days, price, category, target_audience, includes, hotel_id, flight_id,
                    max_participants, start_date, end_date, is_active)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (title_fr, title_ar, dest_options[dest_sel], desc_fr, desc_ar,
                     duration, price, category, audience, includes_list,
                     hotel_options[hotel_sel], flight_options[flight_sel],
                     max_part, start_date, end_date, is_active),
                )
                st.success("Programme ajouté !")
                st.rerun()
            else:
                st.error("Titre (FR) et Destination sont requis.")

# --- List programs ---
programs = execute_query("""
    SELECT p.*, d.name_fr AS dest_name, h.name AS hotel_name
    FROM programs p
    JOIN destinations d ON p.destination_id = d.id
    LEFT JOIN hotels h ON p.hotel_id = h.id
    ORDER BY p.id
""")

if programs:
    df = pd.DataFrame(programs)
    st.dataframe(
        df[["id", "title_fr", "dest_name", "duration_days", "price", "category", "target_audience", "hotel_name", "is_active"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "price": st.column_config.NumberColumn("Prix (TND)", format="%d"),
        },
    )

    # --- Edit / Delete ---
    st.markdown("### Modifier / Supprimer")
    prog_options = {f"{p['id']} - {p['title_fr']}": p for p in programs}
    selected = st.selectbox("Sélectionner un programme", list(prog_options.keys()))
    prog = prog_options[selected]

    with st.form("edit_program"):
        col1, col2 = st.columns(2)
        ed_title_fr = col1.text_input("Titre (FR)", prog["title_fr"])
        ed_title_ar = col2.text_input("Titre (AR)", prog["title_ar"] or "")
        ed_desc_fr = st.text_area("Description (FR)", prog["description_fr"] or "")
        ed_desc_ar = st.text_area("Description (AR)", prog["description_ar"] or "")

        col3, col4, col5 = st.columns(3)
        ed_duration = col3.number_input("Durée (jours)", 1, 60, prog["duration_days"] or 7)
        ed_price = col4.number_input("Prix (TND)", 0, 10000000, int(prog["price"] or 0))
        ed_max = col5.number_input("Max participants", 1, 500, prog["max_participants"] or 30)

        col6, col7 = st.columns(2)
        ed_cat = col6.selectbox("Catégorie", CATEGORIES, index=CATEGORIES.index(prog["category"]) if prog["category"] in CATEGORIES else 0)
        ed_aud = col7.selectbox("Public cible", AUDIENCES, index=AUDIENCES.index(prog["target_audience"]) if prog["target_audience"] in AUDIENCES else 0)

        ed_active = st.checkbox("Actif", prog["is_active"])

        col_save, col_del = st.columns(2)
        save = col_save.form_submit_button("Sauvegarder")
        delete = col_del.form_submit_button("Supprimer", type="primary")

        if save:
            execute_query(
                """UPDATE programs SET title_fr=%s, title_ar=%s, description_fr=%s, description_ar=%s,
                duration_days=%s, price=%s, category=%s, target_audience=%s,
                max_participants=%s, is_active=%s, updated_at=NOW() WHERE id=%s""",
                (ed_title_fr, ed_title_ar, ed_desc_fr, ed_desc_ar, ed_duration, ed_price,
                 ed_cat, ed_aud, ed_max, ed_active, prog["id"]),
                fetch=False,
            )
            st.success("Programme mis à jour !")
            st.rerun()

        if delete:
            execute_query("DELETE FROM programs WHERE id = %s", (prog["id"],), fetch=False)
            st.success("Programme supprimé !")
            st.rerun()
else:
    st.info("Aucun programme. Ajoutez-en un ci-dessus.")
