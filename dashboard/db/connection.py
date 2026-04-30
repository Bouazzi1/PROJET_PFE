import pg8000.dbapi as pg
import os

HOST = os.getenv("POSTGRES_HOST", "localhost")
PORT = int(os.getenv("POSTGRES_PORT", "5555"))
DB   = os.getenv("POSTGRES_DB", "rihla")
USER = os.getenv("POSTGRES_USER", "rihla_user")
PASS = os.getenv("POSTGRES_PASSWORD", "rihla_pass")


def get_connection():
    return pg.connect(host=HOST, port=PORT, database=DB, user=USER, password=PASS)


def execute_query(query, params=None, fetch=True):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
        if fetch:
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
        conn.commit()
        return None
    finally:
        conn.close()


def execute_returning(query, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
        conn.commit()
        row = cur.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, row))
    finally:
        conn.close()
