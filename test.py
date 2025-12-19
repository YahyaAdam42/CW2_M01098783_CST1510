
import pandas as pd
import sqlite3
from pathlib import Path

# Path to your SQLite database file
DB_PATH = Path("DATA") / "intelligence_platform.db"


def create_users_table(conn):
    """Create the users table if it does not already exist."""
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
        """
    )
    conn.commit()


def migrate_users(conn, users_txt_path: str = "user.txt"):
    """
    Read existing users from user.txt (username,hashed_password)
    and insert them into the users table.
    """
    cur = conn.cursor()

    try:
        with open(users_txt_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    username, password_hash = line.split(",", 1)
                except ValueError:
                    # Skip malformed lines
                    continue

                # INSERT OR IGNORE to avoid duplicate usernames
                cur.execute(
                    """
                    INSERT OR IGNORE INTO users (username, password_hash, role)
                    VALUES (?, ?, ?)
                    """,
                    (username, password_hash, "user"),
                )

        conn.commit()
    except FileNotFoundError:
        # No user.txt yet – nothing to migrate
        pass


def migrating_cyber_incidents(conn):
    """Load cyber_incidents.csv into the cyber_incidents table."""
    data = pd.read_csv("DATA/cyber_incidents.csv")
    data.to_sql("cyber_incidents", conn, if_exists="replace", index=False)


def migrating_it_tickets(conn):
    """Load it_tickets.csv into the it_tickets table."""
    data = pd.read_csv("DATA/it_tickets.csv")
    data.to_sql("it_tickets", conn, if_exists="replace", index=False)


if __name__ == "__main__":
    # 1. Connect to the database (created if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)

    # 2. Ensure users table exists
    create_users_table(conn)

    # 3. Migrate users from user.txt → users table
    migrate_users(conn)

    # 4. Migrate CSV data for cyber incidents and IT tickets
    migrating_cyber_incidents(conn)
    migrating_it_tickets(conn)

    # 5. Close connection
    conn.close()
