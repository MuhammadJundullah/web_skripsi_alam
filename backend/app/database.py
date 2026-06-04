from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def create_db_and_tables():
    # Import all models here before calling create_all
    # so that they are registered on the metadata
    from . import models
    print("--- Creating database and tables ---")
    Base.metadata.create_all(bind=engine)
    ensure_detection_job_progress_columns()

def ensure_detection_job_progress_columns():
    inspector = inspect(engine)
    if "detection_jobs" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("detection_jobs")}
    column_definitions = {
        "progress_percent": "REAL DEFAULT 0.0",
        "processed_frames": "INTEGER DEFAULT 0",
        "total_frames": "INTEGER DEFAULT 0",
        "error_message": "VARCHAR",
    }

    with engine.begin() as connection:
        for column_name, column_definition in column_definitions.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(f"ALTER TABLE detection_jobs ADD COLUMN {column_name} {column_definition}")
                )
