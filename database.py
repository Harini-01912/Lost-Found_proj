import os
import sqlite3

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    database_path = app.config["DATABASE"]
    if database_path != ":memory:":
        os.makedirs(os.path.dirname(database_path), exist_ok=True)

    with sqlite3.connect(database_path) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL CHECK (kind IN ('lost', 'found')),
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                event_date TEXT NOT NULL,
                contact TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f', 'now'))
            )
            """
        )
        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_items_kind_created ON items(kind, created_at)"
        )
