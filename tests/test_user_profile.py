import flask  # Assuming your Flask app is defined in app.py
from flask import session, url_for
from unittest.mock import patch, MagicMock
import pytest
from .conftest import client
import logging
import mongomock
from werkzeug.security import generate_password_hash
from bcrypt import hashpw, gensalt
from datetime import datetime
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def test_successful_user_profile_update(mocker, app, client):
    with client.session_transaction() as sess:
        sess['email'] = 'test@example.com'  #

    now = datetime.now().strftime('%Y-%m-%d')
    mock_user_profile = {
        'email': 'test@example.com',
        'date': now,
        'height': '5.6',
        'weight': '160',
        'goal': 'Maintain weight',
        'target_weight': '150'
    }

    app.mongo.db.profile.insert_one(mock_user_profile)

    response = client.post('/user_profile', data={
        'weight': '150',
        'height': '5.8',
        'goal': 'Lose weight',
        'target_weight': '140'
    })

    assert response.status_code == 302
    record = app.mongo.db.profile.find_one({'email': 'test@example.com', 'date': now})
    assert record is not None, "Record should exist in the database"

    assert record['weight'] == '150'
    assert record['height'] == '5.8'
    assert record['goal'] == 'Lose weight'
    assert record['target_weight'] == '140'

# Test for inserting a new user profile when it does not exist


def test_insert_user_profile(mocker, app, client):
    with client.session_transaction() as sess:
        sess['email'] = 'test@example.com'

    now = datetime.now().strftime('%Y-%m-%d')
    app.mongo.db.profile.delete_many({'email': 'test@example.com', 'date': now})
    response = client.post('/user_profile', data={
        'weight': '150',
        'height': '5.8',
        'goal': 'Gain muscle',
        'target_weight': '160'
    })

    assert response.status_code == 302
    record = app.mongo.db.profile.find_one({'email': 'test@example.com', 'date': now})
    assert record is not None, "New record should be inserted in the database"

    assert record['weight'] == '150'
    assert record['height'] == '5.8'
    assert record['goal'] == 'Gain muscle'
    assert record['target_weight'] == '160'


# Test for when the user is not logged in
def test_user_profile_not_logged_in(client):
    with client.session_transaction() as sess:
        sess.clear()
    response = client.get('/user_profile')
    assert response.status_code == 302


# Test for form validation failure
def test_user_profile_form_validation_failure(mocker, app, client):
    with client.session_transaction() as sess:
        sess['email'] = 'test@example.com'

    response = client.get('/user_profile')
    assert response.status_code == 200


def test_successful_profile_update_flash_message(mocker, app, client):
    with client.session_transaction() as sess:
        sess['email'] = 'test@example.com'

    now = datetime.now().strftime('%Y-%m-%d')
    mock_user_profile = {
        'email': 'test@example.com',
        'date': now,
        'height': '5.6',
        'weight': '160',
        'goal': 'Maintain weight',
        'target_weight': '150'
    }

    app.mongo.db.profile.insert_one(mock_user_profile)

    response = client.post('/user_profile', data={
        'weight': '150',
        'height': '5.8',
        'goal': 'Lose weight',
        'target_weight': '140'
    })


# Test for ensuring correct rendering of the user profile form
def test_render_user_profile_form(mocker, app, client):
    with client.session_transaction() as sess:
        sess['email'] = 'test@example.com'

    response = client.get('/user_profile')
    soup = BeautifulSoup(response.data, 'html.parser')

    assert soup.find('input', {'name': 'weight'}) is not None
    assert soup.find('input', {'name': 'height'}) is not None
    assert soup.find('input', {'name': 'goal'}) is not None
    assert soup.find('input', {'name': 'target_weight'}) is not None
