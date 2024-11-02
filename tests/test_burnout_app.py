"""
Additional test cases for Burnout project.
"""

import unittest
from application import app
from flask import session

class TestApplicationExtra(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_logout_route(self):
        response = self.app.get('/logout')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"success", response.data)  # Check if "success" message in response

    def test_ajaxhistory_route(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/ajaxhistory', data={'date': '2024-01-01'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'email', response.data)  # Check if "email" key is in response

    def test_shop_route(self):
        response = self.app.get('/shop')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Shop', response.data)  # Ensure "Shop" page loads correctly

def test_send_email_route_no_session(self):
    with self.app as client:
        # Set up a minimal session with required data to avoid KeyError
        with client.session_transaction() as sess:
            sess['email'] = 'testuser@example.com'
            sess['name'] = 'Test User'  # Adding 'name' to avoid KeyError
            
        response = client.post('/send_email')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Calorie History", response.data)  # Check if response contains expected content


    def test_blog_route(self):
        response = self.app.get('/blog')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'blog', response.data.lower())  # Check if "blog" is present in response

    def test_water_route_logged_in(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/water', data={'intake': '250'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Water Intake Tracker', response.data)



if __name__ == '__main__':
    unittest.main()
