from sqlalchemy.orm import Session
from . import models
from datetime import datetime

def get_job(db: Session, job_id: int):
    return db.query(models.DetectionJob).filter(models.DetectionJob.id == job_id).first()

def get_jobs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DetectionJob).order_by(models.DetectionJob.upload_time.desc()).offset(skip).limit(limit).all()

def create_detection_job(db: Session, filename: str, original_filename: str):
    db_job = models.DetectionJob(
        filename=filename, 
        original_filename=original_filename,
        status="PENDING",
        progress_percent=0.0,
        processed_frames=0,
        total_frames=0,
        error_message=None
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def update_job_task_id(db: Session, job_id: int, task_id: str):
    db_job = get_job(db, job_id)
    if db_job:
        db_job.task_id = task_id
        db.commit()
        db.refresh(db_job)
    return db_job

def set_job_status(db: Session, job_id: int, status: str):
    db_job = get_job(db, job_id)
    if db_job:
        db_job.status = status
        if status == "PENDING":
            db_job.progress_percent = 0.0
            db_job.processed_frames = 0
            db_job.total_frames = 0
            db_job.error_message = None
        db.commit()
        db.refresh(db_job)
    return db_job

def update_job_progress(db: Session, job_id: int, processed_frames: int, total_frames: int):
    db_job = get_job(db, job_id)
    if db_job:
        safe_total_frames = max(int(total_frames or 0), 0)
        safe_processed_frames = max(int(processed_frames or 0), 0)
        if safe_total_frames > 0:
            progress_percent = min(99.0, round((safe_processed_frames / safe_total_frames) * 100, 2))
        else:
            progress_percent = 0.0

        db_job.processed_frames = safe_processed_frames
        db_job.total_frames = safe_total_frames
        db_job.progress_percent = progress_percent
        db.commit()
        db.refresh(db_job)
    return db_job

def complete_job(db: Session, job_id: int, status: str, output_path: str = None, error_message: str = None):
    db_job = get_job(db, job_id)
    if db_job:
        db_job.status = status
        db_job.output_path = output_path
        db_job.error_message = error_message
        if status == "SUCCESS":
            db_job.progress_percent = 100.0
            if db_job.total_frames and db_job.processed_frames < db_job.total_frames:
                db_job.processed_frames = db_job.total_frames
        db_job.completion_time = datetime.utcnow()
        db.commit()
        db.refresh(db_job)
    return db_job

def delete_job(db: Session, job_id: int):
    db_job = get_job(db, job_id)
    if db_job:
        db.delete(db_job)
        db.commit()
    return db_job

# --- Settings CRUD --- 

def get_setting(db: Session, key: str):
    return db.query(models.Setting).filter(models.Setting.key == key).first()

def update_setting(db: Session, key: str, value: str):
    db_setting = get_setting(db, key)
    if db_setting:
        db_setting.value = value
    else:
        db_setting = models.Setting(key=key, value=value)
        db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting
