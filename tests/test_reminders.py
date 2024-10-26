import pytest
from unittest.mock import MagicMock
# Adjust the import based on your project structure
from fitnessapp.tasks import send_task_reminder_email
from datetime import datetime, timedelta


def test_send_task_reminder_email(mocker, app, client):
    with client:
        client.get('/')
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Mock the database and insert the mock event
        mock_event = {
            'host': 'host@example.com',
            'invited_friend': 'friend@example.com',
            'exercise': 'Yoga',
            'start_time': '10:00 AM',
            'date': today_str  # Today's date
        }

        mock_db = app.mongo.db
        # Insert the mock event into the mock database
        mock_db.events.insert_one(mock_event)
        mock_send = mocker.patch('flask.current_app.mail.send')

        send_task_reminder_email()

        sent_message = mock_send.call_args[0][0]
        assert sent_message.subject == "Hello"
        assert sent_message.recipients == [
            'host@example.com', 'friend@example.com']
        assert sent_message.body == f"Dear User, you have an upcoming event (Yoga) today at 10:00 AM"


def test_send_task_reminder_email_no_events(mocker, app, client):
    with client:
        client.get('/')

        mock_send = mocker.patch('flask.current_app.mail.send')

        send_task_reminder_email()

        # Check that no email was sent
        mock_send.assert_not_called()


def test_send_task_reminder_email_multiple_events(mocker, app, client):
    with client:
        client.get('/')
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Insert multiple mock events
        mock_events = [
            {
                'host': 'host1@example.com',
                'invited_friend': 'friend1@example.com',
                'exercise': 'Yoga',
                'start_time': '10:00 AM',
                'date': today_str
            },
            {
                'host': 'host2@example.com',
                'invited_friend': 'friend2@example.com',
                'exercise': 'Running',
                'start_time': '11:00 AM',
                'date': today_str
            }
        ]

        mock_db = app.mongo.db
        mock_db.events.insert_many(mock_events)  # Insert multiple events
        mock_send = mocker.patch('flask.current_app.mail.send')

        send_task_reminder_email()

        assert mock_send.call_count == 2  # Check if two emails were sent

        # Verify the first email
        sent_message1 = mock_send.call_args_list[0][0][0]
        assert sent_message1.subject == "Hello"
        assert sent_message1.recipients == [
            'host1@example.com', 'friend1@example.com']
        assert sent_message1.body == f"Dear User, you have an upcoming event (Yoga) today at 10:00 AM"

        # Verify the second email
        sent_message2 = mock_send.call_args_list[1][0][0]
        assert sent_message2.subject == "Hello"
        assert sent_message2.recipients == [
            'host2@example.com', 'friend2@example.com']
        assert sent_message2.body == f"Dear User, you have an upcoming event (Running) today at 11:00 AM"


def test_send_task_reminder_email_different_exercises(mocker, app, client):
    exercises = ['Yoga', 'Running', 'Swimming']

    for exercise in exercises:
        with client:
            client.get('/')
            today_str = datetime.now().strftime("%Y-%m-%d")

            mock_event = {
                'host': 'host@example.com',
                'invited_friend': 'friend@example.com',
                'exercise': exercise,
                'start_time': '10:00 AM',
                'date': today_str
            }

            mock_db = app.mongo.db
            mock_db.events.insert_one(mock_event)
            mock_send = mocker.patch('flask.current_app.mail.send')

            send_task_reminder_email()

            sent_message = mock_send.call_args[0][0]
            assert sent_message.body == f"Dear User, you have an upcoming event ({exercise}) today at 10:00 AM"


def test_send_task_reminder_email_future_event(mocker, app, client):
    with client:
        client.get('/')
        future_date = (datetime.now() + timedelta(days=1)
                       ).strftime("%Y-%m-%d")  # Tomorrow

        # Insert a future event
        mock_event = {
            'host': 'host@example.com',
            'invited_friend': 'friend@example.com',
            'exercise': 'Yoga',
            'start_time': '10:00 AM',
            'date': future_date
        }

        mock_db = app.mongo.db
        mock_db.events.insert_one(mock_event)
        mock_send = mocker.patch('flask.current_app.mail.send')

        send_task_reminder_email()

        # Check that no email was sent for a future event
        mock_send.assert_not_called()


def test_send_task_reminder_email_special_characters(mocker, app, client):
    with client:
        client.get('/')
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Insert an event with special characters in the exercise name
        mock_event = {
            'host': 'host@example.com',
            'invited_friend': 'friend@example.com',
            'exercise': 'Yoga & Meditation',
            'start_time': '10:00 AM',
            'date': today_str
        }

        mock_db = app.mongo.db
        mock_db.events.insert_one(mock_event)
        mock_send = mocker.patch('flask.current_app.mail.send')

        send_task_reminder_email()

        sent_message = mock_send.call_args[0][0]
        assert sent_message.body == f"Dear User, you have an upcoming event (Yoga & Meditation) today at 10:00 AM"


def test_send_task_reminder_email_send_failure(mocker, app, client):
    with client:
        client.get('/')
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Insert a valid event
        mock_event = {
            'host': 'host@example.com',
            'invited_friend': 'friend@example.com',
            'exercise': 'Yoga',
            'start_time': '10:00 AM',
            'date': today_str
        }

        mock_db = app.mongo.db
        mock_db.events.insert_one(mock_event)
        mock_send = mocker.patch(
            'flask.current_app.mail.send',
            side_effect=Exception("SMTP Error"))

        with pytest.raises(Exception):
            send_task_reminder_email()

        # Verify that the exception is raised
        assert mock_send.call_count == 1  # Ensure it tried to send the email
