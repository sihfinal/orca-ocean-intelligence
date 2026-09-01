"""
Session State & Structured Conversation Memory Models for ORCA
ISRO SIH 2026 - Problem Statement 26176
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class TurnMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    lang_code: str = "en"

class StructuredContext(BaseModel):
    """
    Structured domain memory retained across turns.
    Separated from raw chat logs for reliable downstream reasoning.
    """
    active_port: Optional[Dict[str, Any]] = None
    candidate_pfz_list: List[Dict[str, Any]] = Field(default_factory=list)
    selected_pfz: Optional[Dict[str, Any]] = None
    active_weather: Optional[Dict[str, Any]] = None
    active_route: Optional[Dict[str, Any]] = None
    active_geofence: Optional[Dict[str, Any]] = None
    last_intent: Optional[str] = None
    last_plan_id: Optional[str] = None
    last_status: str = "INITIAL"
    constraints: Dict[str, Any] = Field(default_factory=dict)
    temporal_context: Optional[Dict[str, Any]] = None
    limitations: List[str] = Field(default_factory=list)
    last_decision: Optional[Dict[str, Any]] = None
    decision_history: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_package: Optional[Dict[str, Any]] = None

class ConversationState(BaseModel):
    """
    Multi-turn conversation session container.
    Maintains bounded raw turns and structured state.
    """
    session_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    turn_count: int = 0
    messages: List[TurnMessage] = Field(default_factory=list)
    structured: StructuredContext = Field(default_factory=StructuredContext)
    language: str = "en"

    def add_user_message(self, text: str, lang_code: str = "en", max_turns: int = 10) -> None:
        self.messages.append(TurnMessage(role="user", content=text, lang_code=lang_code))
        self.language = lang_code
        self.turn_count += 1
        self.updated_at = datetime.now(timezone.utc)
        self._prune_history(max_turns)

    def add_assistant_message(self, text: str, lang_code: str = "en", max_turns: int = 10) -> None:
        self.messages.append(TurnMessage(role="assistant", content=text, lang_code=lang_code))
        self.updated_at = datetime.now(timezone.utc)
        self._prune_history(max_turns)

    def _prune_history(self, max_turns: int) -> None:
        """Keeps conversation history bounded to prevent unbounded growth."""
        if len(self.messages) > max_turns * 2:
            self.messages = self.messages[-(max_turns * 2):]
