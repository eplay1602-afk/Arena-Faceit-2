import sqlite3

DB_NAME = "database.db"

def get_db():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        discord_id TEXT PRIMARY KEY,
        game_id TEXT,
        nickname TEXT,
        elo INTEGER DEFAULT 1000,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()