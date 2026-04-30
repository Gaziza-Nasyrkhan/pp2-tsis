import psycopg2

def get_connection():
    conn = psycopg2.connect(
    dbname="snake",
    user="postgres",
    password="pp2psql",
    host="127.0.0.1",
    port="5432"
)
    return conn

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
            score INTEGER DEFAULT 0,
            level_reached INTEGER DEFAULT 1,
            played_at TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

def get_or_create_player(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM players WHERE username=%s", (username,))
    row = cur.fetchone()

    if row:
        player_id = row[0]
    else:
        cur.execute(
            "INSERT INTO players(username) VALUES(%s) RETURNING id",
            (username,)
        )
        player_id = cur.fetchone()[0]
        conn.commit()

    cur.close()
    conn.close()
    return player_id

def save_result(player_id, score, level):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO game_sessions(player_id, score, level_reached) VALUES(%s,%s,%s)",
        (player_id, score, level)
    )

    conn.commit()
    cur.close()
    conn.close()

def get_leaderboard(limit=10):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT p.username, MAX(g.score), MAX(g.level_reached)
        FROM game_sessions g
        JOIN players p ON g.player_id = p.id
        GROUP BY p.username
        ORDER BY MAX(g.score) DESC
        LIMIT %s
    """, (limit,))

    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows

def get_personal_best(player_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT COALESCE(MAX(score),0) FROM game_sessions WHERE player_id=%s",
        (player_id,)
    )

    best = cur.fetchone()[0]

    cur.close()
    conn.close()
    return best