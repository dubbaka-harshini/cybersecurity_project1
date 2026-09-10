"""
init_db.py
----------
Run this once to create the SQLite database and tables:

    python database/init_db.py

Safe to re-run: uses CREATE TABLE IF NOT EXISTS, so it will never
wipe existing data.
"""

import os
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def init_db():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(schema)
        conn.commit()
        print(f"[OK] Database initialised at: {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
