import streamlit as st
import pandas as pd
from db.connection import execute_query

st.title("Passeports extraits")

passports = execute_query("""
    SELECT p.*, c.full_name, c.phone
    FROM passports p
    LEFT JOIN clients c ON p.client_id = c.id
    ORDER BY p.extracted_at DESC
""")

if passports:
    df = pd.DataFrame(passports)
    st.dataframe(
        df[["id", "full_name", "phone", "surname", "given_names", "passport_number",
            "nationality", "date_of_birth", "sex", "date_of_expiry", "extracted_at"]],
        use_container_width=True, hide_index=True,
    )

    # Detail view
    st.markdown("### Détail du passeport")
    pp_opts = {f"{p['id']} - {p['surname'] or ''} {p['given_names'] or ''}": p for p in passports}
    selected = st.selectbox("Sélectionner un passeport", list(pp_opts.keys()))
    pp = pp_opts[selected]

    col1, col2 = st.columns(2)
    col1.markdown(f"**Nom:** {pp['surname']}")
    col1.markdown(f"**Prénoms:** {pp['given_names']}")
    col1.markdown(f"**N° Passeport:** {pp['passport_number']}")
    col1.markdown(f"**Nationalité:** {pp['nationality']}")
    col2.markdown(f"**Date de naissance:** {pp['date_of_birth']}")
    col2.markdown(f"**Sexe:** {pp['sex']}")
    col2.markdown(f"**Date d'expiration:** {pp['date_of_expiry']}")

    if pp["mrz_line1"] or pp["mrz_line2"]:
        st.markdown("#### MRZ")
        st.code(f"{pp['mrz_line1'] or ''}\n{pp['mrz_line2'] or ''}")

    if pp["raw_ocr_text"]:
        with st.expander("Texte OCR brut"):
            st.text(pp["raw_ocr_text"])

    # Edit passport data (manual correction)
    with st.form("edit_passport"):
        st.markdown("#### Corriger les données")
        col1, col2 = st.columns(2)
        ed_surname = col1.text_input("Nom", pp["surname"] or "")
        ed_names = col2.text_input("Prénoms", pp["given_names"] or "")
        ed_number = col1.text_input("N° Passeport", pp["passport_number"] or "")
        ed_nationality = col2.text_input("Nationalité", pp["nationality"] or "")

        if st.form_submit_button("Corriger"):
            execute_query(
                "UPDATE passports SET surname=%s, given_names=%s, passport_number=%s, nationality=%s WHERE id=%s",
                (ed_surname, ed_names, ed_number, ed_nationality, pp["id"]),
                fetch=False,
            )
            st.success("Passeport corrigé !")
            st.rerun()
else:
    st.info("Aucun passeport extrait. Les passeports sont extraits automatiquement lorsqu'un client envoie une image.")
