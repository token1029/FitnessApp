import pytest
from bs4 import BeautifulSoup

# Test for rendering the friends page when user is logged in with friends


def test_render_friends_page(client):
    # Simulate a logged-in user
    with client.session_transaction() as sess:
        sess['email'] = 'test@example.com'

    client.application.mongo.db.user.insert_one({'name': 'John Doe', 'email': 'friend1@example.com'})
    client.application.mongo.db.friends.insert_one({'sender': 'test@example.com', 'receiver': 'friend1@example.com', 'accept': True})

    response = client.get('/friends')

    assert response.status_code == 200

    soup = BeautifulSoup(response.data, 'html.parser')

    assert 'My Friends' in soup.text
    assert 'friend1@example.com' in soup.text


# Test for pending friend requests
def test_pending_requests(client):
    with client.session_transaction() as sess:
        sess['email'] = 'test@example.com'

    client.application.mongo.db.friends.insert_one({'sender': 'friend2@example.com', 'receiver': 'test@example.com', 'accept': False})

    response = client.get('/friends')
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, 'html.parser')
    assert 'Sent Requests' in soup.text
    assert 'friend2@example.com' in soup.text


# Test for rendering the friends page when the user is not logged in
def test_friends_page_not_logged_in(client):
    response = client.get('/friends')
    assert response.status_code == 302
