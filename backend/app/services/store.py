import os
import sqlite3
from datetime import datetime, timezone


def _connect() -> sqlite3.Connection:
    path = os.getenv("ECOVISION_DB_PATH", "./ecovision.db")
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize() -> None:
    with _connect() as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS air_snapshots ("
            "id INTEGER PRIMARY KEY, city TEXT NOT NULL, observed_at TEXT NOT NULL, "
            "source TEXT NOT NULL, payload TEXT NOT NULL)"
        )


def record_snapshot(city: str, payload: str) -> None:
    with _connect() as connection:
        connection.execute(
            "INSERT INTO air_snapshots(city, observed_at, source, payload) VALUES (?, ?, ?, ?)",
            (city, datetime.now(timezone.utc).isoformat(), "Open-Meteo", payload),
        )