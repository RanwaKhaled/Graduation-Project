import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_API_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") 

if not SUPABASE_URL or not SUPABASE_ANON_KEY or not SUPABASE_SERVICE_KEY:
    raise ValueError("Supabase credentials are missing. Please check your .env file.")

# CLIENT 1: The Public Bouncer (Handles Signups & Logins)
supabase_auth: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# CLIENT 2: The Admin (Handles User Management & Data)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)