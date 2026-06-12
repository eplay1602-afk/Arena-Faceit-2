import sqlite3

DB_NAME = "database.db"


# ---------------- CONNECT ---------------- #

def get_db():
    return sqlite3.connect(DB_NAME)


# ---------------- INIT ---------------- #

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


# ---------------- PLAYER ---------------- #

def create_player(discord_id: str, game_id: str, nickname: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO players
    (discord_id, game_id, nickname)
    VALUES (?, ?, ?)
    """, (discord_id, game_id, nickname))

    conn.commit()
    conn.close()


def get_player(discord_id: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM players WHERE discord_id = ?
    """, (discord_id,))

    data = cursor.fetchone()
    conn.close()

    return data


def add_elo(discord_id: str, amount: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players
    SET elo = elo + ?
    WHERE discord_id = ?
    """, (amount, discord_id))

    conn.commit()
    conn.close()


def remove_elo(discord_id: str, amount: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players
    SET elo = elo - ?
    WHERE discord_id = ?
    """, (amount, discord_id))

    conn.commit()
    conn.close()