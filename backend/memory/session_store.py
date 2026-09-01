"""
In-Memory Session Store for ORCA
ISRO SIH 2026 - Problem Statement 26176
Provides bounded session storage, TTL expiration, and strict session isolation.
"""

import uuid
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List
from backend.memory.models import ConversationState

logger = logging.getLogger("blue_orbit.memory.session_store")

class SessionStore:
    """
    Manages active conversational sessions with bounded memory and session isolation.
    """
    def __init__(self, max_sessions: int = 500, session_ttl_seconds: int = 3600):
        self._sessions: Dict[str, ConversationState] = {}
        self._last_accessed: Dict[str, float] = {}
        self.max_sessions: int = max_sessions
        self.session_ttl_seconds: int = session_ttl_seconds

    def get_or_create_session(self, session_id: Optional[str] = None) -> ConversationState:
        """
        Retrieves an existing conversation session or initializes a new isolated session.
        """
        self.prune_expired()

        if not session_id or not session_id.strip():
            session_id = f"sess_{uuid.uuid4().hex[:12]}"

        now_ts = time.time()
        if session_id in self._sessions:
            self._last_accessed[session_id] = now_ts
            return self._sessions[session_id]

        # Enforce maximum sessions bound (LRU prune if at capacity)
        if len(self._sessions) >= self.max_sessions:
            oldest_id = min(self._last_accessed, key=self._last_accessed.get)
            self.clear_session(oldest_id)

        new_session = ConversationState(session_id=session_id)
        self._sessions[session_id] = new_session
        self._last_accessed[session_id] = now_ts
        return new_session

    def save_session(self, session: ConversationState) -> None:
        """Stores the updated session state."""
        self._sessions[session.session_id] = session
        self._last_accessed[session.session_id] = time.time()

    def clear_session(self, session_id: str) -> None:
        """Removes a session from memory."""
        self._sessions.pop(session_id, None)
        self._last_accessed.pop(session_id, None)

    def prune_expired(self) -> int:
        """Prunes sessions that have exceeded the TTL limit."""
        now_ts = time.time()
        expired_ids = [
            s_id for s_id, last_ts in self._last_accessed.items()
            if (now_ts - last_ts) > self.session_ttl_seconds
        ]
        for s_id in expired_ids:
            self.clear_session(s_id)
        return len(expired_ids)

    def list_active_session_ids(self) -> List[str]:
        return list(self._sessions.keys())
