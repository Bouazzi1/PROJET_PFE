import streamlit as st
import pandas as pd
from db.connection import execute_query, execute_returning

st.title("Hôtels")

destinations = execute_query("SELECT id, name_fr FROM destinations ORDER BY name_fr")
dest_options = {d["name_fr"]: d["id"] for d in destinations} if destinations else {}

CATEGORIES = ["budget", "standard", "luxury"]
AMENITIES = ["wifi", "piscine", "spa", "restaurant", "bar", "salle-de-sport", "parking",
             "petit-dejeuner", "room-service", "climatisation", "vue-mer", "terrasse",
             "conciergerie", "navette-haram", "navette-aeroport"]

# --- Add hotel ---
with st.expander("Ajouter un hôtel", expanded=False):
    with st.form("add_hotel"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Nom")
        dest_sel = col2.selectbox("Destination", list(dest_options.keys()) if dest_options else ["Aucune"])

        col3, col4, col5 = st.columns(3)
        stars = col3.number_input("Étoiles", 1, 5, 3)
        price = col4.number_input("Prix/nuit (TND)", 0, 1000000, 5000)
        category = col5.selectbox("Catégorie", CATEGORIES)

        amenities = st.multiselect("Équipements", AMENITIES)
        desc_fr = st.text_area("Description (FR)")
        desc_ar = st.text_area("Description (AR)")
        address = st.text_input("Adresse")

        if st.form_submit_button("Ajouter"):
            if name and dest_sel in dest_options:
                execute_returning(
                    """INSERT INTO hotels (destination_id, name, stars, price_per_night, category, amenities, description_fr, description_ar, address)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (dest_options[dest_sel], name, stars, price, category, amenities, desc_fr, desc_ar, address),
                )
                st.success("Hôtel ajouté !")
                st.rerun()
            else:
                st.error("Nom et Destination sont requis.")

# --- List hotels ---
hotels = execute_query("""
    SELECT h.*, d.name_fr AS dest_name
    FROM hotels h JOIN destinations d ON h.destination_id = d.id
    ORDER BY h.id
""")

if hotels:
    df = pd.DataFrame(hotels)
    st.dataframe(
        df[["id", "name", "dest_name", "stars", "price_per_night", "category", "amenities"]],
        use_container_width=True, hide_index=True,
        column_config={"price_per_night": st.column_config.NumberColumn("Prix/nuit (TND)", format="%d")},
    )

    st.markdown("### Modifier / Supprimer")
    hotel_opts = {f"{h['id']} - {h['name']}": h for h in hotels}
    selected = st.selectbox("Sélectionner un hôtel", list(hotel_opts.keys()))
    hotel = hotel_opts[selected]

    with st.form("edit_hotel"):
        col1, col2 = st.columns(2)
        ed_name = col1.text_input("Nom", hotel["name"])
        ed_stars = col2.number_input("Étoiles", 1, 5, hotel["stars"])
        col3, col4 = st.columns(2)
        ed_price = col3.number_input("Prix/nuit", 0, 1000000, int(hotel["price_per_night"] or 0))
        ed_cat = col4.selectbox("Catégorie", CATEGORIES, index=CATEGORIES.index(hotel["category"]) if hotel["category"] in CATEGORIES else 0)
        ed_amenities = st.multiselect("Équipements", AMENITIES, default=hotel["amenities"] or [])
        ed_desc_fr = st.text_area("Description (FR)", hotel["description_fr"] or "")
        ed_desc_ar = st.text_area("Description (AR)", hotel["description_ar"] or "")
        ed_addr = st.text_input("Adresse", hotel["address"] or "")

        col_s, col_d = st.columns(2)
        save = col_s.form_submit_button("Sauvegarder")
        delete = col_d.form_submit_button("Supprimer", type="primary")

        if save:
            execute_query(
                """UPDATE hotels SET name=%s, stars=%s, price_per_night=%s, category=%s,
                amenities=%s, description_fr=%s, description_ar=%s, address=%s, updated_at=NOW() WHERE id=%s""",
                (ed_name, ed_stars, ed_price, ed_cat, ed_amenities, ed_desc_fr, ed_desc_ar, ed_addr, hotel["id"]),
                fetch=False,
            )
            st.success("Hôtel mis à jour !")
            st.rerun()
        if delete:
            execute_query("DELETE FROM hotels WHERE id = %s", (hotel["id"],), fetch=False)
            st.success("Hôtel supprimé !")
            st.rerun()
else:
    st.info("Aucun hôtel.")
