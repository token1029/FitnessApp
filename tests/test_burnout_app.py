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
        response = self.app.post('/send_email')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"User not logged in", response.data)  # Expected output when no session

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

    def test_clear_intake_route(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/clear-intake')
            self.assertEqual(response.status_code, 302)
            self.assertIn('/water', response.headers['Location'])  # Ensure redirect to /water

    def test_ajaxhistory_invalid_date(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/ajaxhistory', data={'date': 'invalid-date'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'date', response.data)  # Check that date key is returned

    def test_dashboard_route_no_login(self):
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirected to login if not logged in

    def test_register_existing_user(self):
        response = self.app.post('/register', data={
            'username': 'existinguser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account created', response.data)

    def test_update_user_profile(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/user_profile', data={
                'weight': '70',
                'height': '175',
                'goal': 'Fitness',
                'target_weight': '65'
            })
            self.assertEqual(response.status_code, 302)
            self.assertIn('/display_profile', response.headers['Location'])  # Redirect to profile display

    def test_exercise_of_the_day_route(self):
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Exercise of the Day', response.data)  # Check for Exercise of the Day text

    def test_nonexistent_route(self):
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)  # Expecting a 404 response

    def test_yoga_route_logged_out(self):
        response = self.app.get('/yoga')
        self.assertEqual(response.status_code, 302)  # Redirects if not logged in

    def test_invalid_favorite_action(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/add_favorite', json={'exercise_id': '123', 'action': 'invalid_action'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'error', response.data)  # Error message should be returned

if __name__ == '__main__':
    unittest.main()
