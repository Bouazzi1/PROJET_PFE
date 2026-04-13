import streamlit as st
import pandas as pd
from db.connection import execute_query, execute_returning

st.title("Destinations")

# --- Add new destination ---
with st.expander("Ajouter une destination", expanded=False):
    with st.form("add_destination"):
        col1, col2 = st.columns(2)
        name_fr = col1.text_input("Nom (FR)")
        name_ar = col2.text_input("Nom (AR)")
        country = col1.text_input("Pays")
        city = col2.text_input("Ville")
        desc_fr = st.text_area("Description (FR)")
        desc_ar = st.text_area("Description (AR)")
        col3, col4 = st.columns(2)
        climate = col3.text_input("Climat")
        best_season = col4.text_input("Meilleure saison")
        visa_required = st.checkbox("Visa requis")

        if st.form_submit_button("Ajouter"):
            if name_fr and country:
                execute_returning(
                    """INSERT INTO destinations (name_fr, name_ar, country, city, description_fr, description_ar, climate, best_season, visa_required)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                    (name_fr, name_ar, country, city, desc_fr, desc_ar, climate, best_season, visa_required),
                )
                st.success("Destination ajoutée !")
                st.rerun()
            else:
                st.error("Nom (FR) et Pays sont requis.")

# --- List destinations ---
destinations = execute_query("SELECT * FROM destinations ORDER BY id")
if destinations:
    df = pd.DataFrame(destinations)
    st.dataframe(
        df[["id", "name_fr", "name_ar", "country", "city", "climate", "best_season", "visa_required"]],
        use_container_width=True,
        hide_index=True,
    )

    # --- Edit / Delete ---
    st.markdown("### Modifier / Supprimer")
    dest_options = {f"{d['id']} - {d['name_fr']}": d for d in destinations}
    selected = st.selectbox("Sélectionner une destination", list(dest_options.keys()))
    dest = dest_options[selected]

    with st.form("edit_destination"):
        col1, col2 = st.columns(2)
        ed_name_fr = col1.text_input("Nom (FR)", dest["name_fr"])
        ed_name_ar = col2.text_input("Nom (AR)", dest["name_ar"] or "")
        ed_country = col1.text_input("Pays", dest["country"])
        ed_city = col2.text_input("Ville", dest["city"] or "")
        ed_desc_fr = st.text_area("Description (FR)", dest["description_fr"] or "")
        ed_desc_ar = st.text_area("Description (AR)", dest["description_ar"] or "")
        col3, col4 = st.columns(2)
        ed_climate = col3.text_input("Climat", dest["climate"] or "")
        ed_best_season = col4.text_input("Meilleure saison", dest["best_season"] or "")
        ed_visa = st.checkbox("Visa requis", dest["visa_required"])

        col_save, col_del = st.columns(2)
        save = col_save.form_submit_button("Sauvegarder")
        delete = col_del.form_submit_button("Supprimer", type="primary")

        if save:
            execute_query(
                """UPDATE destinations SET name_fr=%s, name_ar=%s, country=%s, city=%s,
                description_fr=%s, description_ar=%s, climate=%s, best_season=%s,
                visa_required=%s, updated_at=NOW() WHERE id=%s""",
                (ed_name_fr, ed_name_ar, ed_country, ed_city, ed_desc_fr, ed_desc_ar,
                 ed_climate, ed_best_season, ed_visa, dest["id"]),
                fetch=False,
            )
            st.success("Destination mise à jour !")
            st.rerun()

        if delete:
            execute_query("DELETE FROM destinations WHERE id = %s", (dest["id"],), fetch=False)
            st.success("Destination supprimée !")
            st.rerun()
else:
    st.info("Aucune destination. Ajoutez-en une ci-dessus.")
