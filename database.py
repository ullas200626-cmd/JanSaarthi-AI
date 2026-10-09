
import sqlite3
from contextlib import contextmanager
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "jansaarthi.db"


@contextmanager
def get_connection():
    """Open a database connection and always close it when finished."""
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                complaint_id TEXT PRIMARY KEY,
                issue TEXT NOT NULL,
                message TEXT NOT NULL,
                language TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Submitted',
                created_at TEXT NOT NULL DEFAULT
                    (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
            )
        """)


def create_complaint(complaint_id, issue, message, language):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO complaints
                (complaint_id, issue, message, language)
            VALUES (?, ?, ?, ?)
            """,
            (complaint_id, issue, message, language),
        )


def get_complaint(complaint_id):
    with get_connection() as connection:
        return connection.execute(
            "SELECT * FROM complaints WHERE complaint_id = ?",
            (complaint_id,),
        ).fetchone()


initialize_database()