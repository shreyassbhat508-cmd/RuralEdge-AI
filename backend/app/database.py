import os
from dotenv import load_dotenv, find_dotenv
from supabase import create_client, Client

app_env = os.path.join(os.path.dirname(__file__), ".env")
backend_env = os.path.join(os.path.dirname(__file__), "..", ".env")

if os.path.exists(app_env):
    load_dotenv(app_env)
if os.path.exists(backend_env):
    load_dotenv(backend_env)
load_dotenv(find_dotenv())

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL environment variable is missing in .env")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY environment variable is missing in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
