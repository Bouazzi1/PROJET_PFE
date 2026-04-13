import streamlit as st
import pandas as pd
from db.connection import execute_query

st.title("Conversations")

# Filters
col1, col2 = st.columns(2)
channel_filter = col1.selectbox("Canal", ["Tous", "whatsapp", "email"])
status_filter = col2.selectbox("Statut", ["Tous", "active", "resolved", "escalated"])

query = """
    SELECT cv.id, cv.channel, cv.status, cv.topic, cv.started_at, cv.last_message_at,
           c.full_name, c.phone,
           (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = cv.id) AS msg_count
    FROM conversations cv
    LEFT JOIN clients c ON cv.client_id = c.id
    WHERE 1=1
"""
params = []
if channel_filter != "Tous":
    query += " AND cv.channel = %s"
    params.append(channel_filter)
if status_filter != "Tous":
    query += " AND cv.status = %s"
    params.append(status_filter)
query += " ORDER BY cv.last_message_at DESC"

conversations = execute_query(query, tuple(params) if params else None)

if conversations:
    df = pd.DataFrame(conversations)
    st.dataframe(
        df[["id", "channel", "full_name", "phone", "topic", "status", "msg_count", "last_message_at"]],
        use_container_width=True, hide_index=True,
    )

    # View conversation messages
    st.markdown("### Détail de la conversation")
    conv_opts = {f"{c['id']} - {c['full_name'] or c['phone'] or 'Anonyme'} ({c['channel']})": c for c in conversations}
    selected = st.selectbox("Sélectionner une conversation", list(conv_opts.keys()))
    conv = conv_opts[selected]

    messages = execute_query(
        "SELECT role, content, media_type, timestamp FROM messages WHERE conversation_id = %s ORDER BY timestamp",
        (conv["id"],),
    )

    if messages:
        for msg in messages:
            if msg["role"] == "client":
                st.chat_message("user").write(f"**{msg['timestamp']}**\n\n{msg['content']}")
            else:
                st.chat_message("assistant").write(f"**{msg['timestamp']}**\n\n{msg['content']}")

    # Actions
    col1, col2 = st.columns(2)
    if col1.button("Marquer comme résolu"):
        execute_query("UPDATE conversations SET status='resolved' WHERE id=%s", (conv["id"],), fetch=False)
        st.success("Conversation marquée comme résolue.")
        st.rerun()
    if col2.button("Escalader"):
        execute_query("UPDATE conversations SET status='escalated' WHERE id=%s", (conv["id"],), fetch=False)
        st.warning("Conversation escaladée.")
        st.rerun()
else:
    st.info("Aucune conversation pour le moment.")
