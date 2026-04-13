import streamlit as st
import requests

st.title("Paramètres")

BACKEND_URL = "http://localhost:8000"

# --- RAG Sync ---
st.markdown("### Synchronisation RAG")
st.markdown("Synchronisez les données de la base de données vers le moteur de recherche vectorielle (Qdrant).")
st.markdown("**Important** : Exécutez cette action après chaque modification des destinations, programmes ou hôtels.")

if st.button("Synchroniser maintenant"):
    with st.spinner("Synchronisation en cours..."):
        try:
            resp = requests.post(f"{BACKEND_URL}/api/ingest/sync", timeout=120)
            if resp.status_code == 200:
                data = resp.json()
                st.success(f"Synchronisation réussie ! {data.get('total', 0)} chunks créés "
                          f"(FR: {data.get('chunks_fr', 0)}, AR: {data.get('chunks_ar', 0)})")
            else:
                st.error(f"Erreur: {resp.status_code} - {resp.text}")
        except requests.exceptions.ConnectionError:
            st.error("Impossible de se connecter au backend. Vérifiez que le service est en cours d'exécution.")

# --- Service Health ---
st.markdown("### État des services")

services = {
    "Backend FastAPI": f"{BACKEND_URL}/health",
    "Qdrant": "http://localhost:6333/collections",
}

for name, url in services.items():
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            st.success(f"{name} : En ligne")
        else:
            st.warning(f"{name} : Réponse {resp.status_code}")
    except Exception:
        st.error(f"{name} : Hors ligne")

# Check Ollama
try:
    resp = requests.get("http://localhost:11434/api/tags", timeout=5)
    if resp.status_code == 200:
        models = [m["name"] for m in resp.json().get("models", [])]
        st.success(f"Ollama : En ligne - Modèles: {', '.join(models)}")
    else:
        st.warning(f"Ollama : Réponse {resp.status_code}")
except Exception:
    st.error("Ollama : Hors ligne")

# Check Redis
st.markdown("---")
st.markdown("### Configuration")
st.markdown(f"**Backend URL:** `{BACKEND_URL}`")
st.markdown(f"**Ollama URL:** `http://localhost:11434`")
st.markdown(f"**Qdrant URL:** `http://localhost:6333`")
st.markdown(f"**WAHA URL:** `http://localhost:3000`")
st.markdown(f"**n8n URL:** `http://localhost:5678`")
