# middleware/log_middleware.py
from __future__ import annotations

from typing import Any
from typing_extensions import NotRequired, TypedDict

from langchain.agents import AgentState
from langchain.agents.middleware import before_agent

class AuditState(AgentState):
    audit: NotRequired[list[dict[str, Any]]]  # allow missing initially

@before_agent(state_schema=AuditState)
def log_before_agent(state: AuditState, runtime) -> dict[str, Any]:
    existing = state.get("audit", [])
    entry = {"event": "agent_start", "n_messages": len(state.get("messages", []))}
    return {"audit": existing + [entry]}
