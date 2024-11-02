
"""
Copyright (c) 2023 Rajat Chandak, Shubham Saboo, Vibhav Deo, Chinmay Nayak
This code is licensed under MIT license (see LICENSE for details)

@author: Burnout


This python file is used in and is part of the Burnout project.

For more information about the Burnout project, visit:
https://github.com/VibhavDeo/FitnessApp

"""
import unittest
import os,sys,inspect
# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
# sys.path.insert(0, parentdir)
from application import app, mongo, bcrypt
from flask import session
from unittest.mock import patch
from itsdangerous import URLSafeTimedSerializer

class TestApplication(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)  

    def test_login_route(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)  

    def test_register_route(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)  

    def test_calories_route(self):
        
        response = self.app.get('/calories')
        self.assertEqual(response.status_code, 302)  

    #New Unit test - 1
    def test_join_route(self):
        response = self.app.get('/join')  
        self.assertEqual(response.status_code, 404) 

    #New Unit test - 2
    def test_sleep_route(self):
        response = self.app.get('/sleep')  
        self.assertEqual(response.status_code, 404) 

    #New Unit test - 3
    def test_protected_route_without_login(self):
        # Access a protected route without logging in, expecting a redirect or unauthorized response
        response = self.app.get('/protected')
        self.assertNotEqual(response.status_code, 200)  # Should not allow access without login

    #New Unit test - 4
    def test_logout_route(self):
        # Test logout to ensure session is cleared
        response = self.app.get('/logout')
        self.assertEqual(response.status_code, 200)  # Assuming it redirects to the login page
        with self.app as client:
            client.get('/logout')
            self.assertNotIn('user_id', session)

    #New Unit test - 5
    def test_invalid_route(self):
        # Access a non-existent route
        response = self.app.get('/invalid-route')
        self.assertEqual(response.status_code, 404)

    #New Unit test - 6
    def test_logout_and_protected_route_access(self):
        # Test that after logout, a protected route cannot be accessed
        with self.app as client:
            client.post('/login', data=dict(username='testuser', password='testpass'))
            client.get('/logout')
            response = client.get('/protected')
            self.assertNotEqual(response.status_code, 200)  # Should not allow access after logout
            
    # def test_display_profile_route(self):
    #     
    #     with self.app as client:
    #         with client.session_transaction() as sess:
    #             sess['email'] = 'testuser@example.com'
    #         response = client.get('/display_profile')
    #         self.assertEqual(response.status_code, 200)  

    def test_user_profile_route(self):
        
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.get('/user_profile')
            self.assertEqual(response.status_code, 200)  

    def test_history_route(self):
        
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.get('/history')
    
            self.assertEqual(response.status_code, 200)  
    def test_bmi_calci_post(self):
        response = self.app.post('/bmi_calc', data={'weight': 70, 'height': 175})
        self.assertEqual(response.status_code, 200)

    def test_ajaxsendrequest_route(self):
    
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/ajaxsendrequest', data={'receiver': 'friend@example.com'})
            self.assertEqual(response.status_code, 200)  

    def test_ajaxcancelrequest_route(self):
        
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/ajaxcancelrequest', data={'receiver': 'friend@example.com'})
            self.assertEqual(response.status_code, 200)  

    def test_ajaxapproverequest_route(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/ajaxapproverequest', data={'receiver': 'friend@example.com'})
            self.assertEqual(response.status_code, 200) 
   
    def test_dashboard_route(self):
    
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.get('/dashboard')
            self.assertEqual(response.status_code, 200)  

    def test_add_favorite_route(self):
        
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/add_favorite', json={'exercise_id': '123', 'action': 'add'})
            self.assertEqual(response.status_code, 200)  

    def test_favorites_route(self):
        
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.get('/favorites')
            self.assertEqual(response.status_code, 200)  

    def test_exercise_routes(self):
        
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'

            exercise_routes = ['/yoga', '/swim', '/abbs', '/belly', '/core', '/gym', '/walk', '/dance', '/hrx']

            for route in exercise_routes:
                response = client.get(route)
                self.assertEqual(response.status_code, 200)  

    def test_submit_reviews_route(self):
    
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.get('/review')
            self.assertEqual(response.status_code, 200)  #

    #sas


    def test_login_without_verification(self):
        response = self.app.post('/login', data={
            'email': self.test_email,
            'password': self.test_password
        }, follow_redirects=True)
        self.assertIn(b'Please verify your email address before logging in.', response.data)
        self.assertEqual(response.status_code, 200)


    def test_successful_email_verification(self):
        user = mongo.db.user.find_one({'email': self.test_email})
        token = user['verification_token']
        response = self.app.get(f'/verify_email/{token}', follow_redirects=True)
        self.assertIn(b'Your account has been verified! You can now log in.', response.data)
        self.assertEqual(response.status_code, 200)

        # Verify that is_verified is now True
        updated_user = mongo.db.user.find_one({'email': self.test_email})
        self.assertTrue(updated_user['is_verified'])


    def test_login_after_verification(self):
        # First, verify the user's email
        self.test_successful_email_verification()

        # Attempt to log in
        response = self.app.post('/login', data={
            'email': self.test_email,
            'password': self.test_password
        }, follow_redirects=True)
        self.assertIn(b'You have been logged in!', response.data)
        self.assertEqual(response.status_code, 200)

    def test_email_verification_invalid_token(self):
        invalid_token = 'invalidtoken123'
        response = self.app.get(f'/verify_email/{invalid_token}', follow_redirects=True)
        self.assertIn(b'Invalid verification token.', response.data)
        self.assertEqual(response.status_code, 200)


    @patch('application.mail.send')
    def test_resend_verification_email(self, mock_mail_send):
        # Attempt to resend verification email
        response = self.app.post('/resend_verification', data={
            'email': self.test_email
        }, follow_redirects=True)
        self.assertIn(b'A new verification email has been sent.', response.data)
        self.assertEqual(response.status_code, 200)
        mock_mail_send.assert_called_once()


    def test_resend_verification_already_verified(self):
        # First, verify the user's email
        self.test_successful_email_verification()

        # Attempt to resend verification email
        response = self.app.post('/resend_verification', data={
            'email': self.test_email
        }, follow_redirects=True)
        self.assertIn(b'Account already verified. Please log in.', response.data)
        self.assertEqual(response.status_code, 200)


    def test_email_verification_nonexistent_user(self):
        # Generate a token for an email that doesn't exist
        fake_email = 'nonexistent@example.com'
        fake_token = self.serializer.dumps(fake_email, salt='email-confirm')
        response = self.app.get(f'/verify_email/{fake_token}', follow_redirects=True)
        self.assertIn(b'Account not found.', response.data)
        self.assertEqual(response.status_code, 200)


    def test_login_incorrect_password_after_verification(self):
        # First, verify the user's email
        self.test_successful_email_verification()

        # Attempt to log in with incorrect password
        response = self.app.post('/login', data={
            'email': self.test_email,
            'password': 'WrongPassword!'
        }, follow_redirects=True)
        self.assertIn(b'Login Unsuccessful. Please check username and password', response.data)
        self.assertEqual(response.status_code, 200)


    def test_access_protected_route_without_login(self):
        response = self.app.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Please log in to access this page.', response.data)  # Assuming such a flash message exists
        self.assertEqual(response.status_code, 200)


    def test_multiple_email_verification_attempts(self):
        # First verification attempt
        self.test_successful_email_verification()

        # Second verification attempt with the same token
        user = mongo.db.user.find_one({'email': self.test_email})
        token = user['verification_token']
        response = self.app.get(f'/verify_email/{token}', follow_redirects=True)
        self.assertIn(b'Account already verified. Please log in.', response.data)
        self.assertEqual(response.status_code, 200)

    
    def test_login_after_failed_verification_attempts(self):
        # Attempt to verify with invalid token multiple times
        for _ in range(3):
            response = self.app.get('/verify_email/invalidtoken', follow_redirects=True)
            self.assertIn(b'Invalid verification token.', response.data)
            self.assertEqual(response.status_code, 200)

        # Ensure the user is still not verified
        user = mongo.db.user.find_one({'email': self.test_email})
        self.assertFalse(user['is_verified'])

    
    def test_resend_verification_without_email(self):
        response = self.app.post('/resend_verification', data={}, follow_redirects=True)
        self.assertIn(b'Email address not found. Please register first.', response.data)
        self.assertEqual(response.status_code, 200)

    
    def test_email_verification_tampered_token(self):
        user = mongo.db.user.find_one({'email': self.test_email})
        token = user['verification_token']
        tampered_token = token + 'tampered'
        response = self.app.get(f'/verify_email/{tampered_token}', follow_redirects=True)
        self.assertIn(b'Invalid verification token.', response.data)
        self.assertEqual(response.status_code, 200)

    
    def test_register_with_existing_email(self):
        response = self.app.post('/register', data={
            'username': 'Another User',
            'email': self.test_email,
            'password': 'AnotherPassword123!'
        }, follow_redirects=True)
        self.assertIn(b'Email address already exists. Please log in or use a different email.', response.data)
        self.assertEqual(response.status_code, 200)

    
    def test_register_with_missing_fields(self):
        response = self.app.post('/register', data={
            'username': '',
            'email': '',
            'password': ''
        }, follow_redirects=True)
        self.assertIn(b'This field is required.', response.data)  # Assuming form validation messages
        self.assertEqual(response.status_code, 200)

    
    def test_register_with_weak_password(self):
        response = self.app.post('/register', data={
            'username': 'Weak Password User',
            'email': 'weakpassword@example.com',
            'password': '123'  # Assuming password strength validation
        }, follow_redirects=True)
        self.assertIn(b'Password does not meet strength requirements.', response.data)  # Adjust based on actual message
        self.assertEqual(response.status_code, 200)
if __name__ == '__main__':
    unittest.main()


