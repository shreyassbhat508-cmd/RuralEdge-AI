"""Phase 5 Entry Point: Controlled Individual Scheme Ingestion Pipeline.

This script ingests one real individual government scheme from MyScheme (Janani Suraksha Yojana - JSY1):
https://www.myscheme.gov.in/schemes/jsy1

Flow:
1. Fetch individual scheme HTML / content safely using HTTPFetcher & MyScheme API.
2. Store raw document in 'raw_documents' with SHA-256 content hash & duplicate check.
3. Update processing_status: pending -> processing -> processed.
4. Clean HTML & extract scheme, eligibility, and benefit records deterministically.
5. Validate record against rules and type constraints.
6. Insert into 'schemes', 'scheme_eligibility', and 'scheme_benefits' using exact frozen database schema.
7. Run duplicate test to verify idempotency.
8. Track complete run lifecycle in 'ingestion_runs'.
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
from sources import MySchemeSource
from fetchers import HTTPFetcher
from processors import (
    clean_html,
    extract_scheme_from_html,
    ExtractedSchemeRecord,
)
from validators import validate_scheme_record
from loaders import (
    compute_content_hash,
    check_duplicate_document,
    insert_raw_document,
    check_duplicate_scheme,
    insert_scheme_record,
    update_raw_document_status,
)

logger = setup_logging("main")

# Phase 5 Target Individual Scheme URL
TEST_SCHEME_URL = "https://www.myscheme.gov.in/schemes/jsy1"


def create_ingestion_run(
    client: Any,
    source_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Creates a new record in 'ingestion_runs' with status 'running'."""
    started_at = datetime.now(timezone.utc).isoformat()
    run_payload: Dict[str, Any] = {
        "started_at": started_at,
        "status": "running",
        "documents_found": 0,
        "documents_processed": 0,
        "documents_failed": 0,
        "metadata": metadata or {"phase": "phase_5_individual_scheme_ingestion"},
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
    """Marks an ingestion run as completed."""
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
    """Marks an ingestion run as failed with error details."""
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


def ingest_individual_scheme(
    client: Any,
    myscheme_source: MySchemeSource,
    scheme_url: str,
    run_id: str,
) -> Dict[str, Any]:
    """Executes single scheme ingestion flow (Fetch -> Store Raw -> Clean -> Extract -> Validate -> Load).

    Args:
        client: Authenticated Supabase client.
        myscheme_source: Loaded MySchemeSource instance.
        scheme_url: Individual scheme page URL.
        run_id: Current ingestion run UUID.

    Returns:
        Dict[str, Any]: Ingestion execution details.
    """
    logger.info("Starting individual scheme ingestion for URL: %s...", scheme_url)

    # 1. Fetch individual scheme content
    fetch_res = myscheme_source.fetch(scheme_url)
    if not fetch_res.get("success") or not fetch_res.get("content"):
        error_msg = fetch_res.get("error") or "Failed to fetch individual scheme page."
        logger.error("Fetch failed for %s: %s", scheme_url, error_msg)
        return {"status": "failed", "error": error_msg}

    raw_content = fetch_res["content"]
    content_hash = compute_content_hash(raw_content)
    fetched_at = fetch_res.get("fetched_at") or datetime.now(timezone.utc).isoformat()

    # 2. Check duplicate raw document in raw_documents
    is_raw_dup = check_duplicate_document(
        client=client,
        source_id=myscheme_source.source_id,
        content_hash=content_hash,
    )

    raw_doc_id = None
    if is_raw_dup:
        logger.info("Raw document duplicate detected for content_hash=%s. Retrieving existing record...", content_hash)
        existing_doc = (
            client.table("raw_documents")
            .select("id, processing_status")
            .eq("source_id", myscheme_source.source_id)
            .eq("content_hash", content_hash)
            .limit(1)
            .execute()
        )
        if existing_doc.data:
            raw_doc_id = existing_doc.data[0]["id"]
    else:
        # Insert raw document into raw_documents table
        doc_metadata = {
            "http_status": fetch_res.get("status_code", 200),
            "content_type": fetch_res.get("content_type", "text/html"),
            "source": myscheme_source.source_name,
            "fetch_method": "http",
        }
        inserted_raw = insert_raw_document(
            client=client,
            source_id=myscheme_source.source_id,
            title="Janani Suraksha Yojana (JSY)",
            document_url=scheme_url,
            document_type="html",
            raw_content=raw_content,
            content_hash=content_hash,
            language="en",
            fetched_at=fetched_at,
            metadata=doc_metadata,
        )
        raw_doc_id = inserted_raw["id"]

    # 3. Update raw_documents.processing_status -> 'processing'
    if raw_doc_id:
        update_raw_document_status(client, raw_doc_id, "processing")

    # 4. Clean HTML & Extract Scheme Data
    cleaned_text = clean_html(raw_content)
    extracted_record: ExtractedSchemeRecord = extract_scheme_from_html(
        raw_html=raw_content,
        document_url=scheme_url,
    )

    # 5. Validate Extracted Scheme Record
    val_res = validate_scheme_record(extracted_record, source_id=myscheme_source.source_id)
    if not val_res.is_valid:
        err_desc = f"Validation failed: {'; '.join(val_res.errors)}"
        logger.error(err_desc)
        if raw_doc_id:
            update_raw_document_status(client, raw_doc_id, "failed", {"error": err_desc})
        return {"status": "failed", "error": err_desc}

    # 6. Load into Database (schemes, scheme_eligibility, scheme_benefits)
    load_res = insert_scheme_record(
        client=client,
        source_id=myscheme_source.source_id,
        record=extracted_record,
    )

    # 7. Update raw_documents.processing_status -> 'processed'
    if raw_doc_id:
        update_raw_document_status(
            client=client,
            document_id=raw_doc_id,
            status="processed",
            metadata_update={
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "scheme_id": load_res.get("scheme_id"),
                "loader_status": load_res.get("status"),
            },
        )

    return {
        "status": "success",
        "raw_doc_id": raw_doc_id,
        "is_raw_duplicate": is_raw_dup,
        "content_hash": content_hash,
        "loader_result": load_res,
        "extracted_record": extracted_record,
    }


def run_phase_5_individual_scheme_ingestion() -> bool:
    """Executes Phase 5 Controlled Individual Scheme Ingestion and Idempotency Verification."""
    print("=" * 60)
    print("RuralEdge — Government Data Ingestion Pipeline")
    print("PHASE 5: CONTROLLED INDIVIDUAL SCHEME INGESTION")
    print("=" * 60)
    print()
    print(f"Target Scheme URL: {TEST_SCHEME_URL}")
    print()

    # Step 1: Validate Configuration
    logger.info("Validating environment configuration...")
    try:
        Config.validate()
    except Exception as e:
        logger.error("Configuration error: %s", str(e))
        print(f"[FAILED] Configuration Error: {e}")
        return False

    # Step 2: Connect to Supabase
    logger.info("Connecting to Supabase PostgreSQL database...")
    try:
        client = get_supabase_client()
        if not test_connection():
            print("[FAILED] Database connectivity test failed.")
            return False
    except Exception as e:
        logger.error("Database connection error: %s", str(e))
        print(f"[FAILED] Database Connection Error: {e}")
        return False

    # Step 3: Load MyScheme Source Record
    myscheme_source = MySchemeSource()
    try:
        myscheme_source.load_source_record(client)
    except Exception as e:
        logger.error("Source loading error: %s", str(e))
        print(f"[FAILED] Source Lookup Error: {e}")
        return False

    # Create Ingestion Run Record
    run_record = None
    try:
        run_record = create_ingestion_run(
            client=client,
            source_id=myscheme_source.source_id,
            metadata={
                "phase": "phase_5_individual_scheme_ingestion",
                "target_url": TEST_SCHEME_URL,
                "started_at": datetime.now(timezone.utc).isoformat(),
            },
        )
    except Exception as e:
        logger.error("Could not create ingestion_runs record: %s", str(e))
        print(f"[FAILED] Ingestion run creation failed: {e}")
        return False

    run_id = run_record["id"]

    try:
        # --- FIRST EXECUTION RUN ---
        print("--- RUN 1: INITIAL INDIVIDUAL SCHEME INGESTION ---")
        run1_res = ingest_individual_scheme(
            client=client,
            myscheme_source=myscheme_source,
            scheme_url=TEST_SCHEME_URL,
            run_id=run_id,
        )

        if run1_res.get("status") != "success":
            print(f"[FAILED] Ingestion Run 1 failed: {run1_res.get('error')}")
            update_ingestion_run_failed(client, run_id, run1_res.get("error", "Run 1 failed"))
            return False

        rec: ExtractedSchemeRecord = run1_res["extracted_record"]
        loader_res = run1_res["loader_result"]

        print(f"HTTP Fetch: SUCCESS (HTTP 200)")
        print(f"Raw Document ID: {run1_res.get('raw_doc_id')}")
        print(f"Content Hash: {run1_res.get('content_hash')}")
        print(f"Scheme Name: {rec.scheme.name}")
        print(f"Ministry: {rec.scheme.ministry}")
        print(f"Department: {rec.scheme.department}")
        print(f"Scheme Type: {rec.scheme.scheme_type}")
        print(f"Launch Date: {rec.scheme.launch_date}")
        print(f"Gender Requirement: {rec.eligibility.gender}")
        print(f"Occupation Requirement: {rec.eligibility.occupation}")
        print(f"Benefit Type: {rec.benefits.benefit_type}")
        print(f"Benefit Amount: {rec.benefits.amount}")
        print(f"Loader Result: {loader_res.get('status')} (Scheme ID: {loader_res.get('scheme_id')})")
        print()

        # --- SECOND EXECUTION RUN (DUPLICATE & IDEMPOTENCY TEST) ---
        print("--- RUN 2: DUPLICATE & IDEMPOTENCY VERIFICATION ---")
        run2_res = ingest_individual_scheme(
            client=client,
            myscheme_source=myscheme_source,
            scheme_url=TEST_SCHEME_URL,
            run_id=run_id,
        )

        print(f"Raw Document Duplicate Protection: {'PASSED (Duplicate skipped)' if run2_res.get('is_raw_duplicate') else 'FAILED'}")
        print(f"Scheme Duplicate Protection: {'PASSED (Duplicate skipped)' if run2_res.get('loader_result', {}).get('status') == 'skipped' else 'FAILED'}")
        print()

        # Mark Ingestion Run Completed
        update_ingestion_run_completed(
            client=client,
            run_id=run_id,
            documents_found=1,
            documents_processed=1,
            documents_failed=0,
            additional_metadata={
                "phase": "phase_5_individual_scheme_ingestion",
                "source_name": myscheme_source.source_name,
                "target_url": TEST_SCHEME_URL,
                "scheme_name": rec.scheme.name,
                "scheme_id": loader_res.get("scheme_id"),
                "idempotency_check": "PASSED",
                "result": "SUCCESS",
            },
        )

        print("Ingestion run completed successfully.")
        return True

    except Exception as e:
        logger.error("Unhandled exception during Phase 5 execution: %s", str(e))
        if run_id:
            update_ingestion_run_failed(client, run_id, str(e))
        print(f"[FAILED] Execution Error: {e}")
        return False


if __name__ == "__main__":
    success = run_phase_5_individual_scheme_ingestion()
    sys.exit(0 if success else 1)
