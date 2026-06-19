import json
from graph.state import PipelineState
from config.llm import get_llm
from schemas.router_schemas import RouterResponse
from prompts.router_prompts import ROUTER_SYSTEM_PROMPT

def decide_lane(validation_results: dict, cross_doc_results: dict | None = None) -> str:
    """Deterministically selects the next workflow lane."""
    # Detect if validation_results is nested (filenames map to dicts of fields)
    is_nested = False
    if validation_results:
        first_val = list(validation_results.values())[0]
        if isinstance(first_val, dict) and any(isinstance(v, dict) and "result" in v for v in first_val.values()):
            is_nested = True
            
    # Flatten validation results
    all_individual_results = []
    if is_nested:
        for doc_res in validation_results.values():
            all_individual_results.extend(doc_res.values())
    else:
        all_individual_results = list(validation_results.values())
        
    # 1. Any individual field mismatch -> amendment_request
    if any(res.get("result") == "mismatch" for res in all_individual_results):
        return "amendment_request"
        
    # 2. Cross-document consistency failure -> amendment_request
    if cross_doc_results and not cross_doc_results.get("is_consistent", True):
        return "amendment_request"
        
    # 3. Any individual field uncertainty -> flag_review
    if any(res.get("result") == "uncertain" for res in all_individual_results):
        return "flag_review"
        
    # 4. Otherwise -> auto_approve
    return "auto_approve"

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
