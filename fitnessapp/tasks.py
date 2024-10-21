from celery import shared_task
import logging
from flask_mail import Message
from flask import current_app
from datetime import timedelta, datetime

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

@shared_task()
def send_task_reminder_email():
    
    

    # today's date in "YYYY-MM-DD" format
    today_str = datetime.now().strftime("%Y-%m-%d")


    events_today = current_app.mongo.db.events.find({
        "date": today_str
    })

    events_list = list(events_today)


    for event in events_list:
        msg = Message(
            subject="Hello",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[event['host'], event['invited_friend']],
        )
        
        msg.body = f"Dear User, you have an upcoming event ({event['exercise']}) today at {event['start_time']}"
        current_app.mail.send(msg)

    
