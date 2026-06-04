import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.orchestrator.orchestrator import Task, SubTask, TaskStatus
from app.comms.message_bus import Message

DB_PATH = Path(__file__).resolve().parent.parent / "agentos.db"


class SQLiteDatabase:
    """Singleton SQLite persistence for tasks, subtasks, memory, and messages."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._db_path = str(DB_PATH)
        self._init_tables()
        self._initialized = True

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    goal TEXT NOT NULL,
                    status TEXT NOT NULL,
                    final_result TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    completed_at TEXT DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS subtasks (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    description TEXT NOT NULL,
                    assigned_to TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result TEXT DEFAULT '',
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                );
                CREATE TABLE IF NOT EXISTS memory (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    from_agent TEXT NOT NULL,
                    to_agent TEXT NOT NULL,
                    content TEXT NOT NULL,
                    msg_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );
            """)

    def _status_value(self, status) -> str:
        return status.value if isinstance(status, TaskStatus) else str(status)

    def save_task(self, task: Task) -> None:
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO tasks (id, goal, status, final_result, created_at, completed_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(id) DO UPDATE SET
                     goal=excluded.goal,
                     status=excluded.status,
                     final_result=excluded.final_result,
                     completed_at=excluded.completed_at""",
                (
                    task.id,
                    task.goal,
                    self._status_value(task.status),
                    task.final_result,
                    task.created_at,
                    task.completed_at,
                ),
            )
            conn.execute("DELETE FROM subtasks WHERE task_id = ?", (task.id,))
            for sub in task.subtasks:
                conn.execute(
                    """INSERT INTO subtasks (id, task_id, description, assigned_to, status, result)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        sub.id,
                        task.id,
                        sub.description,
                        sub.assigned_to,
                        self._status_value(sub.status),
                        sub.result,
                    ),
                )

    def get_task(self, task_id: str) -> Optional[Task]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if not row:
                return None
            sub_rows = conn.execute(
                "SELECT * FROM subtasks WHERE task_id = ? ORDER BY rowid",
                (task_id,),
            ).fetchall()
        subtasks = [
            SubTask(
                id=s["id"],
                description=s["description"],
                assigned_to=s["assigned_to"],
                status=TaskStatus(s["status"]),
                result=s["result"] or "",
            )
            for s in sub_rows
        ]
        return Task(
            id=row["id"],
            goal=row["goal"],
            subtasks=subtasks,
            status=TaskStatus(row["status"]),
            final_result=row["final_result"] or "",
            created_at=row["created_at"],
            completed_at=row["completed_at"] or "",
        )

    def get_all_tasks(self) -> List[Task]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id FROM tasks ORDER BY created_at DESC"
            ).fetchall()
        tasks = []
        for row in rows:
            task = self.get_task(row["id"])
            if task:
                tasks.append(task)
        return tasks

    def save_memory(self, key: str, value: str) -> None:
        ts = datetime.now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO memory (key, value, timestamp) VALUES (?, ?, ?)
                   ON CONFLICT(key) DO UPDATE SET
                     value=excluded.value,
                     timestamp=excluded.timestamp""",
                (key, value, ts),
            )

    def get_memory(self, key: str) -> Optional[str]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM memory WHERE key = ?", (key,)
            ).fetchone()
        return row["value"] if row else None

    def get_all_memory(self) -> dict:
        with self._connect() as conn:
            rows = conn.execute("SELECT key, value FROM memory").fetchall()
        return {r["key"]: r["value"] for r in rows}

    def save_message(self, message: Message) -> None:
        msg_type = (
            message.msg_type.value
            if hasattr(message.msg_type, "value")
            else str(message.msg_type)
        )
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO messages
                   (id, from_agent, to_agent, content, msg_type, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    message.id,
                    message.from_agent,
                    message.to_agent,
                    message.content,
                    msg_type,
                    message.timestamp,
                ),
            )
