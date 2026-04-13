import streamlit as st
import pandas as pd
from db.connection import execute_query, execute_returning

st.title("Vols")

destinations = execute_query("SELECT id, name_fr FROM destinations ORDER BY name_fr")
dest_options = {d["name_fr"]: d["id"] for d in destinations} if destinations else {}
CLASSES = ["economy", "business", "first"]

# --- Add flight ---
with st.expander("Ajouter un vol", expanded=False):
    with st.form("add_flight"):
        col1, col2 = st.columns(2)
        origin = col1.text_input("Origine", "Tunis")
        dest_sel = col2.selectbox("Destination", list(dest_options.keys()) if dest_options else ["Aucune"])
        col3, col4 = st.columns(2)
        airline = col3.text_input("Compagnie aérienne")
        flight_number = col4.text_input("Numéro de vol")
        col5, col6 = st.columns(2)
        dep_date = col5.date_input("Date de départ")
        ret_date = col6.date_input("Date de retour")
        col7, col8, col9 = st.columns(3)
        price = col7.number_input("Prix (TND)", 0, 10000000, 50000)
        flight_class = col8.selectbox("Classe", CLASSES)
        seats = col9.number_input("Places disponibles", 0, 500, 100)

        if st.form_submit_button("Ajouter"):
            if origin and dest_sel in dest_options and airline:
                execute_returning(
                    """INSERT INTO flights (origin, destination_id, airline, flight_number, departure_date, return_date, price, class, seats_available)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (origin, dest_options[dest_sel], airline, flight_number, dep_date, ret_date, price, flight_class, seats),
                )
                st.success("Vol ajouté !")
                st.rerun()
            else:
                st.error("Origine, Destination et Compagnie sont requis.")

# --- List flights ---
flights = execute_query("""
    SELECT f.*, d.name_fr AS dest_name
    FROM flights f JOIN destinations d ON f.destination_id = d.id
    ORDER BY f.departure_date
""")

if flights:
    df = pd.DataFrame(flights)
    st.dataframe(
        df[["id", "origin", "dest_name", "airline", "flight_number", "departure_date", "return_date", "price", "class", "seats_available"]],
        use_container_width=True, hide_index=True,
        column_config={"price": st.column_config.NumberColumn("Prix (TND)", format="%d")},
    )

    st.markdown("### Modifier / Supprimer")
    flight_opts = {f"{f['id']} - {f['airline']} {f['flight_number']}": f for f in flights}
    selected = st.selectbox("Sélectionner un vol", list(flight_opts.keys()))
    flight = flight_opts[selected]

    with st.form("edit_flight"):
        col1, col2 = st.columns(2)
        ed_origin = col1.text_input("Origine", flight["origin"])
        ed_airline = col2.text_input("Compagnie", flight["airline"])
        ed_fn = st.text_input("Numéro de vol", flight["flight_number"])
        col3, col4, col5 = st.columns(3)
        ed_price = col3.number_input("Prix", 0, 10000000, int(flight["price"] or 0))
        ed_class = col4.selectbox("Classe", CLASSES, index=CLASSES.index(flight["class"]) if flight["class"] in CLASSES else 0)
        ed_seats = col5.number_input("Places", 0, 500, flight["seats_available"] or 0)

        col_s, col_d = st.columns(2)
        save = col_s.form_submit_button("Sauvegarder")
        delete = col_d.form_submit_button("Supprimer", type="primary")

        if save:
            execute_query(
                """UPDATE flights SET origin=%s, airline=%s, flight_number=%s,
                price=%s, class=%s, seats_available=%s, updated_at=NOW() WHERE id=%s""",
                (ed_origin, ed_airline, ed_fn, ed_price, ed_class, ed_seats, flight["id"]),
                fetch=False,
            )
            st.success("Vol mis à jour !")
            st.rerun()
        if delete:
            execute_query("DELETE FROM flights WHERE id = %s", (flight["id"],), fetch=False)
            st.success("Vol supprimé !")
            st.rerun()
else:
    st.info("Aucun vol.")
