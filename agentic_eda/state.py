from __future__ import annotations

import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel, Field

#Supporting Schemas

class DataFrameInfo(BaseModel):
    shape: Tuple[int, int]
    columns: List[str]
    dtypes: Dict[str, str]
    null_counts: Dict[str, int]
    sample_rows: List[Dict]
    detected_time_column: Optional[str] = None


class ColumnInfo(BaseModel):
    name: str
    dtype: str
    statistics: Dict[str, float] = Field(default_factory=dict)
    detected_issues: List[str] = Field(default_factory=list)


class NotebookCell(BaseModel):
    id: str
    cell_type: str
    content: str

    result_text: Optional[str] = None
    result_tables: Optional[List[Dict]] = None
    result_images: Optional[List[str]] = None

    error: Optional[str] = None
    executed_at: Optional[datetime] = None


#Core Agent State Tracking

class AgentState(BaseModel):
    #Metadata
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    #Conversation
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)

    #Dataset Understanding
    dataset_info: Optional[DataFrameInfo] = None
    columns: List[ColumnInfo] = Field(default_factory=list)

    #Notebook Tracking
    notebook_path: Optional[str] = None
    executed_cells: List[NotebookCell] = Field(default_factory=list)

    #Analysis Progress
    current_phase: str = "INITIALIZATION"
    phase_progress: Dict[str, str] = Field(default_factory=dict)

    #Process Control
    retry_count: int = 0
    max_retries: int = 3
    should_continue: bool = True

    #Error tracking
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

#Utility Methods

    def update_timestamp(self):
        self.last_updated = datetime.utcnow()

    def add_error(self, message: str):
        self.errors.append(message)
        self.retry_count += 1
        self.update_timestamp()

        if self.retry_count >= self.max_retries:
            self.should_continue = False

    def add_warning(self, message: str):
        self.warnings.append(message)
        self.update_timestamp()

    def advance_phase(self, next_phase: str):
        self.phase_progress[self.current_phase] = "done"
        self.current_phase = next_phase
        self.phase_progress[next_phase] = "running"
        self.retry_count = 0
        self.update_timestamp()

    def fail_phase(self):
        self.phase_progress[self.current_phase] = "failed"
        self.should_continue = False
        self.update_timestamp()

#Serialization Utilities

def save_state(state: AgentState, path: str):
    with open(path, "w") as f:
        f.write(state.model_dump_json(indent=2))


def load_state(path: str) -> AgentState:
    with open(path, "r") as f:
        raw = json.load(f)

    raw = migrate_state(raw)
    return AgentState.model_validate(raw)


#Migration Strategy

def migrate_state(data: dict) -> dict:
    version = data.get("version", "0.0.0")

    if version == "0.0.0":
        data["version"] = "1.0.0"
        data.setdefault("retry_count", 0)
        data.setdefault("max_retries", 3)

    return data
