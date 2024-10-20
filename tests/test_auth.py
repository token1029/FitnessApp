import flask  # Assuming your Flask app is defined in app.py
from flask import session
from unittest.mock import patch, MagicMock
import pytest
from .conftest import client
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def test_redirect_to_google_page(client):
    response = client.get('/google-login')
    assert response.status_code == 302


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
    # Custom logic can be added here if needed
    # For demonstration, we are just returning mock values
    return (
        token_endpoint,  # Return the original token endpoint
        {"Content-Type": "application/x-www-form-urlencoded"},  # Headers
        f"code=4223"  # Body of the request
    )


def test_google_login_callback_unverified_email(mocker, client):
    # Mock the first call to requests.get (for the Google provider config)
    mock_get = mocker.patch('requests.get')

    mock_get.side_effect = [
        # First call returns the Google provider config
        MagicMock(json=MagicMock(return_value=mock_google_provider_cfg())),
        # Second call returns the user info with email verified
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


@patch('requests.post')
@patch('requests.get')
@patch('app.current_app.mongo.db.user.find_one')
@patch('app.current_app.mongo.db.user.insert')
def test_google_login_callback_success(mock_insert, mock_find_one, mock_get, mock_post, client):
    # Mock token response from Google
    mock_post.return_value.json = MagicMock(return_value=mock_token_response())
    # Mock userinfo response from Google
    mock_get.return_value.json = MagicMock(return_value=mock_userinfo_response())

    # Simulate user not existing in the database (so the user gets inserted)
    mock_find_one.return_value = None

    # Simulate request to the /login/callback route with a mock 'code' in the query string
    response = client.get('/login/callback?code=fake-auth-code')

    # Assertions for successful login
    assert response.status_code == 302  # Redirect to dashboard
    assert 'email' in session
    assert 'name' in session
    assert session['email'] == "testuser@gmail.com"
    assert session['name'] == "Test"
    mock_insert.assert_called_once_with({
        'name': 'Test',
        'email': 'testuser@gmail.com',
        'pwd': ''
    })
