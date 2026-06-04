import uuid
import sqlite3
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class MessageType(str, Enum):
    TASK = "TASK"
    QUESTION = "QUESTION"
    ANSWER = "ANSWER"
    DELEGATE = "DELEGATE"
    UPDATE = "UPDATE"
    BROADCAST = "BROADCAST"

@dataclass
class Message:
    from_agent: str
    to_agent: str
    content: str
    msg_type: MessageType = MessageType.TASK
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    read: bool = False

class MessageBus:
    """Central communication hub. Agents talk to each other through here."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._messages: List[Message] = []
        self._db_path = "/tmp/agentos_messages.db"
        self._setup_db()
        self._initialized = True
        print("[MessageBus] Initialized")

    def _setup_db(self):
        conn = sqlite3.connect(self._db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                from_agent TEXT,
                to_agent TEXT,
                content TEXT,
                msg_type TEXT,
                timestamp TEXT,
                read INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def send(self, from_agent: str, to_agent: str, content: str,
             msg_type: MessageType = MessageType.TASK) -> Message:
        """Send a message from one agent to another."""
        msg = Message(
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            msg_type=msg_type
        )
        self._messages.append(msg)
        # Persist to SQLite
        conn = sqlite3.connect(self._db_path)
        conn.execute(
            "INSERT INTO messages VALUES (?,?,?,?,?,?,?)",
            (msg.id, msg.from_agent, msg.to_agent, msg.content,
             msg.msg_type, msg.timestamp, 0)
        )
        conn.commit()
        conn.close()
        print(f"[MessageBus] {from_agent} → {to_agent}: {content[:60]}...")
        return msg

    def receive(self, agent_name: str) -> List[Message]:
        """Get all unread messages for an agent."""
        unread = [m for m in self._messages
                  if m.to_agent == agent_name and not m.read]
        for m in unread:
            m.read = True
        return unread

    def broadcast(self, from_agent: str, content: str) -> List[Message]:
        """Send a message to ALL agents."""
        from app.agents.registry import AgentRegistry
        registry = AgentRegistry()
        msgs = []
        for agent_name in registry.list_all():
            if agent_name != from_agent:
                msgs.append(self.send(from_agent, agent_name, content,
                                      MessageType.BROADCAST))
        return msgs

    def get_history(self, agent_name: str = None) -> List[Message]:
        """Get full message history, optionally filtered by agent."""
        if agent_name:
            return [m for m in self._messages
                    if m.from_agent == agent_name or m.to_agent == agent_name]
        return self._messages

    def get_all_messages(self) -> List[dict]:
        return [
            {
                "id": m.id,
                "from": m.from_agent,
                "to": m.to_agent,
                "content": m.content,
                "type": m.msg_type,
                "timestamp": m.timestamp
            }
            for m in self._messages
        ]
