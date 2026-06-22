import sqlite3
from pathlib import Path
from ai.sentiment import analyze_sentiment

# Use an absolute path to ensure the database file is always located inside the
# project `database` directory regardless of current working directory.
DB_PATH = Path(__file__).resolve().parent / "feedback.db"
DB_NAME = str(DB_PATH)


def get_connection():
    # Ensure the database directory exists (should already), then connect.
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_NAME)

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_name TEXT NOT NULL,
        subject TEXT NOT NULL,
        rating INTEGER NOT NULL,
        feedback_text TEXT NOT NULL,
        sentiment TEXT NOT NULL DEFAULT 'Neutral',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("PRAGMA table_info(feedback)")
    columns = [row[1] for row in cursor.fetchall()]

    if "sentiment" not in columns:
        cursor.execute(
            "ALTER TABLE feedback ADD COLUMN sentiment TEXT NOT NULL DEFAULT 'Neutral'"
        )

    conn.commit()
    conn.close()

create_table()

print("Table created successfully at:", DB_NAME)

def insert_feedback(faculty_name, subject, rating, feedback_text):
    sentiment = analyze_sentiment(feedback_text)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO feedback
    (faculty_name, subject, rating, feedback_text, sentiment)
    VALUES (?, ?, ?, ?, ?)
    """, (faculty_name, subject, rating, feedback_text, sentiment))

    conn.commit()
    conn.close()


def fetch_feedback():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM feedback")

    rows = cursor.fetchall()

    conn.close()

    return rows


def fetch_feedback():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM feedback")

    rows = cursor.fetchall()

    conn.close()

    return rows
