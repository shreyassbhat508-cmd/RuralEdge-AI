"""Database connection module for the RuralEdge Government Data Ingestion Pipeline.

Initializes, validates, and exports the Supabase PostgreSQL client instance.
"""

from typing import Optional
from config import Config, setup_logging

logger = setup_logging("database")

try:
    from supabase import Client, create_client
except ImportError:
    logger.error(
        "The 'supabase' library is not installed. "
        "Please run 'pip install -r requirements.txt'."
    )
    Client = None  # type: ignore
    create_client = None  # type: ignore


_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Initializes (if needed) and returns the singleton Supabase client.

    Validates configuration before establishing the client.

    Returns:
        Client: An authenticated Supabase client instance.

    Raises:
        RuntimeError: If supabase library is not installed or initialization fails.
        ValueError: If configuration values are invalid or missing.
    """
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    if create_client is None:
        raise RuntimeError(
            "Supabase client library is not installed. Run: pip install -r requirements.txt"
        )

    # Validate configuration
    Config.validate()

    try:
        logger.info(
            "Initializing Supabase client (URL: %s, Key: %s)",
            Config.masked_url(),
            Config.masked_key(),
        )
        _supabase_client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        logger.info("Supabase client initialized successfully.")
        return _supabase_client
    except Exception as e:
        logger.error("Failed to initialize Supabase client: %s", str(e))
        raise RuntimeError(f"Failed to initialize Supabase client: {e}") from e


def test_connection() -> bool:
    """Tests basic connectivity to the Supabase database.

    Attempts a lightweight query on the 'government_sources' table.

    Returns:
        bool: True if connection is healthy, False otherwise.
    """
    try:
        client = get_supabase_client()
        logger.info("Testing connection by querying 'government_sources' table...")
        response = client.table("government_sources").select("id, name").limit(1).execute()
        logger.info(
            "Database connectivity test successful. Retrieved %d record(s).",
            len(response.data) if response.data else 0,
        )
        return True
    except Exception as e:
        logger.error("Database connectivity test failed: %s", str(e))
        return False


# Lazy initialization helper for module-level export
class _SupabaseProxy:
    """Proxy object that defers client initialization until first access."""

    def __getattr__(self, name):
        client = get_supabase_client()
        return getattr(client, name)


supabase: Client = _SupabaseProxy()  # type: ignore
