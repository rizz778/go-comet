import os
import sqlite3
import json
from datetime import datetime
from config.settings import settings

def get_db_connection():
    """Establishes a connection to the SQLite database.
    Creates any missing parent directories dynamically.
    """
    db_dir = os.path.dirname(settings.db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
        
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite schema for tracking audit runs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create runs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            upload_time TEXT NOT NULL,
            extracted_data TEXT NOT NULL,
            validation_results TEXT NOT NULL,
            decision TEXT NOT NULL,
            decision_reason TEXT NOT NULL,
            amendment_draft TEXT,
            status TEXT NOT NULL,
            edited_data TEXT
        )
    """)
    
    # Dynamically alter table to add columns if they don't exist
    try:
        cursor.execute("ALTER TABLE pipeline_runs ADD COLUMN cross_doc_results TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE pipeline_runs ADD COLUMN source TEXT DEFAULT 'manual_upload'")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE pipeline_runs ADD COLUMN email_sender TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE pipeline_runs ADD COLUMN email_metadata_json TEXT")
    except sqlite3.OperationalError:
        pass
        
    conn.commit()
    conn.close()
 
def save_pipeline_run(
    filename: str,
    extracted_data: dict,
    validation_results: dict,
    decision: str,
    decision_reason: str,
    amendment_draft: str | None,
    status: str = "pending_review",
    cross_doc_results: dict | None = None,
    source: str = "manual_upload",
    email_sender: str | None = None,
    email_metadata_json: str | None = None
) -> int:
    """Saves a run log to the SQLite table and returns the row ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    upload_time = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO pipeline_runs (
            filename, upload_time, extracted_data, validation_results, 
            decision, decision_reason, amendment_draft, status, 
            cross_doc_results, source, email_sender, email_metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        filename,
        upload_time,
        json.dumps(extracted_data),
        json.dumps(validation_results),
        decision,
        decision_reason,
        amendment_draft,
        status,
        json.dumps(cross_doc_results or {"is_consistent": True, "discrepancies": []}),
        source,
        email_sender,
        email_metadata_json
    ))
    
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return run_id
 
def get_pipeline_run(run_id: int) -> dict | None:
    """Retrieves a single run log by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pipeline_runs WHERE id = ?", (run_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    # Helper to safely extract column with fallback
    def get_col(r, key, default=None):
        try:
            return r[key]
        except (IndexError, KeyError):
            return default
            
    cross_doc_raw = get_col(row, "cross_doc_results")
    source_val = get_col(row, "source", "manual_upload")
    email_sender_val = get_col(row, "email_sender")
    email_meta_raw = get_col(row, "email_metadata_json")
    
    meta = json.loads(email_meta_raw) if email_meta_raw else {}
    
    return {
        "id": row["id"],
        "filename": row["filename"],
        "upload_time": row["upload_time"],
        "extracted_data": json.loads(row["extracted_data"]),
        "validation_results": json.loads(row["validation_results"]),
        "decision": row["decision"],
        "decision_reason": row["decision_reason"],
        "amendment_draft": row["amendment_draft"],
        "status": row["status"],
        "edited_data": json.loads(row["edited_data"]) if row["edited_data"] else None,
        "cross_doc_results": json.loads(cross_doc_raw) if cross_doc_raw else {"is_consistent": True, "discrepancies": []},
        "source": source_val,
        "email_sender": email_sender_val,
        "email_subject": meta.get("subject"),
        "email_body": meta.get("email_body"),
        "received_at": meta.get("received_at")
    }
 
def get_all_runs() -> list[dict]:
    """Retrieves all pipeline run logs in descending order."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pipeline_runs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    # Helper to safely extract column with fallback
    def get_col(r, key, default=None):
        try:
            return r[key]
        except (IndexError, KeyError):
            return default
            
    runs = []
    for row in rows:
        cross_doc_raw = get_col(row, "cross_doc_results")
        source_val = get_col(row, "source", "manual_upload")
        email_sender_val = get_col(row, "email_sender")
        email_meta_raw = get_col(row, "email_metadata_json")
        
        meta = json.loads(email_meta_raw) if email_meta_raw else {}
        
        runs.append({
            "id": row["id"],
            "filename": row["filename"],
            "upload_time": row["upload_time"],
            "extracted_data": json.loads(row["extracted_data"]),
            "validation_results": json.loads(row["validation_results"]),
            "decision": row["decision"],
            "decision_reason": row["decision_reason"],
            "amendment_draft": row["amendment_draft"],
            "status": row["status"],
            "edited_data": json.loads(row["edited_data"]) if row["edited_data"] else None,
            "cross_doc_results": json.loads(cross_doc_raw) if cross_doc_raw else {"is_consistent": True, "discrepancies": []},
            "source": source_val,
            "email_sender": email_sender_val,
            "email_subject": meta.get("subject"),
            "email_body": meta.get("email_body"),
            "received_at": meta.get("received_at")
        })
    return runs

def update_run_status(run_id: int, status: str, edited_data: dict | None = None, amendment_draft: str | None = None) -> bool:
    """Updates the status or fields of a historical pipeline run."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if edited_data is not None and amendment_draft is not None:
        cursor.execute("""
            UPDATE pipeline_runs 
            SET status = ?, edited_data = ?, amendment_draft = ?
            WHERE id = ?
        """, (status, json.dumps(edited_data), amendment_draft, run_id))
    elif edited_data is not None:
        cursor.execute("""
            UPDATE pipeline_runs 
            SET status = ?, edited_data = ?
            WHERE id = ?
        """, (status, json.dumps(edited_data), run_id))
    elif amendment_draft is not None:
        cursor.execute("""
            UPDATE pipeline_runs 
            SET status = ?, amendment_draft = ?
            WHERE id = ?
        """, (status, amendment_draft, run_id))
    else:
        cursor.execute("""
            UPDATE pipeline_runs 
            SET status = ?
            WHERE id = ?
        """, (status, run_id))
        
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def get_analytics() -> dict:
    """Returns total counts for analytics metrics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM pipeline_runs")
    total_runs = cursor.fetchone()[0]
    
    cursor.execute("SELECT decision, COUNT(*) FROM pipeline_runs GROUP BY decision")
    decision_counts = {row[0]: row[1] for row in cursor.fetchall()}
    
    cursor.execute("SELECT status, COUNT(*) FROM pipeline_runs GROUP BY status")
    status_counts = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    return {
        "total_runs": total_runs,
        "decisions": {
            "auto_approve": decision_counts.get("auto_approve", 0),
            "flag_review": decision_counts.get("flag_review", 0),
            "amendment_request": decision_counts.get("amendment_request", 0)
        },
        "statuses": {
            "pending_review": status_counts.get("pending_review", 0),
            "approved": status_counts.get("approved", 0),
            "amended": status_counts.get("amended", 0)
        }
    }
