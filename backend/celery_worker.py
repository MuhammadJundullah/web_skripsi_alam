from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

print(f"--- Celery Worker starting with Redis URL: {os.getenv('REDIS_URL')} ---")

# This imports the Celery app instance from the app package
from app.celery_utils import celery_app
