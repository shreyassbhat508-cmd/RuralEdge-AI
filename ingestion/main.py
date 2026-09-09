"""Phase 2 Entry Point: Source Management and Pipeline Run Verification.

This script initializes government sources via the modular source abstraction layer,
retrieves active source records from Supabase PostgreSQL, and manages ingestion run lifecycles.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# Ensure the ingestion directory is on sys.path for direct execution
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from config import Config, setup_logging
from database import get_supabase_client, test_connection
from sources import (
    MySchemeSource,
    SourceError,
    SourceNotFoundError,
    InactiveSourceError,
    InvalidSourceConfigError,
)

logger = setup_logging("main")


def create_ingestion_run(
    client: Any,
    source_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Creates a new record in 'ingestion_runs' with status 'running'.

    Args:
        client: The Supabase client instance.
        source_id: UUID of the associated government source (if available).
        metadata: Optional metadata dictionary to attach to the run.

    Returns:
        Dict[str, Any]: The newly created ingestion run record.
    """
    started_at = datetime.now(timezone.utc).isoformat()
    run_payload: Dict[str, Any] = {
        "started_at": started_at,
        "status": "running",
        "documents_found": 0,
        "documents_processed": 0,
        "documents_failed": 0,
        "metadata": metadata or {"phase": "phase_2_source_management"},
    }
    if source_id:
        run_payload["source_id"] = source_id

    logger.info("Creating initial 'ingestion_runs' record with status='running'...")
    response = client.table("ingestion_runs").insert(run_payload).execute()

    if not response.data:
        raise RuntimeError("Failed to insert into 'ingestion_runs'; no data returned.")

    run_record = response.data[0]
    logger.info("Ingestion run created successfully (Run ID: %s)", run_record.get("id"))
    return run_record


def update_ingestion_run_completed(
    client: Any,
    run_id: str,
    documents_found: int = 0,
    documents_processed: int = 0,
    documents_failed: int = 0,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Marks an ingestion run as completed.

    Args:
        client: The Supabase client instance.
        run_id: UUID of the ingestion run record.
        documents_found: Total documents discovered.
        documents_processed: Total documents successfully processed.
        documents_failed: Total documents that failed processing.
        additional_metadata: Optional extra metadata to merge.

    Returns:
        Dict[str, Any]: The updated ingestion run record.
    """
    completed_at = datetime.now(timezone.utc).isoformat()
    update_payload: Dict[str, Any] = {
        "completed_at": completed_at,
        "status": "completed",
        "documents_found": documents_found,
        "documents_processed": documents_processed,
        "documents_failed": documents_failed,
    }
    if additional_metadata:
        update_payload["metadata"] = additional_metadata

    logger.info("Updating ingestion run %s to status='completed'...", run_id)
    response = client.table("ingestion_runs").update(update_payload).eq("id", run_id).execute()

    if not response.data:
        raise RuntimeError(f"Failed to update 'ingestion_runs' record {run_id}.")

    updated_record = response.data[0]
    logger.info("Ingestion run %s marked as 'completed'.", run_id)
    return updated_record


def update_ingestion_run_failed(
    client: Any, run_id: str, error_message: str
) -> Optional[Dict[str, Any]]:
    """Marks an ingestion run as failed with error details.

    Args:
        client: The Supabase client instance.
        run_id: UUID of the ingestion run record.
        error_message: Error description.

    Returns:
        Optional[Dict[str, Any]]: The updated record if successful.
    """
    completed_at = datetime.now(timezone.utc).isoformat()
    update_payload: Dict[str, Any] = {
        "completed_at": completed_at,
        "status": "failed",
        "error_message": error_message,
    }
    logger.warning("Updating ingestion run %s to status='failed'...", run_id)
    try:
        response = client.table("ingestion_runs").update(update_payload).eq("id", run_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error("Failed to record failure state in 'ingestion_runs': %s", str(e))
        return None


def run_phase_2_source_management() -> bool:
    """Executes the Phase 2 Source Management verification workflow.

    Returns:
        bool: True if test passes, False otherwise.
    """
    # Step 1: Validate Configuration
    logger.info("Validating environment configuration...")
    try:
        Config.validate()
    except Exception as e:
        logger.error("Configuration error: %s", str(e))
        print(f"\n[FAILED] Configuration Error: {e}")
        return False

    # Step 2: Database Connectivity Check
    logger.info("Connecting to Supabase PostgreSQL database...")
    try:
        client = get_supabase_client()
        if not test_connection():
            print("\n[FAILED] Database connectivity test failed.")
            return False
    except Exception as e:
        logger.error("Database connection error: %s", str(e))
        print(f"\n[FAILED] Database Connection Error: {e}")
        return False

    # Step 3: Source Abstraction Initialization (MyScheme)
    logger.info("Initializing MyScheme source abstraction...")
    myscheme_source = MySchemeSource()
    try:
        source_record = myscheme_source.load_source_record(client)
    except SourceNotFoundError as e:
        logger.error("Source not found error: %s", str(e))
        print(f"\n[FAILED] Source Lookup Error: {e}")
        return False
    except InactiveSourceError as e:
        logger.error("Inactive source error: %s", str(e))
        print(f"\n[FAILED] Inactive Source Error: {e}")
        return False
    except InvalidSourceConfigError as e:
        logger.error("Invalid source config error: %s", str(e))
        print(f"\n[FAILED] Source Config Error: {e}")
        return False
    except SourceError as e:
        logger.error("Source error: %s", str(e))
        print(f"\n[FAILED] Source Error: {e}")
        return False

    # Perform lightweight controlled availability check
    fetch_result = myscheme_source.fetch()

    # Step 4: Display Output as Required by Phase 2 Specification
    print("=" * 60)
    print("RuralEdge — Government Data Ingestion Pipeline")
    print("=" * 60)
    print()
    print(f"Source: {myscheme_source.source_name}")
    print(f"Organization: {myscheme_source.organization or 'Government of India'}")
    print(f"URL: {myscheme_source.base_url}")
    print(f"Status: {'active' if myscheme_source.is_active else 'inactive'}")
    print()

    # Step 5: Ingestion Run Lifecycle Tracking
    run_record = None
    try:
        run_record = create_ingestion_run(
            client=client,
            source_id=myscheme_source.source_id,
            metadata={
                "phase": "phase_2_source_management",
                "source_name": myscheme_source.source_name,
                "availability_check": fetch_result.get("availability"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        # Mark run as completed
        completed_record = update_ingestion_run_completed(
            client=client,
            run_id=run_record["id"],
            documents_found=0,
            documents_processed=0,
            documents_failed=0,
            additional_metadata={
                "phase": "phase_2_source_management",
                "source_name": myscheme_source.source_name,
                "result": "SUCCESS",
            },
        )
        logger.info(
            "Ingestion run %s completed successfully for source %s.",
            completed_record["id"],
            myscheme_source.source_name,
        )

        print("Source management test successful.")
        print()
        print("=" * 60)
        return True

    except Exception as e:
        logger.error("Error during ingestion_runs lifecycle management: %s", str(e))
        if run_record and "id" in run_record:
            update_ingestion_run_failed(client, run_record["id"], str(e))
        print(f"\n[FAILED] Ingestion Run Lifecycle Error: {e}")
        return False


if __name__ == "__main__":
    success = run_phase_2_source_management()
    sys.exit(0 if success else 1)
