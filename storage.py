import sqlite3
from datetime import datetime

DB_PATH = "safety_watch.db"


def _conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS safety_runs (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                run_date      TEXT,
                category      TEXT,
                signal_level  TEXT,
                summary       TEXT,
                report_path   TEXT
            )
        """)
        c.commit()


def _extract_signal(text: str) -> str:
    for level in ("HIGH", "MEDIUM", "LOW"):
        if level in text:
            return level
    return "UNKNOWN"


def save_run(analyses: list, report_path: str):
    init_db()
    run_date = datetime.now().isoformat()
    with _conn() as c:
        for a in analyses:
            c.execute(
                "INSERT INTO safety_runs "
                "(run_date, category, signal_level, summary, report_path) "
                "VALUES (?,?,?,?,?)",
                (run_date, a["category"],
                 _extract_signal(a["analysis"]),
                 a["analysis"][:600],
                 report_path),
            )
        c.commit()


def get_history(days: int = 30) -> list[tuple]:
    init_db()
    with _conn() as c:
        rows = c.execute(
            "SELECT run_date, category, signal_level "
            "FROM safety_runs "
            "ORDER BY run_date DESC LIMIT 50"
        ).fetchall()
    return rows
