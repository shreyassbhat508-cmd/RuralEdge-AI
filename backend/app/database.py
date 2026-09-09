import os
from dotenv import find_dotenv, load_dotenv
from supabase import Client, create_client

backend_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))

if os.path.exists(backend_env):
    load_dotenv(backend_env)

load_dotenv(find_dotenv())
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL environment variable is missing")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY environment variable is missing")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
