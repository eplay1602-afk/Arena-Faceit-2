import sqlite3

conn = sqlite3.connect("arenafc.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    discord_id TEXT PRIMARY KEY,
    game_id TEXT NOT NULL,
    nickname TEXT NOT NULL,
    elo INTEGER DEFAULT 1000,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()
