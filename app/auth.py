import hashlib
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "agentos.db"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def generate_api_key() -> str:
    return "agos_sk_" + secrets.token_hex(16)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_users_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            plan TEXT DEFAULT 'free',
            api_key TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_user(email: str, password: str) -> dict:
    create_users_table()
    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM users WHERE email = ?", (email,)
    ).fetchone()
    if existing:
        conn.close()
        return {"error": "Email already exists"}
    user_id = secrets.token_hex(8)
    api_key = generate_api_key()
    hashed = hash_password(password)
    created_at = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO users VALUES (?,?,?,?,?,?)",
        (user_id, email, hashed, "free", api_key, created_at)
    )
    conn.commit()
    conn.close()
    return {
        "user_id": user_id,
        "email": email,
        "api_key": api_key,
        "plan": "free",
        "created_at": created_at
    }

def get_user_by_email(email: str) -> dict:
    create_users_table()
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_user_by_api_key(api_key: str) -> dict:
    create_users_table()
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE api_key = ?", (api_key,)
    ).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def login_user(email: str, password: str) -> dict:
    user = get_user_by_email(email)
    if not user:
        return {"error": "Email not found"}
    if not verify_password(password, user["password"]):
        return {"error": "Wrong password"}
    return {
        "email": user["email"],
        "api_key": user["api_key"],
        "plan": user["plan"]
    }

def check_usage_limit(api_key: str) -> dict:
    """Check if user has exceeded their daily limit."""
    user = get_user_by_api_key(api_key)
    if not user:
        return {"allowed": False, "reason": "Invalid API key"}
    if user["plan"] in ["pro", "team"]:
        return {"allowed": True, "plan": user["plan"], "limit": "unlimited"}
    conn = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    count = conn.execute("""
        SELECT COUNT(*) as cnt FROM tasks
        WHERE created_at LIKE ? || '%'
    """, (today,)).fetchone()
    conn.close()
    daily_count = count["cnt"] if count else 0
    if daily_count >= 5:
        return {
            "allowed": False,
            "reason": "Daily limit reached. Upgrade to Pro for unlimited tasks.",
            "used": daily_count,
            "limit": 5,
            "plan": "free"
        }
    return {
        "allowed": True,
        "used": daily_count,
        "limit": 5,
        "remaining": 5 - daily_count,
        "plan": "free"
    }