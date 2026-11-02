import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials missing in root .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def test_supabase_connection():
    try:
        response = (
            supabase
            .table("benchmark_metrics")
            .select("*")
            .limit(5)
            .execute()
        )

        print("Supabase connection successful!")
        print("Records retrieved:", len(response.data))
        print(response.data)

    except Exception as error:
        print("Supabase connection failed:", error)


if __name__ == "__main__":
    test_supabase_connection()