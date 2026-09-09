"""Scheme Loader module for the RuralEdge Government Data Ingestion Pipeline.

Handles duplicate detection for schemes, relational database insertion into 'schemes',
'scheme_eligibility', and 'scheme_benefits' tables in Supabase PostgreSQL,
and manages raw document processing status transitions.
"""

from typing import Any, Dict, Optional
from config import setup_logging
from processors.scheme_extractor import ExtractedSchemeRecord
from validators.scheme_validator import validate_scheme_record

logger = setup_logging("loaders.scheme")


def check_duplicate_scheme(
    client: Any,
    source_id: str,
    official_url: Optional[str],
    name: str,
) -> bool:
    """Checks whether a scheme with matching official_url or name already exists for a source.

    Args:
        client: Authenticated Supabase client instance.
        source_id (str): UUID of the government source.
        official_url (Optional[str]): Scheme official/source URL.
        name (str): Scheme name.

    Returns:
        bool: True if a matching scheme exists, False otherwise.
    """
    logger.info("Checking duplicate scheme for source_id=%s, name='%s'...", source_id, name)
    try:
        # Check by official_url first if available
        if official_url:
            url_res = (
                client.table("schemes")
                .select("id, name")
                .eq("source_id", source_id)
                .eq("official_url", official_url)
                .limit(1)
                .execute()
            )
            if url_res.data and len(url_res.data) > 0:
                logger.info("Duplicate scheme found by official_url (ID: %s).", url_res.data[0].get("id"))
                return True

        # Check by name (exact case-insensitive match)
        name_res = (
            client.table("schemes")
            .select("id, name")
            .eq("source_id", source_id)
            .ilike("name", name)
            .limit(1)
            .execute()
        )
        if name_res.data and len(name_res.data) > 0:
            logger.info("Duplicate scheme found by name (ID: %s).", name_res.data[0].get("id"))
            return True

        logger.info("No duplicate scheme found for '%s'.", name)
        return False
    except Exception as e:
        logger.error("Error querying 'schemes' table for duplicate check: %s", str(e))
        raise RuntimeError(f"Duplicate scheme check failed: {e}") from e


def insert_scheme_record(
    client: Any,
    source_id: str,
    record: ExtractedSchemeRecord,
) -> Dict[str, Any]:
    """Inserts a validated scheme record, eligibility criteria, and benefits into Supabase PostgreSQL.

    Args:
        client: Authenticated Supabase client instance.
        source_id (str): UUID of the government source.
        record (ExtractedSchemeRecord): Extracted and validated scheme data.

    Returns:
        Dict[str, Any]: Result summary dictionary containing inserted IDs or skip status.

    Raises:
        ValueError: If validation fails.
        RuntimeError: If database insertion fails.
    """
    # 1. Validate record
    val_res = validate_scheme_record(record, source_id=source_id)
    if not val_res.is_valid:
        error_msg = f"Validation failed: {'; '.join(val_res.errors)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    scheme_dict = record.scheme.to_dict()
    scheme_name = scheme_dict["name"]
    official_url = scheme_dict.get("official_url")

    # 2. Check for duplicate scheme
    if check_duplicate_scheme(client, source_id=source_id, official_url=official_url, name=scheme_name):
        logger.info("Skipping insertion for duplicate scheme '%s'.", scheme_name)
        return {
            "status": "skipped",
            "reason": "duplicate_scheme",
            "scheme_name": scheme_name,
        }

    # 3. Insert into 'schemes' table
    scheme_payload = {
        "source_id": source_id,
        "name": scheme_name,
        "short_name": scheme_dict.get("short_name"),
        "ministry": scheme_dict.get("ministry"),
        "department": scheme_dict.get("department"),
        "description": scheme_dict.get("description"),
        "scheme_type": scheme_dict.get("scheme_type"),
        "official_url": official_url,
        "application_url": scheme_dict.get("application_url"),
        "launch_date": scheme_dict.get("launch_date"),
        "status": scheme_dict.get("status", "active"),
        "target_beneficiaries": scheme_dict.get("target_beneficiaries"),
        "states": scheme_dict.get("states"),
        "metadata": scheme_dict.get("metadata", {}),
    }

    logger.info("Inserting scheme record '%s' into 'schemes' table...", scheme_name)
    scheme_resp = client.table("schemes").insert(scheme_payload).execute()
    if not scheme_resp.data or len(scheme_resp.data) == 0:
        raise RuntimeError("Failed to insert into 'schemes' table; no data returned.")

    inserted_scheme = scheme_resp.data[0]
    scheme_id = inserted_scheme["id"]
    logger.info("Scheme inserted successfully (Scheme ID: %s).", scheme_id)

    # 4. Insert into 'scheme_eligibility' table linked by scheme_id
    eligibility_dict = record.eligibility.to_dict()
    eligibility_payload = {
        "scheme_id": scheme_id,
        "category": eligibility_dict.get("category"),
        "min_age": eligibility_dict.get("min_age"),
        "max_age": eligibility_dict.get("max_age"),
        "gender": eligibility_dict.get("gender"),
        "occupation": eligibility_dict.get("occupation"),
        "income_min": eligibility_dict.get("income_min"),
        "income_max": eligibility_dict.get("income_max"),
        "education": eligibility_dict.get("education"),
        "location_requirement": eligibility_dict.get("location_requirement"),
        "caste_category": eligibility_dict.get("caste_category"),
        "disability_required": eligibility_dict.get("disability_required"),
        "land_required": eligibility_dict.get("land_required"),
        "business_required": eligibility_dict.get("business_required"),
        "other_conditions": eligibility_dict.get("other_conditions"),
        "eligibility_data": eligibility_dict.get("eligibility_data", {}),
    }

    logger.info("Inserting eligibility record for scheme_id=%s...", scheme_id)
    elig_resp = client.table("scheme_eligibility").insert(eligibility_payload).execute()
    elig_id = elig_resp.data[0]["id"] if elig_resp.data else None

    # 5. Insert into 'scheme_benefits' table linked by scheme_id
    benefit_dict = record.benefits.to_dict()
    benefit_payload = {
        "scheme_id": scheme_id,
        "benefit_type": benefit_dict.get("benefit_type"),
        "amount": benefit_dict.get("amount"),
        "interest_rate": benefit_dict.get("interest_rate"),
        "subsidy_percentage": benefit_dict.get("subsidy_percentage"),
        "maximum_amount": benefit_dict.get("maximum_amount"),
        "repayment_period_months": benefit_dict.get("repayment_period_months"),
        "moratorium_months": benefit_dict.get("moratorium_months"),
        "description": benefit_dict.get("description"),
        "benefit_data": benefit_dict.get("benefit_data", {}),
    }

    logger.info("Inserting benefits record for scheme_id=%s...", scheme_id)
    benefit_resp = client.table("scheme_benefits").insert(benefit_payload).execute()
    benefit_id = benefit_resp.data[0]["id"] if benefit_resp.data else None

    return {
        "status": "inserted",
        "scheme_id": scheme_id,
        "eligibility_id": elig_id,
        "benefit_id": benefit_id,
        "scheme_name": scheme_name,
    }


def update_raw_document_status(
    client: Any,
    document_id: str,
    status: str,
    metadata_update: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Updates raw_documents.processing_status ('pending' -> 'processing' -> 'processed' / 'failed').

    Args:
        client: Authenticated Supabase client.
        document_id (str): UUID of raw document.
        status (str): New status ('processing', 'processed', 'failed').
        metadata_update (Optional[Dict[str, Any]]): Optional metadata updates.

    Returns:
        Optional[Dict[str, Any]]: Updated raw document record.
    """
    logger.info("Updating raw_document %s processing_status to '%s'...", document_id, status)
    update_payload: Dict[str, Any] = {"processing_status": status}

    if metadata_update:
        # Fetch current metadata to merge
        try:
            curr = client.table("raw_documents").select("metadata").eq("id", document_id).limit(1).execute()
            if curr.data:
                curr_meta = curr.data[0].get("metadata") or {}
                curr_meta.update(metadata_update)
                update_payload["metadata"] = curr_meta
        except Exception as e:
            logger.warning("Could not fetch current raw document metadata for merge: %s", str(e))
            update_payload["metadata"] = metadata_update

    try:
        resp = client.table("raw_documents").update(update_payload).eq("id", document_id).execute()
        return resp.data[0] if resp.data else None
    except Exception as e:
        logger.error("Failed to update raw_document processing_status: %s", str(e))
        return None
