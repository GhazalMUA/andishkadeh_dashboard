
from celery import Celery
import os
import pytz

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
app = Celery('dashboard', broker='amqp://guest:guest@localhost:5672//')
# Optional: Use a more lenient retry policy for task retries
app.conf.timezone = 'Asia/Tehran'  # Change this to your timezone
app.conf.enable_utc = True
app.conf.task_acks_late = True
app.conf.worker_prefetch_multiplier = 10
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
# Enable retries even with time drift
app.conf.task_retries = 5
app.conf.task_retry_delay = 10  # Delay for retries in seconds
app.conf.task_track_started = True
app.conf.broker_transport_options = {
    'visibility_timeout': 3600  # Set this to a higher value, e.g., 1 hour
}

app.conf.task_time_limit = 3600  # Allow each task to run for 1 hour
app.conf.task_soft_time_limit = 300  # Gracefully handle a task running for 5 minutes
