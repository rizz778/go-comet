import json
from graph.state import PipelineState
from config.llm import get_llm
from schemas.router_schemas import RouterResponse
from prompts.router_prompts import ROUTER_SYSTEM_PROMPT
from helpers.router_agent import decide_lane

def router_agent(state: PipelineState) -> PipelineState:
    logs = list(state.get("logs", []))
    logs.append("Router Agent: Running deterministic lane decision...")
    
    validation_results = state["validation_results"]
    cross_doc_results = state.get("cross_doc_results")
    
    # 1. Deterministic Lane Choice
    decision = decide_lane(validation_results, cross_doc_results)
    logs.append(f"Router Agent: Decided lane '{decision}' based on rules.")
    
    logs.append("Router Agent: Invoking LLM to generate reasoning and draft...")
    
    # 2. Invoke LLM for reasoning and draft
    llm = get_llm()
    reasoning = ""
    amendment_draft = ""
    
    prompt = f"""
    The pre-selected workflow decision is: {decision}
    
    Here is the field-by-field Validation Results:
    {json.dumps(validation_results, indent=2)}
    
    Here is the Cross-Document Consistency Results:
    {json.dumps(cross_doc_results, indent=2)}
    
    Write the reasoning and the draft message. If there are cross-document discrepancies, list them clearly in the reasoning and draft message.
    """
    
    try:
        structured_llm = llm.with_structured_output(RouterResponse)
        router_result = structured_llm.invoke([
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ])
        
        reasoning = router_result.reasoning
        amendment_draft = router_result.amendment_draft
        
    except Exception as e:
        logs.append(f"Router Agent: Structured output failed ({str(e)}). Running fallback JSON prompt...")
        
        fallback_prompt = f"""{ROUTER_SYSTEM_PROMPT}
        You must output a raw JSON object matching this schema exactly:
        {{
            "reasoning": "string",
            "amendment_draft": "string"
        }}
        Do not include markdown wrappers (like ```json), just output raw JSON.
        
        Decision: {decision}
        Validation Results:
        {json.dumps(validation_results, indent=2)}
        Cross-Document Consistency Results:
        {json.dumps(cross_doc_results, indent=2)}
        """
        try:
            response = llm.invoke([{"role": "user", "content": fallback_prompt}])
            content = response.content.strip()
            if content.startswith("```"):
                content = content.replace("```json", "", 1).replace("```", "").strip()
            res_dict = json.loads(content)
            reasoning = res_dict.get("reasoning", "Fallback reasoning completed.")
            amendment_draft = res_dict.get("amendment_draft", "")
        except Exception as e_fallback:
            logs.append(f"Router Agent: Fallback failed ({str(e_fallback)}). Setting default notes.")
            reasoning = f"Deterministic decision: {decision}. Fallback text generated."
            amendment_draft = "Please inspect the document manually. Draft generation failed."
            
    logs.append("Router Agent: Reasoning and draft completed.")
    
    return {
        **state,
        "decision": decision,
        "decision_reason": reasoning,
        "amendment_draft": amendment_draft,
        "logs": logs
    }
