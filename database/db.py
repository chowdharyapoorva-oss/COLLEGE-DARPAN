import sqlite3
import os
from config import Config

def get_db_connection():
    """Returns a SQLite connection with row_factory configured as dict-like sqlite3.Row."""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def query_db(query, args=(), one=False):
    """Executes a parameterized read query and returns a list of dictionaries or a single dict."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, args)
        rv = cur.fetchall()
        cur.close()
        results = [dict(row) for row in rv]
        return (results[0] if results else None) if one else results
    finally:
        conn.close()

def execute_db(query, args=(), commit=True):
    """Executes an insert/update/delete parameterized query and returns the lastrowid."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, args)
        if commit:
            conn.commit()
        last_id = cur.lastrowid
        cur.close()
        return last_id
    finally:
        conn.close()

def execute_script(script_path):
    """Executes an entire SQL script file against the database."""
    conn = get_db_connection()
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()
