
from __future__ import annotations

from typing_extensions import Annotated
from langchain.tools import tool
from langgraph.prebuilt import InjectedStore
from langgraph.store.base import BaseStore

@tool
def save_pref(
    user_id: str,
    key: str,
    value: str,
    store: Annotated[BaseStore, InjectedStore()],
) -> str:
    """Save a user preference (key/value) to persistent store."""
    namespace = ("prefs", user_id)
    store.put(namespace, key, {"value": value})
    return f"saved {key}={value} for user_id={user_id}"

@tool
def load_pref(
    user_id: str,
    key: str,
    store: Annotated[BaseStore, InjectedStore()],
) -> str:
    """Load a user preference (key) from persistent store."""
    namespace = ("prefs", user_id)
    item = store.get(namespace, key)

    if not item:
        return f"(missing) {key}"
    return str(item.value.get("value", f"(missing) {key}"))
