def test_burnbot_hydration_reminder(self):
    user_message = {'message': 'Remind me to drink water every hour'}
    response = self.app.post('/burnbot', json=user_message)
    self.assertEqual(response.status_code, 200)
    data = response.get_json()
    self.assertIn('Hydration reminder set! I’ll remind you every hour to drink water.', data['response'])

def test_burnbot_weight_loss_goal(self):
    user_message = {'message': 'I want to lose 10 pounds'}
    response = self.app.post('/burnbot', json=user_message)
    self.assertEqual(response.status_code, 200)
    data = response.get_json()
    self.assertIn('Got it! We’ll work towards losing 10 pounds together. Let’s start with some goal-oriented exercises.', data['response'])

def test_burnbot_motivation(self):
    user_message = {'message': 'I need some motivation'}
    response = self.app.post('/burnbot', json=user_message)
    self.assertEqual(response.status_code, 200)
    data = response.get_json()
    self.assertIn('Keep pushing! You’re closer to your goal than you think!', data['response'])

def test_burnbot_daily_workout_plan(self):
    user_message = {'message': 'Give me a daily workout plan'}
    response = self.app.post('/burnbot', json=user_message)
    self.assertEqual(response.status_code, 200)
    data = response.get_json()
    self.assertIn('Here’s a balanced workout plan for today: 20 mins of cardio, 15 mins of strength, and 10 mins of stretching.', data['response'])

def test_burnbot_exercise_details(self):
    user_message = {'message': 'Tell me about push-ups'}
    response = self.app.post('/burnbot', json=user_message)
    self.assertEqual(response.status_code, 200)
    data = response.get_json()
    self.assertIn('Push-ups strengthen your chest, shoulders, and triceps.', data['response'])


def test_burnbot_calorie_advice(self):
    user_message = {'message': 'How many calories should I eat if I want to lose weight?'}
    response = self.app.post('/burnbot', json=user_message)
    self.assertEqual(response.status_code, 200)
    data = response.get_json()
    self.assertIn('For weight loss, aim to consume about 500 calories less than your maintenance level.', data['response'])

def test_burnbot_rest_day_advice(self):
    user_message = {'message': 'Should I take a rest day?'}
    response = self.app.post('/burnbot', json=user_message)
    self.assertEqual(response.status_code, 200)
    data = response.get_json()
    self.assertIn('Yes, rest days are essential for muscle recovery and preventing injury.', data['response'])

def test_burnbot_dietary_advice(self):
    user_message = {'message': 'Any dietary tips for building muscle?'}
    response = self.app.post('/burnbot', json=user_message)
    self.assertEqual(response.status_code, 200)
    data = response.get_json()
    self.assertIn('For muscle building, focus on protein-rich foods like chicken, eggs, and legumes.', data['response'])

def test_burnbot_emotional_support(self):
    user_message = {'message': 'I feel like giving up on my fitness goals'}
    response = self.app.post('/burnbot', json=user_message)
    self.assertEqual(response.status_code, 200)
    data = response.get_json()
    self.assertIn('Don’t give up! Remember why you started and take one step at a time. You’re stronger than you think!', data['response'])