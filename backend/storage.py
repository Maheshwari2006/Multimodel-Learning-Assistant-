
import os

from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
BUCKET_NAME = "documents"


def get_supabase():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError("Supabase environment variables are missing.")

    return create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY
    )


def upload_to_storage(file_path, file_data, content_type):
    client = get_supabase()

    return client.storage.from_(BUCKET_NAME).upload(
        path=file_path,
        file=file_data,
        file_options={
            "content-type": content_type or "application/octet-stream",
            "upsert": "false"
        }
    )


def download_from_storage(file_path):
    client = get_supabase()

    return client.storage.from_(BUCKET_NAME).download(file_path)


def delete_from_storage(file_path):
    client = get_supabase()

    return client.storage.from_(BUCKET_NAME).remove([file_path])
