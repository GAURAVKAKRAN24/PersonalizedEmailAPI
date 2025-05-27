from datetime import datetime, timedelta
from utils import send_bulk_emails
import os

def schedule_email_job(scheduler, job_id, time_str, email_user, email_pass, subject, body, companies, attachment_path, file_name):
    
    try:
        # Parse ISO datetime string
        run_time = datetime.fromisoformat(time_str)
    except ValueError:
        raise ValueError("Invalid ISO datetime format. Use format like '2025-05-26T08:00:00'.")

    now = datetime.now()

    # If that time already passed today, schedule for tomorrow
    if run_time <= now:
        run_time += timedelta(days=1)

    def job():
        try:
            send_bulk_emails(email_user, email_pass, subject, body, companies, attachment_path, file_name)
        finally:
            if attachment_path and os.path.exists(attachment_path):
                os.remove(attachment_path)

    scheduler.add_job(
        id=job_id,
        func=job,
        trigger='date',
        run_date=run_time,
        replace_existing=True
    )