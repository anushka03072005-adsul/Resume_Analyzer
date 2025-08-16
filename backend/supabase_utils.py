# supabase_utils.py
import requests
from supabase import create_client

# Supabase credentials (hardcoded for convenience)
SUPABASE_URL = "https://pccdjaplsjxrifypznlb.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBjY2RqYXBsc2p4cmlmeXB6bmxiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTI3MDUwOSwiZXhwIjoyMDcwODQ2NTA5fQ.bc3YP-u1diyJ5dpj1a5duiu58vPBwkzfdLvsmmXiLLM"

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def download_resume(user_id, filename, save_as="downloaded_resume.pdf"):
    """
    Download a user's uploaded resume from Supabase storage.
    """
    signed_url = supabase.storage.from_("resumes").create_signed_url(f"{user_id}/{filename}", 60)
    file_url = signed_url["signedURL"]
    file_data = requests.get(file_url)
    with open(save_as, "wb") as f:
        f.write(file_data.content)
    print(f"Resume saved as {save_as}")


def download_analysis_pdf(user_id, filename, save_as="analysis.pdf"):
    """
    Download a previously generated analysis PDF from Supabase storage.
    """
    storage_path = f"{user_id}/{filename}"
    signed_url = supabase.storage.from_("resumes").create_signed_url(storage_path, 60)
    file_url = signed_url["signedURL"]
    file_data = requests.get(file_url)
    with open(save_as, "wb") as f:
        f.write(file_data.content)
    print(f"Analysis PDF saved as {save_as}")
