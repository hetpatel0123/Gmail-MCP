"""SQLite storage for Gmail OAuth tokens."""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path.home() / ".gmail-mcp-tokens.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            email TEXT PRIMARY KEY,
            access_token TEXT NOT NULL,
            refresh_token TEXT NOT NULL,
            token_expiry TEXT,
            scopes TEXT
        )
    """)
    conn.commit()
    return conn

def save_tokens(email, access_token, refresh_token, expiry=None, scopes=None):
    conn = get_connection()
    expiry_str = expiry.isoformat() if expiry else None
    scopes_str = json.dumps(scopes) if scopes else None
    conn.execute("""
        INSERT OR REPLACE INTO accounts (email, access_token, refresh_token, token_expiry, scopes)
        VALUES (?, ?, ?, ?, ?)
    """, (email, access_token, refresh_token, expiry_str, scopes_str))
    conn.commit()
    conn.close()

def get_tokens(email):
    conn = get_connection()
    cursor = conn.execute(
        "SELECT access_token, refresh_token, token_expiry, scopes FROM accounts WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "access_token": row[0],
        "refresh_token": row[1],
        "expiry": datetime.fromisoformat(row[2]) if row[2] else None,
        "scopes": json.loads(row[3]) if row[3] else None
    }

def list_accounts():
    conn = get_connection()
    cursor = conn.execute("SELECT email FROM accounts")
    accounts = [row[0] for row in cursor.fetchall()]
    conn.close()
    return accounts

def remove_account(email):
    conn = get_connection()
    cursor = conn.execute("DELETE FROM accounts WHERE email = ?", (email,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted