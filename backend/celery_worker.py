from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


def mask_redis_url(raw_url: str | None) -> str:
    if not raw_url:
        return "<missing>"

    if not raw_url.startswith(("redis://", "rediss://")) or "@" not in raw_url:
        return raw_url

    scheme, remainder = raw_url.split("://", 1)
    userinfo, host_and_path = remainder.rsplit("@", 1)
    if ":" in userinfo:
        username, _password = userinfo.split(":", 1)
        masked_userinfo = f"{username}:***"
    else:
        masked_userinfo = "***"

    return f"{scheme}://{masked_userinfo}@{host_and_path}"


print(f"--- Celery Worker starting with Redis URL: {mask_redis_url(os.getenv('REDIS_URL'))} ---")

# This imports the Celery app instance from the app package
from app.celery_utils import celery_app
