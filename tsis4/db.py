import psycopg2

DB_CONFIG = {
    "dbname": "snake",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_sessions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players(id),
            score INTEGER NOT NULL DEFAULT 0,
            level_reached INTEGER NOT NULL DEFAULT 1,
            played_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def get_or_create_player(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    row = cur.fetchone()
    if row:
        player_id = row[0]
    else:
        cur.execute("INSERT INTO players (username) VALUES (%s) RETURNING id", (username,))
        player_id = cur.fetchone()[0]
        conn.commit()
    cur.close()
    conn.close()
    return player_id

def save_result(player_id, score, level):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
        (player_id, score, level)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_leaderboard(limit=10):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.username, MAX(gs.score) as best_score, MAX(gs.level_reached) as best_level
        FROM game_sessions gs
        JOIN players p ON gs.player_id = p.id
        GROUP BY p.username
        ORDER BY best_score DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_personal_best(player_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT MAX(score) FROM game_sessions WHERE player_id = %s
    """, (player_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row and row[0] else 0