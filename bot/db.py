import sqlite3
import threading
import time
from contextlib import contextmanager

from . import config

_lock = threading.Lock()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT DEFAULT '',
                username TEXT DEFAULT '',
                lang TEXT DEFAULT 'ru',
                balance_stars INTEGER DEFAULT 0,
                cases_opened INTEGER DEFAULT 0,
                tasks_done INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT 0,
                last_task_at INTEGER DEFAULT 0,
                last_case_at INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS cases_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_sponsor TEXT DEFAULT '',
                stars_won INTEGER NOT NULL,
                created_at INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS tasks_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                sponsor_id TEXT NOT NULL,
                sponsor_title TEXT DEFAULT '',
                created_at INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY
            );
            """
        )


@contextmanager
def get_conn():
    with _lock:
        conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ---------- users ----------

def ensure_user(user_id: int, first_name: str = "", username: str = "") -> dict:
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, first_name, username, created_at) VALUES (?, ?, ?, ?)",
            (user_id, first_name, username, int(time.time())),
        )
        conn.execute(
            "UPDATE users SET first_name=?, username=? WHERE user_id=?",
            (first_name, username, user_id),
        )
        row = conn.execute(
            "SELECT * FROM users WHERE user_id=?", (user_id,)
        ).fetchone()
        return dict(row)


def get_user(user_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        return dict(row) if row else None


def set_lang(user_id: int, lang: str) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))


def add_stars(user_id: int, amount: int) -> int:
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET balance_stars=balance_stars+? WHERE user_id=?",
            (amount, user_id),
        )
        return conn.execute(
            "SELECT balance_stars FROM users WHERE user_id=?", (user_id,)
        ).fetchone()["balance_stars"]


def touch_last_task(user_id: int) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE users SET last_task_at=? WHERE user_id=?", (int(time.time()), user_id))


def touch_last_case(user_id: int) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE users SET last_case_at=? WHERE user_id=?", (int(time.time()), user_id))


# ---------- ops ----------

def log_case(user_id: int, sponsor: str, stars: int) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO cases_log (user_id, task_sponsor, stars_won, created_at) VALUES (?, ?, ?, ?)",
            (user_id, sponsor, stars, int(time.time())),
        )
        conn.execute("UPDATE users SET cases_opened=cases_opened+1 WHERE user_id=?", (user_id,))


def log_task(user_id: int, sponsor_id: str, sponsor_title: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO tasks_log (user_id, sponsor_id, sponsor_title, created_at) VALUES (?, ?, ?, ?)",
            (user_id, sponsor_id, sponsor_title, int(time.time())),
        )
        conn.execute("UPDATE users SET tasks_done=tasks_done+1 WHERE user_id=?", (user_id,))


# ---------- stats ----------

def stats_total() -> dict:
    with get_conn() as conn:
        users = conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
        cases = conn.execute("SELECT COUNT(*) c FROM cases_log").fetchone()["c"]
        stars = conn.execute("SELECT COALESCE(SUM(stars_won),0) s FROM cases_log").fetchone()["s"]
        tasks = conn.execute("SELECT COUNT(*) c FROM tasks_log").fetchone()["c"]
        return {"users": users, "cases": cases, "stars": stars, "tasks": tasks}


def recent_cases(limit: int = 10) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM cases_log ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]