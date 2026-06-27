from .celery_utils import celery_app
from . import crud
from .database import SessionLocal
from ultralytics import YOLO
import os
import cv2
import time

# Define base directory for uploads and outputs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "..", "uploads")
OUTPUTS_DIR = os.path.join(BASE_DIR, "..", "outputs")
WEIGHT_PATH = os.path.join(BASE_DIR, "..", "weight/yolov8n.pt")

# Load the model once when the worker starts
try:
    model = YOLO(WEIGHT_PATH)
except Exception as e:
    print(f"Error loading YOLO model in worker: {e}")
    model = None

@celery_app.task
def process_video_task(job_id: int, confidence: float = 0.1):
    """
    Celery task to process a video, using CRUD functions to update state.
    """
    db = SessionLocal()
    try:
        job = crud.get_job(db, job_id)
        if not job:
            print(f"Error: Job with ID {job_id} not found.")
            return

        crud.set_job_status(db, job_id, "PROCESSING")

        if not model:
            raise ValueError("YOLO model not loaded in worker.")

        video_path = os.path.join(UPLOADS_DIR, job.filename)
        output_path = os.path.join(OUTPUTS_DIR, f"output_{job.filename}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Could not open video file {video_path}")

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        processed_frames = 0
        last_progress_update = time.monotonic()
        progress_update_interval = 1.0

        crud.update_job_progress(db, job_id, processed_frames, total_frames)
        
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            results = model(frame, verbose=False, conf=confidence)
            annotated_frame = results[0].plot()
            out.write(annotated_frame)
            processed_frames += 1

            now = time.monotonic()
            if processed_frames == total_frames or now - last_progress_update >= progress_update_interval:
                crud.update_job_progress(db, job_id, processed_frames, total_frames)
                last_progress_update = now

        cap.release()
        out.release()

        crud.complete_job(db, job_id, "SUCCESS", output_path)
        print(f"--- Video Processing Task SUCCESS for job {job_id} ---")

        # Clean up the original uploaded file
        try:
            os.remove(video_path)
            print(f"Successfully deleted original file: {video_path}")
        except OSError as e:
            print(f"Error deleting original file {video_path}: {e}")

    except Exception as e:
        print(f"Error during video processing task for job {job_id}: {e}")
        crud.complete_job(db, job_id, "FAILURE", error_message=str(e))
    finally:
        db.close()
