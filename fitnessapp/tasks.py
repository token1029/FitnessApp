from celery import shared_task
import logging


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

@shared_task()
def send_task_reminder_email():
    LOGGER.info('sending email')
