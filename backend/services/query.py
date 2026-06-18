import sqlite3
import json
from config.llm import get_llm
from services.storage import get_db_connection

DB_SCHEMA_PROMPT = """
You are a database querying expert. You are helping to query a SQLite database table called `pipeline_runs`.
The table schema is as follows:
CREATE TABLE pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    upload_time TEXT NOT NULL,
    extracted_data TEXT NOT NULL,       -- JSON string containing extracted fields (consignee_name, hs_code, etc.)
    validation_results TEXT NOT NULL,   -- JSON string containing validation results (match, mismatch, etc.)
    decision TEXT NOT NULL,             -- 'auto_approve', 'flag_review', or 'amendment_request'
    decision_reason TEXT NOT NULL,
    amendment_draft TEXT,
    status TEXT NOT NULL,               -- 'pending_review', 'approved', or 'amended'
    edited_data TEXT                    -- JSON string containing operator edits (if any)
)

Example of JSON structure inside `extracted_data` or `edited_data`:
{
  "consignee_name": {"value": "Nova Logistics Ltd", "confidence": 0.95, "source_snippet": "CONSIGNEE: Nova Logistics Ltd"},
  "hs_code": {"value": "8708.29.90", "confidence": 0.9},
  "incoterms": {"value": "FOB", "confidence": 0.99},
  "port_of_loading": {"value": "Port of Shanghai, China", "confidence": 0.95},
  "port_of_discharge": {"value": "Port of Singapore, Singapore", "confidence": 0.95},
  "invoice_number": {"value": "INV-2026-0045", "confidence": 0.99},
  "gross_weight": {"value": 1500.0, "confidence": 0.98},
  "description_of_goods": {"value": "Car bumpers", "confidence": 0.9}
}

Given a natural language query, you must generate a SQL SELECT query to answer it.
Return ONLY valid SQLite SQL code. Do NOT wrap it in backticks, markdown, or any other explanations.

Remember:
- Use standard SQL syntax.
- If referencing fields inside JSON columns, you can use json_extract functions. E.g. `json_extract(extracted_data, '$.consignee_name.value')` or `json_extract(validation_results, '$.consignee_name.status')`.
- Example user query: "How many runs have status approved?"
  SQL: SELECT COUNT(*) FROM pipeline_runs WHERE status = 'approved'
- Example user query: "List all filenames of documents that were auto-approved."
  SQL: SELECT filename FROM pipeline_runs WHERE decision = 'auto_approve'
- Do not write any modifying SQL queries like UPDATE, DELETE, or INSERT.
"""

def execute_nl_query(user_query: str) -> dict:
    llm = get_llm()
    
    # 1. Ask LLM to generate the SQL query
    try:
        sql_generation_prompt = [
            {"role": "system", "content": DB_SCHEMA_PROMPT},
            {"role": "user", "content": f"Generate the SQL query for: {user_query}"}
        ]
        response = llm.invoke(sql_generation_prompt)
        sql_query = response.content.strip()
        
        # Clean potential markdown wrapping if LLM ignored instructions
        if sql_query.startswith("```"):
            lines = sql_query.splitlines()
            if lines[0].startswith("```sql") or lines[0].startswith("```"):
                sql_query = "\n".join(lines[1:-1]).strip()
                
        # Validate that it is a SELECT query
        if not sql_query.lower().startswith("select"):
            raise ValueError(f"Generated query is not a SELECT statement: {sql_query}")
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate SQL: {str(e)}",
            "sql": None,
            "answer": "Sorry, I couldn't translate your question to database instructions."
        }
        
    # 2. Execute SQL query on SQLite
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        results = [dict(r) for r in rows]
        conn.close()
    except Exception as e:
        return {
            "success": False,
            "error": f"SQL Execution Error: {str(e)}",
            "sql": sql_query,
            "answer": f"I generated the SQL query `{sql_query}`, but executing it failed: {str(e)}"
        }
        
    # 3. Ask LLM to synthesize the results into a friendly markdown response
    try:
        synthesize_prompt = [
            {"role": "system", "content": "You are a helpful logistics assistant. Analyze the SQLite database query results and provide a friendly, grounded, and concise answer to the user's question."},
            {"role": "user", "content": f"User question: {user_query}\nExecuted SQL: {sql_query}\nQuery Results: {json.dumps(results)}\n\nPlease synthesize a final user-facing answer."}
        ]
        s_response = llm.invoke(synthesize_prompt)
        answer = s_response.content.strip()
    except Exception as e:
        answer = f"Found {len(results)} matching records: {json.dumps(results)}"
        
    return {
        "success": True,
        "sql": sql_query,
        "results": results,
        "answer": answer
    }
