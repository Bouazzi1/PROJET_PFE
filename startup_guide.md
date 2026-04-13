# Rihla-AI - Guide de Démarrage

## Prérequis
- Docker Desktop installé et lancé
- Ollama installé et lancé (`ollama serve`)
- Modèles Ollama téléchargés :
  ```
  ollama pull qwen2.5:7b
  ollama pull nomic-embed-text
  ```

---

## Étape 1 — Lancer les services Docker

```bash
cd "c:/Users/RAZER/OneDrive/Bureau/Rihla_AI"
docker compose up -d
```

Cela lance 6 services :
| Service    | Port (host) | Description               |
|------------|-------------|---------------------------|
| postgres   | 5432        | Base de données            |
| qdrant     | 6333        | Vector store (RAG)         |
| redis      | 6379        | Mémoire conversation       |
| waha       | 3000        | API WhatsApp               |
| n8n        | 5679        | Orchestration workflows    |
| backend    | 8000        | FastAPI (intelligence)     |

Vérifier que tout tourne :
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

---

## Étape 2 — Vérifier Ollama

```bash
curl http://localhost:11434/api/tags
```

Doit afficher `qwen2.5:7b` et `nomic-embed-text` dans la liste.

---

## Étape 3 — Vérifier le Backend

```bash
curl http://localhost:8000/api/health
```

Réponse attendue : `{"status":"ok"}`

---

## Étape 4 — Ingérer les données dans Qdrant (RAG)

Première fois uniquement (ou après reset de Qdrant) :
```bash
curl -X POST http://localhost:8000/api/ingest/sync
```

Cela synchronise les données PostgreSQL (programmes, destinations, hôtels, activités) vers les collections Qdrant en français et arabe.

---

## Étape 5 — Configurer WAHA (WhatsApp)

1. Ouvrir http://localhost:3000 (Dashboard WAHA)
2. Se connecter (voir fichier credentials.md)
3. Si la session "default" n'est pas WORKING :
   - Démarrer une nouvelle session
   - Scanner le QR code avec WhatsApp sur votre téléphone
4. Vérifier la session :
   ```bash
   curl -s http://localhost:3000/api/sessions -H "X-Api-Key: rihla2026"
   ```
   Réponse attendue : `"status":"WORKING"`

---

## Étape 6 — Vérifier n8n (Workflows)

1. Ouvrir http://localhost:5679
2. Se connecter (voir fichier credentials.md)
3. Vérifier que les 2 workflows sont **actifs** (toggle vert) :
   - **WhatsApp Handler** — 5 noeuds
   - **Email Handler** — 3 noeuds

Si les workflows ne sont pas présents après un reset :
```bash
# Importer via API (nécessite une session n8n active)
# Se connecter d'abord via le navigateur, puis utiliser l'API
```

---

## Étape 7 — Lancer le Dashboard Streamlit

```bash
cd "c:/Users/RAZER/OneDrive/Bureau/Rihla_AI/dashboard"
python -m streamlit run app.py --server.port 8502
```

Ouvrir http://localhost:8502

---

## Étape 8 — Tester le système

### Test WhatsApp
Envoyer un message au numéro lié à WAHA depuis WhatsApp :
- "Bonjour" → réponse générale
- "Quels programmes proposez-vous ?" → réponse RAG
- "Recommandez-moi un voyage" → recommandation personnalisée
- Envoyer une photo de passeport → extraction OCR

### Test Email
Envoyer un email à contact.alrihla@gmail.com depuis une autre adresse.
La réponse automatique arrive en ~1-2 minutes.

---

## Commandes utiles

```bash
# Voir les logs d'un service
docker logs rihla-backend --tail 30
docker logs rihla-n8n --tail 30
docker logs rihla-waha --tail 30

# Redémarrer un service
docker compose restart backend
docker compose restart n8n

# Arrêter tout
docker compose down

# Arrêter et supprimer les données (ATTENTION)
docker compose down -v

# Reconstruire le backend après modification du code
docker compose up -d --build backend
```

---

## Résolution de problèmes

| Problème | Solution |
|----------|----------|
| Backend ne démarre pas | Vérifier qu'Ollama tourne : `ollama serve` |
| WAHA déconnecté | Re-scanner le QR code dans http://localhost:3000 |
| n8n webhook 404 | Vérifier que le workflow WhatsApp Handler est actif |
| Email ne répond pas | Vérifier que le workflow Email Handler est actif dans n8n |
| RAG ne trouve rien | Relancer l'ingestion : `curl -X POST http://localhost:8000/api/ingest/sync` |
| Dashboard erreur encodage | Bug connu — à corriger (caractères français dans PostgreSQL) |
