import os
import json
from fastapi import HTTPException

async def get_rules() -> dict:
    rules_path = os.path.join(os.path.dirname(__file__), "..", "config", "rules.json")
    try:
        with open(rules_path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read rules configuration: {str(e)}")
