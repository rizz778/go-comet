import os
import re
import json
from graph.state import PipelineState
from helpers.common_helpers import load_rules
from helpers.validator_agent import validate_field, validate_cross_document_consistency


#Rule basded validator no LLM (may cause hallucination)


def validator_agent(state: PipelineState) -> PipelineState:
    logs = list(state.get("logs", []))
    logs.append("Validator Agent: Starting deterministic validation...")
    
    extracted_data = state.get("extracted_data", {})
    rules = load_rules()
    validation_results = {}
    
    filenames = state.get("filenames", [])
    if not filenames:
        if "filename" in state:
            filenames = [state["filename"]]
        else:
            filenames = ["document.pdf"]
            
    is_multidoc = False
    if extracted_data:
        first_key = list(extracted_data.keys())[0]
        if first_key in filenames or first_key.endswith((".pdf", ".png", ".jpg", ".jpeg")):
            is_multidoc = True
            
    fields = [
        "consignee_name", "hs_code", "port_of_loading", "port_of_discharge",
        "incoterms", "description_of_goods", "gross_weight", "invoice_number"
    ]
    
    if is_multidoc:
        for doc_name, doc_data in extracted_data.items():
            doc_results = {}
            for field in fields:
                field_data = doc_data.get(field) or {"value": None, "confidence": 0.0}
                value = field_data.get("value")
                confidence = field_data.get("confidence", 1.0)
                rule = rules.get(field)
                
                result, expected, found, reason = validate_field(field, rule, value)
                
                if confidence < 0.70:
                    result = "uncertain"
                    reason = f"Extraction confidence too low to trust ({confidence:.2f}). " + (reason or "")
                    
                doc_results[field] = {
                    "result": result,
                    "expected_value": expected,
                    "found_value": found,
                    "reason": reason
                }
            validation_results[doc_name] = doc_results
            logs.append(f"Validator Agent: Completed individual validation for {doc_name}.")
            
        # Run cross-document check
        cross_doc_results = validate_cross_document_consistency(extracted_data, logs)
    else:
        for field in fields:
            field_data = extracted_data.get(field) or {"value": None, "confidence": 0.0}
            value = field_data.get("value")
            confidence = field_data.get("confidence", 1.0)
            rule = rules.get(field)
            
            result, expected, found, reason = validate_field(field, rule, value)
            
            if confidence < 0.70:
                result = "uncertain"
                reason = f"Extraction confidence too low to trust ({confidence:.2f}). " + (reason or "")
                
            validation_results[field] = {
                "result": result,
                "expected_value": expected,
                "found_value": found,
                "reason": reason
            }
        logs.append("Validator Agent: Completed validation for single document.")
        cross_doc_results = {
            "is_consistent": True,
            "discrepancies": []
        }
        
    logs.append("Validator Agent: Validation completed.")
    return {
        **state,
        "validation_results": validation_results,
        "cross_doc_results": cross_doc_results,
        "logs": logs
    }
