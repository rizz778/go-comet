from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class PipelineRunRepository(ABC):
    @abstractmethod
    def init_db(self) -> None:
        """Initializes the database schema."""
        pass

    @abstractmethod
    def save_run(
        self,
        filename: str,
        extracted_data: dict,
        validation_results: dict,
        decision: str,
        decision_reason: str,
        amendment_draft: Optional[str],
        status: str = "pending_review",
        cross_doc_results: Optional[dict] = None,
        source: str = "manual_upload",
        email_sender: Optional[str] = None,
        email_metadata_json: Optional[str] = None
    ) -> int:
        """Saves a run log to the repository and returns the row ID."""
        pass

    @abstractmethod
    def get_run(self, run_id: int) -> Optional[dict]:
        """Retrieves a single run by its ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[dict]:
        """Retrieves all pipeline run logs."""
        pass

    @abstractmethod
    def get_incoming(self) -> List[dict]:
        """Retrieves all unprocessed inbox runs."""
        pass

    @abstractmethod
    def get_processed(self) -> List[dict]:
        """Retrieves all processed/resolved inbox runs."""
        pass

    @abstractmethod
    def update_status(
        self,
        run_id: int,
        status: str,
        edited_data: Optional[dict] = None,
        amendment_draft: Optional[str] = None
    ) -> bool:
        """Updates the status or fields of a pipeline run."""
        pass

    @abstractmethod
    def get_analytics(self) -> dict:
        """Returns counts for analytics metrics."""
        pass
