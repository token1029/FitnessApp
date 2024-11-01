
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
import json
from application import app
from flask import session
from unittest.mock import patch, MagicMock
from unittest import TestCase
import numpy as np

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
            self.assertEqual(response.status_code, 200)

    # @patch('application.mongo.db.profile.find_one')
    # def test_display_profile_route(self, mock_find_one):
    #     mock_find_one.return_value = {'target_weight': 70.0}

    #     with self.app as client:
    #         with client.session_transaction() as sess:
    #             sess['email'] = 'testuser@example.com'

    #         response = client.post('/display_profile')
    #         self.assertEqual(response.status_code, 200)

    def test_community_route(self):
    
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.get('/community')
            self.assertEqual(response.status_code, 200)


    def test_delete_friend_route(self):
    
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.get('/delete_friend')
            self.assertEqual(response.status_code, 302)


    def test_display_beginner_workout_recommendation(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.get('/beginner')
            self.assertEqual(response.status_code, 200)


    def test_post_beginner_workout_recommendation(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/beginner', data={'selectedPrimaryMuscle': 'Chest'})

            self.assertEqual(response.status_code, 302)
            self.assertIn('selectedPrimaryMuscle', response.headers['Set-Cookie'])
            self.assertIn('Chest', response.headers['Set-Cookie'])
            self.assertEqual(response.location, 'http://localhost/recommend')


    def test_display_advanced_workout_recommendation(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.get('/advanced')
            self.assertEqual(response.status_code, 200)


    def test_post_advanced_workout_recommendation(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/advanced', data={'selectedPrimaryMuscle': 'Chest'})

            self.assertEqual(response.status_code, 302)
            self.assertIn('selectedPrimaryMuscle', response.headers['Set-Cookie'])
            self.assertIn('Chest', response.headers['Set-Cookie'])
            self.assertEqual(response.location, 'http://localhost/recommend')


    def test_display_recommend_workout_route(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.get('/recommend_workout')
            self.assertEqual(response.status_code, 200)


    def test_beginner_routing_recommend_workout(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/recommend_workout', data={'selectedLevel': 'Beginner'})
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, 'http://localhost/beginner')


    def test_advanced_routing_recommend_workout_route(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/recommend_workout', data={'selectedLevel': 'Advanced'})
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, 'http://localhost/advanced')
            

    @patch('application.collection')  # Mock the MongoDB collection
    @patch('application.tfidf_vectorizer')  # Mock the TF-IDF vectorizer
    @patch('application.linear_kernel')  # Mock the linear_kernel function
    def test_recommend_exercises(self, mock_linear_kernel, mock_tfidf_vectorizer, mock_collection):
        # Mock the TF-IDF transformation and linear kernel computation
        mock_tfidf_vectorizer.transform.return_value = MagicMock()  # Mock the result of transform
        mock_linear_kernel.return_value = np.array([[0.1, 0.2, 0.3, 0.4, 0.5]])  # Mock cosine similarity scores

        # Mock the MongoDB find_one method to return sample exercise data
        mock_collection.find_one.side_effect = lambda query: {
            "id": query["id"],
            "instructions": "Do this exercise.,",
            "name": "Sample Exercise"
        }

        # Set up cookies and form data for the POST request
        with self.app as client:
            # Set a cookie for the primary muscle
            client.set_cookie('localhost', 'selectedPrimaryMuscle', 'chest')

            # Simulate form data
            form_data = {
                'level': '1',
                'equipment': 'dumbbell',
                'force': 'push',
                'mechanic': 'isolation',
                'category': 'strength',
                'secondaryMuscles[]': ['triceps', 'shoulders']
            }

            # Perform the POST request
            response = client.post('/recommend', data=form_data)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Sample Exercise', response.data)

    
    @patch('application.collection.find_one')  # Mock the MongoDB collection find_one method
    @patch('application.tfidf_vectorizer.transform')  # Mock TF-IDF vectorizer transform
    @patch('application.cosine_similarity')  # Mock cosine similarity function
    def test_more_recommendations_post(self, mock_cosine_similarity, mock_tfidf_transform, mock_find_one):
        mock_tfidf_transform.return_value = "mock_tfidf_matrix"  # Mock output of the TF-IDF transformation
        mock_cosine_similarity.return_value = np.array([[0.9, 0.8, 0.7, 0.6, 0.5]])  # Mock similarity scores
        mock_find_one.side_effect = [
            {"id": "1", "instructions": "Instruction 1."},
            {"id": "2", "instructions": "Instruction 2."},
            {"id": "3", "instructions": "Instruction 3."},
            {"id": "4", "instructions": "Instruction 4."},
            {"id": "5", "instructions": "Instruction 5."}
        ]

        with self.app as client:
            with client.session_transaction() as sess:
                sess['selectedPrimaryMuscle'] = 'Chest'
            
            # Simulate a POST request with user input
            user_input = {
                'level': ['Beginner'],
                'equipment': ['Dumbbell'],
                'force': ['Push'],
                'mechanic': ['Compound'],
                'category': ['Strength']
            }
            response = client.post('/more_recommendations',
                                    data={
                                        'user_input': json.dumps(user_input),
                                        'secondaryMuscles[]': ['Triceps', 'Shoulders']
                                    })

            self.assertEqual(response.status_code, 200)


    def test_more_recommendations_get(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.get('/more_recommendations')
            self.assertEqual(response.status_code, 200)

    def test_progress_monitor(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.get('/progress_monitor')
            self.assertEqual(response.status_code, 200)
    
    def test_progress_monitor_post_valid_data(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            
            form_data = {
                'current_weight': '70',
                'goal_weight': '65',
                'waist': '30',
                'hips': '35',
                'chest': '40',
                'notes': 'Good progress!'
            }

            response = client.post('/progress_monitor', data=form_data, follow_redirects=True)

            self.assertEqual(response.status_code, 200)

    def test_progress_monitor_post_missing_fields(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            
            form_data = {
                'current_weight': '',  
                'goal_weight': '65',
                'waist': '30',
                'hips': '75',
                'chest': '75',
                'notes': 'Waist measurements not within range'
            }

            response = client.post('/progress_monitor', data=form_data, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Waist must be between 50 and 150 ', response.data)  


    def test_progress_history(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.get('/progress_history')
            self.assertEqual(response.status_code, 200)

    def test_progress_history_get_no_session(self):
        with self.app as client:
            response = client.get('/progress_history', follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Log In', response.data)  
    
    def test_progress_history_post_request(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            
            response = client.post('/progress_history', follow_redirects=True)

            self.assertEqual(response.status_code, 405)  

    
    def test_wellness_log(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.get('/wellness_log')
            self.assertEqual(response.status_code, 200)

    def test_update_streak(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.get('/update_streak')
            self.assertEqual(response.status_code, 200)
    
    def test_update_streak_no_session(self):
        with self.app as client:
            response = client.get('/update_streak', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Log In', response.data)  

    @patch('application.collection')  # Mock the MongoDB collection
    def test_update_streak_get_with_session(self, mock_db):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            
            mock_db.db.streaks.insert_one({
                'email': 'testuser@example.com',
                'date': '2020-01-01',
                'streak': 3
            })

            response = client.get('/update_streak')
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
