"""Raw Document Loader module for the RuralEdge Government Data Ingestion Pipeline.

Handles content hashing, duplicate detection against Supabase PostgreSQL,
and insertion of raw documents into the 'raw_documents' table.
"""

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from config import setup_logging

logger = setup_logging("loaders.raw_document")


def compute_content_hash(content: str) -> str:
    """Computes the SHA-256 hash of raw text content.

    Args:
        content (str): Raw text content to hash.

    Returns:
        str: 64-character hexadecimal SHA-256 digest string.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def check_duplicate_document(client: Any, source_id: str, content_hash: str) -> bool:
    """Checks whether a raw document with the same content_hash exists for a source.

    Args:
        client: Authenticated Supabase client instance.
        source_id (str): UUID of the government source.
        content_hash (str): SHA-256 digest of the raw content.

    Returns:
        bool: True if a matching document exists, False otherwise.
    """
    logger.info("Checking duplicate document for source_id=%s, content_hash=%s...", source_id, content_hash)
    try:
        response = (
            client.table("raw_documents")
            .select("id")
            .eq("source_id", source_id)
            .eq("content_hash", content_hash)
            .limit(1)
            .execute()
        )
        is_duplicate = bool(response.data and len(response.data) > 0)
        if is_duplicate:
            logger.info("Duplicate document found (ID: %s).", response.data[0].get("id"))
        else:
            logger.info("No duplicate document found for content_hash=%s.", content_hash)
        return is_duplicate
    except Exception as e:
        logger.error("Error querying 'raw_documents' for duplicate check: %s", str(e))
        raise RuntimeError(f"Duplicate document check failed: {e}") from e


def insert_raw_document(
    client: Any,
    source_id: str,
    title: str,
    document_url: str,
    document_type: str,
    raw_content: str,
    content_hash: str,
    language: str = "en",
    fetched_at: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Inserts a raw document record into the 'raw_documents' table in Supabase.

    Args:
        client: Authenticated Supabase client instance.
        source_id (str): UUID of the government source.
        title (str): Descriptive title of the raw document.
        document_url (str): Source URL of the raw document.
        document_type (str): Format or type of document (e.g. 'html').
        raw_content (str): Full raw text content.
        content_hash (str): SHA-256 hash of raw content.
        language (str): Language code (defaults to 'en').
        fetched_at (Optional[str]): ISO timestamp of fetch time. Defaults to UTC now.
        metadata (Optional[Dict[str, Any]]): Additional safe metadata dictionary.

    Returns:
        Dict[str, Any]: Inserted raw document record from database.

    Raises:
        RuntimeError: If database insertion fails or returns no data.
    """
    if not fetched_at:
        fetched_at = datetime.now(timezone.utc).isoformat()

    payload = {
        "source_id": source_id,
        "title": title,
        "document_url": document_url,
        "document_type": document_type,
        "raw_content": raw_content,
        "content_hash": content_hash,
        "language": language,
        "fetched_at": fetched_at,
        "processing_status": "pending",
        "metadata": metadata or {},
    }

    logger.info("Inserting raw document '%s' into 'raw_documents'...", title)
    try:
        response = client.table("raw_documents").insert(payload).execute()
        if not response.data or len(response.data) == 0:
            raise RuntimeError("Failed to insert into 'raw_documents'; no data returned.")
        record = response.data[0]
        logger.info("Raw document stored successfully (ID: %s).", record.get("id"))
        return record
    except Exception as e:
        logger.error("Supabase error during raw document insertion: %s", str(e))
        raise RuntimeError(f"Failed to insert raw document into database: {e}") from e
