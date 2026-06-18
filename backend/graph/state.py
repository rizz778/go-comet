from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    """Existing chat state definition for general chat routing."""
    messages: Annotated[list, add_messages]

class PipelineState(TypedDict):
    """Unified state for the multi-agent trade document validation pipeline."""
    filename: str
    file_path: str
    raw_text: str
    extracted_data: dict
    validation_results: dict
    decision: str
    decision_reason: str
    amendment_draft: str | None
    logs: list[str]