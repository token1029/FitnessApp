import flask  # Assuming your Flask app is defined in app.py
from flask import session, url_for
from unittest.mock import patch, MagicMock
import pytest
from .conftest import client
import logging
import mongomock
from werkzeug.security import generate_password_hash
from bcrypt import hashpw, gensalt
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)




def mock_token_response():
    return {
        "access_token": "fake-access-token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "fake-refresh-token",
        "userinfo_endpoint": "",
        "token_endpoint": "https://oauth2.googleapis.com/token",
    }


def mock_userinfo_response(email_verified=True):
    return {
        "sub": "1234567890",
        "email": "testuser@gmail.com",
        "email_verified": email_verified,
        "given_name": "Test",
        "picture": "https://example.com/pic.jpg"

    }


def mock_google_provider_cfg():
    return {
        "token_endpoint": "https://oauth2.googleapis.com/token",
        "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo",
    }


def mock_requests_post(url, headers=None, data=None, auth=None):

    return MagicMock(json=MagicMock(return_value={
        "access_token": "fake-access-token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "fake-refresh-token",
    }))


def mock_prepare_token_request(token_endpoint, authorization_response, redirect_url, code):
    return (
        token_endpoint,  # Return the original token endpoint
        {"Content-Type": "application/x-www-form-urlencoded"},  # Headers
        f"code=4223"  # Body of the request
    )


def test_email_password_login_success_given_valid_credentials(mocker, app, client):
    # Mock session and form
    with client:
        with client.session_transaction() as sess:
            sess.clear()

        mock_user = {
                'email': 'test@gmail.com',
                'pwd': hashpw("correctpassword".encode('utf-8'), gensalt()),
                'name': 'Test User',
            }
        app.mongo.db.user.insert_one({
                'name': mock_user['email'], 
                'email': mock_user['email'], 
                'pwd': mock_user['pwd']
                })
            
        app.mongo.db.profile.insert_one({'email': mock_user['email'],
                                        'date': "2022-02-18",
                                                        'height': 20,
                                                        'weight': 30,
                                                        'goal': 90,
                                                        'target_weight': 123})
       
        response = client.get('/login')  # Adjust to your endpoint
        soup = BeautifulSoup(response.data, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']  # Adjust the name based on your setup



       
        client.post('/login', data={
                'email':'test@gmail.com', # mock_user['email'],
                'password': 'correctpassword',
                'csrf_token': csrf_token
            })

        
        with client.session_transaction() as sess:
            assert sess['email'] == 'test@gmail.com'
            assert sess['name'] == 'test@gmail.com'
            #pass

def test_email_password_login_failure_given_invalid_email(mocker, app, client):
    # Mock session and form
    with client:
        with client.session_transaction() as sess:
            sess.clear()

        response = client.post('/login', data={
            'email':"invalid@gmail.com", 
            'password':"wrongpassword",
        })
        
        assert response.status_code == 400


def test_email_password_login_failure_given_incorrect_password(mocker, app, client):
    with client:
        with client.session_transaction() as sess:
            sess.clear()
            
        mock_user = {
            'email': 'test@gmail.com',
            'pwd': hashpw("correctpassword".encode("utf-8"), gensalt()),
            'name': 'Test User',
        }
        app.mongo.db.user.insert_one({
            'name': mock_user['name'], 
            'email': mock_user['email'], 
            'pwd': mock_user['pwd'],
            'temp': mock_user['pwd']
        })
        
        response = client.post('/login', data={
            'email': mock_user['email'],
            'password': "wrongpassword"
        })

        assert response.status_code == 400


# def test_redirect_to_google_page(client):
#     response = client.get('/google-login')
#     assert response.status_code == 302


def test_google_login_callback_unverified_email(mocker, client):
    mock_get = mocker.patch('requests.get')
    mock_get.side_effect = [
        MagicMock(json=MagicMock(return_value=mock_google_provider_cfg())),
        MagicMock(json=MagicMock(return_value={
            "sub": "1234567890",
            "email": "testuser@gmail.com",
            "email_verified": False,  # Simulate verified email
            "given_name": "Test",
            "picture": "https://example.com/pic.jpg"
        })),
    ]

    mock_post = mocker.patch('requests.post', side_effect=mock_requests_post)

    response = client.get('/login/callback?code=fake-auth-code')

    # Assertions for the response when the email is not verified
    assert response.status_code == 400
    assert b"User email not available or not verified by Google." in response.data

# Test case for successful login with verified email


def test_google_login_callback_success(mocker, client):
    with client:
        # Make an initial request to create the request context
        client.get('/')

        mock_get = mocker.patch('requests.get')
        mock_get.side_effect = [
            mocker.Mock(json=mocker.Mock(return_value=mock_google_provider_cfg())),
            mocker.Mock(json=mocker.Mock(return_value={
                "sub": "1234567890",
                "email": "testuser@gmail.com",
                "email_verified": True,  # Simulate verified email
                "given_name": "Test",
                "picture": "https://example.com/pic.jpg"
            })),
        ]

        mocker.patch('requests.post', side_effect=mock_requests_post)


        response = client.get('/login/callback?code=fake-auth-code')

        # Assertions for successful login
        assert response.status_code == 302
        assert 'email' in session
        assert 'name' in session
        assert session['email'] == "testuser@gmail.com"
        assert session['name'] == "Test"


def test_google_login_does_not_create_multiple_accounts(mocker, app, client):
    with client:
        client.get('/')
        mock_get = mocker.patch('requests.get')

        mock_get.side_effect = [
            mocker.Mock(json=mocker.Mock(return_value=mock_google_provider_cfg())),
            mocker.Mock(json=mocker.Mock(return_value={
                "sub": "1234567890",
                "email": "testuser@gmail.com",
                "email_verified": True,  # Simulate verified email
                "given_name": "Test",
                "picture": "https://example.com/pic.jpg"
            })),

            # repeats the mocks for the 3rd and 4th call since we are calling the enpoint twice
            mocker.Mock(json=mocker.Mock(return_value=mock_google_provider_cfg())),
            mocker.Mock(json=mocker.Mock(return_value={
                "sub": "1234567890",
                "email": "testuser@gmail.com",
                "email_verified": True,  # Simulate verified email
                "given_name": "Test",
                "picture": "https://example.com/pic.jpg"
            })),
        ]

        mocker.patch('requests.post', side_effect=mock_requests_post)

        # attempt to login twice
        response = client.get('/login/callback?code=fake-auth-code')

        response2 = client.get('/login/callback?code=fake-auth-code')
        LOGGER.info(app.mongo)

        assert app.mongo.db.user.count_documents({}) == 1
