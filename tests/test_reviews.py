import pytest
from bs4 import BeautifulSoup
from fitnessapp.forms import ReviewForm

# Test for rendering the review page


def test_render_review_page(client):
    with client.session_transaction() as sess:
        sess['email'] = 'test@example.com'

    response = client.get('/review')
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    assert soup.find('form') is not None
    assert 'Submit a Review' in soup.text

# Test for submitting a valid review


def test_submit_valid_review(client):
    with client.session_transaction() as sess:
        sess['email'] = 'test@example.com'

    response = client.post('/review', data={
        'name': 'Test User',
        'review': 'This is a test review.'
    })

    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    assert 'This is a test review.' in soup.text
    assert 'Test User' in soup.text

# Test for handling reviews when user is not logged in


def test_user_not_logged_in(client):
    response = client.get('/review')

    assert response.status_code == 200
    assert 'User not logged in' in response.data.decode()

# Test for submitting a review when the user is not logged in


def test_submit_review_not_logged_in(client):
    response = client.post('/review', data={
        'name': 'Test User',
        'review': 'This is a test review.'
    })

    assert response.status_code == 200
    assert 'User not logged in' in response.data.decode()


# Test for retrieving existing reviews
def test_existing_reviews_displayed(client):
    # Simulate a logged-in user
    with client.session_transaction() as sess:
        sess['email'] = 'test@example.com'

    client.application.mongo.db.reviews.insert_one({'name': 'Existing User', 'review': 'This is an existing review.'})

    response = client.get('/review')

    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')

    assert 'This is an existing review.' in soup.text
    assert 'Existing User' in soup.text
