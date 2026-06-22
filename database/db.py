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
        student_name TEXT DEFAULT '',
        faculty_name TEXT NOT NULL,
        subject TEXT NOT NULL,
        rating INTEGER NOT NULL,
        feedback_text TEXT NOT NULL,
        sentiment TEXT NOT NULL DEFAULT 'Neutral',
        theme_ids TEXT DEFAULT '',
        recommendations TEXT DEFAULT '',
        theme_scores TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("PRAGMA table_info(feedback)")
    columns = [row[1] for row in cursor.fetchall()]

    if "sentiment" not in columns:
        cursor.execute(
            "ALTER TABLE feedback ADD COLUMN sentiment TEXT NOT NULL DEFAULT 'Neutral'"
        )

    # Add student_name column if missing
    if "student_name" not in columns:
        cursor.execute("ALTER TABLE feedback ADD COLUMN student_name TEXT DEFAULT ''")

    # Add new columns if missing (for theme persistence)
    if "theme_ids" not in columns:
        cursor.execute("ALTER TABLE feedback ADD COLUMN theme_ids TEXT DEFAULT ''")
    if "recommendations" not in columns:
        cursor.execute("ALTER TABLE feedback ADD COLUMN recommendations TEXT DEFAULT ''")
    if "theme_scores" not in columns:
        cursor.execute("ALTER TABLE feedback ADD COLUMN theme_scores TEXT DEFAULT ''")

    conn.commit()
    conn.close()

create_table()

print("Table created successfully at:", DB_NAME)

def insert_feedback(faculty_name, subject, rating, feedback_text, student_name: str = ""):
    sentiment = analyze_sentiment(feedback_text)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO feedback
    (student_name, faculty_name, subject, rating, feedback_text, sentiment)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (student_name or "", faculty_name, subject, rating, feedback_text, sentiment))

    conn.commit()
    conn.close()


def fetch_feedback():
    conn = get_connection()
    cursor = conn.cursor()

    # Ensure we return columns in a stable, explicit order so callers
    # (dashboards, pages) can map fields reliably even if the table
    # schema changed over time via ALTER TABLE.
    cursor.execute("PRAGMA table_info(feedback)")
    existing_cols = [row[1] for row in cursor.fetchall()]

    preferred_order = [
        "id",
        "student_name",
        "faculty_name",
        "subject",
        "rating",
        "feedback_text",
        "sentiment",
        "theme_ids",
        "recommendations",
        "theme_scores",
        "created_at",
    ]

    select_cols = [c for c in preferred_order if c in existing_cols]
    if not select_cols:
        # fallback to selecting all if something odd happened
        cursor.execute("SELECT * FROM feedback")
    else:
        q = "SELECT " + ",".join(select_cols) + " FROM feedback"
        cursor.execute(q)

    rows = cursor.fetchall()
    conn.close()
    return rows
