import streamlit as st

st.set_page_config(
    page_title="Rihla-AI Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Rihla-AI Dashboard")
st.markdown("### Tableau de bord de l'agence de voyage intelligente")

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

# Quick stats
from db.connection import execute_query

try:
    destinations = execute_query("SELECT COUNT(*) as count FROM destinations")[0]["count"]
    programs = execute_query("SELECT COUNT(*) as count FROM programs WHERE is_active = TRUE")[0]["count"]
    clients = execute_query("SELECT COUNT(*) as count FROM clients")[0]["count"]
    bookings = execute_query("SELECT COUNT(*) as count FROM bookings")[0]["count"]

    col1.metric("Destinations", destinations)
    col2.metric("Programmes actifs", programs)
    col3.metric("Clients", clients)
    col4.metric("Réservations", bookings)
except Exception as e:
    st.error(f"Erreur de connexion à la base de données: {e}")
    st.info("Vérifiez que PostgreSQL est en cours d'exécution et que les paramètres de connexion sont corrects.")

st.markdown("---")
st.markdown(
    """
    **Navigation** : Utilisez le menu latéral pour accéder aux différentes sections.

    - **Destinations** : Gérer les destinations de voyage
    - **Programmes** : Gérer les programmes/packages de voyage
    - **Hôtels** : Gérer les hôtels partenaires
    - **Vols** : Gérer les vols disponibles
    - **Clients** : Consulter et gérer les clients
    - **Réservations** : Gérer les réservations
    - **Conversations** : Voir les conversations de l'agent AI
    - **Passeports** : Voir les passeports extraits par OCR
    - **Analytiques** : Rapports et statistiques
    - **Paramètres** : Configuration du système
    """
)
