"""Phase 1 Entry Point: Database Connectivity and Ingestion Run Verification.

This script tests connectivity to the Supabase PostgreSQL database,
looks up the 'MyScheme' source in 'government_sources', and verifies
the lifecycle of an 'ingestion_runs' record (running -> completed/failed).
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

logger = setup_logging("main")


def get_or_lookup_source(client, source_name: str = "MyScheme") -> Optional[Dict[str, Any]]:
    """Looks up a government source record by name.

    Args:
        client: The Supabase client instance.
        source_name: Name of the government source to query.

    Returns:
        Optional[Dict[str, Any]]: The source record dictionary if found, else None.
    """
    logger.info("Looking up government source: '%s'...", source_name)
    try:
        response = (
            client.table("government_sources")
            .select("*")
            .eq("name", source_name)
            .limit(1)
            .execute()
        )
        if response.data and len(response.data) > 0:
            source = response.data[0]
            logger.info(
                "Found source '%s' (ID: %s, Type: %s, Active: %s)",
                source.get("name"),
                source.get("id"),
                source.get("source_type"),
                source.get("is_active"),
            )
            return source

        logger.warning(
            "Source '%s' not found in 'government_sources'. "
            "Checking available sources in database...",
            source_name,
        )
        all_sources_res = (
            client.table("government_sources").select("id, name, is_active").execute()
        )
        if all_sources_res.data:
            logger.info("Existing sources in database: %s", all_sources_res.data)
        else:
            logger.warning("No records currently exist in 'government_sources' table.")
        return None
    except Exception as e:
        logger.error("Error querying 'government_sources': %s", str(e))
        raise


def create_ingestion_run(
    client, source_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None
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
        "metadata": metadata or {"phase": "phase_1_test", "mode": "connectivity_verification"},
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
    client,
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


def update_ingestion_run_failed(client, run_id: str, error_message: str) -> Optional[Dict[str, Any]]:
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


def run_phase_1_test() -> bool:
    """Executes the complete Phase 1 database connection and ingestion run test.

    Returns:
        bool: True if test passes, False otherwise.
    """
    print("=" * 60)
    print(" RuralEdge — Government Data Ingestion Pipeline (Phase 1) ")
    print("=" * 60)

    # Step 1: Configuration Validation
    logger.info("Validating environment configuration...")
    try:
        Config.validate()
        logger.info("Configuration validated: Supabase URL is %s", Config.masked_url())
    except Exception as e:
        logger.error("Configuration validation failed: %s", str(e))
        print("\n[FAILED] Configuration Error:", str(e))
        return False

    # Step 2: Test Database Connectivity
    logger.info("Testing Supabase database connectivity...")
    try:
        client = get_supabase_client()
        if not test_connection():
            print("\n[FAILED] Unable to query database tables. Check connection and permissions.")
            return False
    except Exception as e:
        logger.error("Database connection failed: %s", str(e))
        print("\n[FAILED] Database Connection Error:", str(e))
        return False

    # Step 3: Source Lookup (MyScheme)
    source_record = None
    source_id = None
    try:
        source_record = get_or_lookup_source(client, "MyScheme")
        if source_record:
            source_id = source_record.get("id")
    except Exception as e:
        logger.error("Failed during source lookup: %s", str(e))
        print("\n[FAILED] Source lookup error:", str(e))
        return False

    # Step 4: Ingestion Run Lifecycle Test
    run_record = None
    try:
        # Create run in 'running' state
        run_record = create_ingestion_run(
            client=client,
            source_id=source_id,
            metadata={
                "test_name": "phase_1_connection_test",
                "source_name": "MyScheme" if source_record else "Unlinked (Test)",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        run_id = run_record["id"]

        # Step 5: Mark run as completed
        completed_record = update_ingestion_run_completed(
            client=client,
            run_id=run_id,
            documents_found=0,
            documents_processed=0,
            documents_failed=0,
            additional_metadata={
                "test_name": "phase_1_connection_test",
                "source_name": "MyScheme" if source_record else "Unlinked (Test)",
                "test_result": "SUCCESS",
            },
        )

        print("\n" + "=" * 60)
        print(" PHASE 1 VERIFICATION COMPLETED SUCCESSFULLY ")
        print("=" * 60)
        print(f"Supabase Project URL : {Config.masked_url()}")
        print(f"Government Source    : {source_record.get('name') if source_record else 'None found'}")
        if source_id:
            print(f"Source ID            : {source_id}")
        print(f"Ingestion Run ID     : {completed_record.get('id')}")
        print(f"Initial Status       : running")
        print(f"Final Status         : {completed_record.get('status')}")
        print(f"Started At           : {completed_record.get('started_at')}")
        print(f"Completed At         : {completed_record.get('completed_at')}")
        print("=" * 60 + "\n")
        return True

    except Exception as e:
        logger.error("Ingestion run lifecycle test encountered an error: %s", str(e))
        if run_record and "id" in run_record:
            update_ingestion_run_failed(client, run_record["id"], str(e))
        print("\n[FAILED] Ingestion Run Test Error:", str(e))
        return False


if __name__ == "__main__":
    success = run_phase_1_test()
    sys.exit(0 if success else 1)
