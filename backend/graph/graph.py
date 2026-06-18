from langgraph.graph import StateGraph, START, END
from graph.state import  PipelineState

from agents.extractor import extract_agent
from agents.validator import validator_agent
from agents.router import router_agent
from services.storage import save_pipeline_run



# 2. Document Pipeline Graph (New)
def db_saver_node(state: PipelineState) -> PipelineState:
    """Graph node to persist final pipeline outcomes to the SQLite database."""
    logs = list(state.get("logs", []))
    logs.append("Storage Node: Saving pipeline results to SQLite database...")
    
    # Save to SQLite
    run_id = save_pipeline_run(
        filename=state["filename"],
        extracted_data=state["extracted_data"],
        validation_results=state["validation_results"],
        decision=state["decision"],
        decision_reason=state["decision_reason"],
        amendment_draft=state["amendment_draft"],
        status="approved" if state["decision"] == "auto_approve" else "pending_review"
    )
    
    logs.append(f"Storage Node: Run saved successfully. DB ID: {run_id}")
    return {
        **state,
        "logs": logs
    }

pipeline_builder = StateGraph(PipelineState)
pipeline_builder.add_node("extract", extract_agent)
pipeline_builder.add_node("validate", validator_agent)
pipeline_builder.add_node("route", router_agent)
pipeline_builder.add_node("save", db_saver_node)

pipeline_builder.add_edge(START, "extract")
pipeline_builder.add_edge("extract", "validate")
pipeline_builder.add_edge("validate", "route")
pipeline_builder.add_edge("route", "save")
pipeline_builder.add_edge("save", END)

pipeline_graph = pipeline_builder.compile()
