
"""
Copyright (c) 2023 Rajat Chandak, Shubham Saboo, Vibhav Deo, Chinmay Nayak
This code is licensed under MIT license (see LICENSE for details)

@author: Burnout


This python file is used in and is part of the Burnout project.

For more information about the Burnout project, visit:
https://github.com/VibhavDeo/FitnessApp

"""
import json, os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from bson import ObjectId
import bcrypt
import smtplib
from flask import json,jsonify,Flask
from flask import render_template, session, url_for, flash, redirect, request, Flask
from flask_mail import Mail, Message
from flask_pymongo import PyMongo
from tabulate import tabulate
from forms import HistoryForm, RegistrationForm, LoginForm, CalorieForm, UserProfileForm, EnrollForm,ReviewForm, ProgressForm, StreakForm
from insert_db_data import insertfooddata,insertexercisedata
from insert_excercises import coaching_videos
import schedule
from threading import Thread
import time
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

app = Flask(__name__, template_folder='templates', static_url_path='/static')
app.secret_key = 'secret'
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/test'
app.config['MONGO_CONNECT'] = False
mongo = PyMongo(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "burnoutapp2023@gmail.com"
app.config['MAIL_PASSWORD'] = "jgny mtda gguq shnw"
mail = Mail(app)

insertfooddata()
insertexercisedata()
coaching_videos()

# data directory
data_dir = os.path.join(os.path.dirname(__file__), 'data')

# Open json file
json_file_path = os.path.join(data_dir, 'exercises.json')
with open(json_file_path, 'r', encoding='utf-8') as file:
    exercises = json.load(file)

# Remove folder names in image filenames
for exercise in exercises:
    images = exercise["images"]
    exercise["images"] = [image.split('/')[-1] for image in images]

# Convert the modified exercise data to a pandas DataFrame
dataframe = pd.DataFrame(exercises)

# Save the DataFrame to a CSV file
csv_file_path = os.path.join(data_dir, 'exercises.csv')
dataframe.to_csv(csv_file_path, index=False, sep=',')
csv_cleaned_file_path = os.path.join(data_dir, 'exercises_cleaned.csv')

# Load the cleaned data from the CSV file
df = pd.read_csv(csv_cleaned_file_path)

# Convert the 'images' field from a string to a list and strip single quotes
df['images'] = df['images'].apply(lambda x: [image.strip(" '") for image in x.strip("[]").split(", ")])

# Connect to MongoDB
collection = mongo.db.exercises

# Insert the CSV data into MongoDB
df_dict = df.to_dict(orient='records')
collection.insert_many(df_dict)

# Define the priority for user input fields
priority_fields = ['primaryMuscles','level', 'equipment', 'secondaryMuscles', 'force', 'mechanic', 'category']

# Define priority weights
priority_weights = [20, 15, 10, 5, 3, 2, 1]

# Concatenate the relevant columns to create content for recommendations
df['content'] = df[priority_fields].apply(
    lambda row: (
        ' '.join([str(val) * weight for val, weight in zip(row, priority_weights)])
    ),
    axis=1
)

# Create a TF-IDF vectorizer to convert the content into numerical form
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(df['content'])


def reminder_email():
    """
    reminder_email() will send a reminder to users for doing their workout.
    """
    with app.app_context():
        try:
            time.sleep(10)
            print('in send mail')
            recipientlst = list(mongo.db.user.distinct('email'))
            print(recipientlst)
            
            server = smtplib.SMTP_SSL("smtp.gmail.com",465)
            sender_email = "burnoutapp2023@gmail.com"
            sender_password = "jgny mtda gguq shnw"

            server.login(sender_email,sender_password)
            message = 'Subject: Daily Reminder to Exercise'
            for e in recipientlst:
                print(e)
                server.sendmail(sender_email,e,message)                
            server.quit()        
        except KeyboardInterrupt:
            print("Thread interrupted")

schedule.every().day.at("08:00").do(reminder_email)

# Run the scheduler
def schedule_process():
    while True:
        schedule.run_pending()
        time.sleep(10)

Thread(target=schedule_process).start()
  

@app.route("/", methods=["GET", "POST"])
@app.route("/home")
def home():
    """
    home() function displays the homepage of our website.
    route "/home" will redirect to home() function.
    input: The function takes session as the input
    Output: Out function will redirect to the login page
    """
    if session.get('email'):
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if not session.get('email'):
        form = LoginForm()
        if form.validate_on_submit():
            # Find user by email
            user = mongo.db.user.find_one({'email': form.email.data}, {'email', 'pwd', 'name', 'user_type'})
            if user and bcrypt.checkpw(form.password.data.encode("utf-8"), user['pwd']):
                flash('You have been logged in!', 'success')
                session['email'] = user['email']
                session['name'] = user['name']

                # Now fetch the user type
                user_type = user.get('user_type')  # Get user type from the fetched user data

                # Redirect based on user type
                if user_type == 'coach':
                    return redirect(url_for('coach_dashboard'))
                else:
                    return redirect(url_for('dashboard'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
    else:
        return redirect(url_for('home'))

    return render_template('login.html', title='Login', form=form)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    """
    logout() function just clears out the session and returns success
    route "/logout" will redirect to logout() function.
    Output: session clear
    """
    session.clear()
    return "success"


@app.route("/register", methods=['GET', 'POST'])
def register():
    now = datetime.now().strftime('%Y-%m-%d')

    if not session.get('email'):
        form = RegistrationForm()
        
        # Fetch all coaches and create a list for the dropdown display
        try:
            coaches = mongo.db.profile.find({"user_type": "coach"})
            coach_list = [{"name": coach.get("name"), "specialization": coach.get("specialization")} for coach in coaches]
            print("Fetched coaches:", coach_list)  # Debugging line
        except Exception as e:
            print(f"Error fetching coaches: {e}")
            coach_list = []
        
        # Create choices for the form field that only stores the coach's name
        coach_choices = [(coach["name"], f"{coach['name']} - {coach['specialization']}") for coach in coach_list]
        form.coach.choices = coach_choices

        if form.validate_on_submit() and request.method == 'POST':
            # Common fields for both coach and student
            username = form.username.data
            email = form.email.data
            password = form.password.data
            user_type = form.user_type.data

            # Prepare user_data for insertion
            user_data = {
                'name': username,
                'email': email,
                'pwd': bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()),
                'user_type': user_type,
                'date': now
            }
            mongo.db.user.insert_one(user_data)
            
            # Profile data
            profile_data = {
                'name': username,
                'user_type': user_type,
                'email': email,
                'weight': form.weight.data if user_type == 'student' else None,
                'height': form.height.data if user_type == 'student' else None,
                'goal': form.goal.data if user_type == 'student' else None,
                'target_weight': form.target_weight.data if user_type == 'student' else None,
                'coach': form.coach.data if user_type == 'student' else None,  # Store only the coach name
                'specialization': form.specialization.data if user_type == 'coach' else None,
                'experience': form.experience.data if user_type == 'coach' else None,
                'date': now
            }
            mongo.db.profile.insert_one(profile_data)
            
            flash(f'Account created for {username}!', 'success')
            return redirect(url_for('home'))

    else:
        return redirect(url_for('home'))

    # Pass coach_list to the template
    return render_template('register.html', title='Register', form=form, coach_list=coach_list)

@app.route('/recommend_workout', methods=['GET', 'POST'])
def recommend_workout():
    if request.method == 'POST':
        # Handle form submission for level
        selected_level = request.form.get('selectedLevel')
        if selected_level == 'Beginner':
            return redirect(url_for('beginner'))
        else:
            return redirect(url_for('advanced'))
        
    return render_template('recommend_workout.html')


@app.route('/beginner', methods=['GET', 'POST'])
def beginner():
    primary_muscles = ["Chest", "Biceps", "Abdominals", "Quadriceps", "Middle Back", "Glutes", "Hamstrings", "Calves "]
    selected_primary_muscle = request.cookies.get('selectedPrimaryMuscle')
    if request.method == 'POST':
        # Handle form submission and update the selected primary muscle
        selected_primary_muscle = request.form.get('selectedPrimaryMuscle')

        # Store the selected primary muscle in the cookie or local storage
        response = redirect(url_for('recommend_exercises'))
        response.set_cookie('selectedPrimaryMuscle', selected_primary_muscle)
        return response
    return render_template('beginner.html', primary_muscles=primary_muscles, selectedPrimaryMuscle=selected_primary_muscle)


@app.route('/advanced', methods=['GET', 'POST'])
def advanced():
    primary_muscles = ["Neck", "Shoulders", "Chest", "Biceps", "Forearms", "Abdominals", "Quadriceps", "Adductors", "Calves",
                       "Traps", "Triceps", "Lats", "Middle Back", "Lower Back", "Abductors", "Glutes", "Hamstrings", "Calves "]
    selected_primary_muscle = request.cookies.get('selectedPrimaryMuscle')
    if request.method == 'POST':
        # Handle form submission and update the selected primary muscle
        selected_primary_muscle = request.form.get('selectedPrimaryMuscle')

        # Store the selected primary muscle in the cookie or local storage
        response = redirect(url_for('recommend_exercises'))
        response.set_cookie('selectedPrimaryMuscle', selected_primary_muscle)
        return response
    return render_template('advanced.html', primary_muscles=primary_muscles, selectedPrimaryMuscle=selected_primary_muscle)


@app.route('/recommend', methods=['GET', 'POST'])
def recommend_exercises():
    exercise_data = []
    user_input = {}
    selected_primary_muscle= ""
    if request.method == 'POST':
        user_input = {field: request.form.get(field) for field in priority_fields}

        # Retrieve the selected primary muscle from the cookie
        selected_primary_muscle = request.cookies.get('selectedPrimaryMuscle', "")
        for field in priority_fields:
            if user_input[field] is None:
                user_input[field] = ""  # Set to an empty string or a default value

        # Extract and process the secondary muscles
        secondary_muscles = request.form.getlist('secondaryMuscles[]')
        secondary_muscles_str = ' '.join(secondary_muscles)
        user_content = (
            selected_primary_muscle * 20 + ' ' +
            ''.join(map(str, user_input['level'])) * priority_weights[0] + ' ' +
            ''.join(map(str, user_input['equipment'])) * priority_weights[1] + ' ' +
            secondary_muscles_str * priority_weights[2] + ' ' +
            ''.join(map(str, user_input['force'])) * priority_weights[3] + ' ' +
            ''.join(map(str, user_input['mechanic'])) * priority_weights[4] + ' ' +
            ''.join(map(str, user_input['category'])) * priority_weights[5]
        )

        # Convert user content into TF-IDF vector for recommendation
        user_tfidf_matrix = tfidf_vectorizer.transform([user_content])
        user_cosine_sim = linear_kernel(user_tfidf_matrix, tfidf_matrix)
        sim_scores = user_cosine_sim[0]
        exercise_indices = sim_scores.argsort()[::-1][:5]  # Select top 5 recommendations

        # Convert exercise_indices to a list of exercise IDs
        exercise_ids = [str(df.iloc[index]["id"]) for index in exercise_indices]
        for exercise_id in exercise_ids:
            exercise_doc = collection.find_one({"id": exercise_id})
            if exercise_doc:
                if 'instructions' in exercise_doc:
                    # Replace "\n" with "<br>" to add line breaks in the instructions
                    exercise_doc['instructions'] = exercise_doc['instructions'].replace('.,', '<br>')
                exercise_data.append(exercise_doc)

        # Render the recommendations template with the results
        return render_template('recommendations.html', recommendations=exercise_data, user_input=user_input, selectedPrimaryMuscle=selected_primary_muscle)
    
    # Handle the case where there's no POST data (initial page load or form submission)
    return render_template('recommendations.html', recommendations=exercise_data, user_input=user_input, selectedPrimaryMuscle=selected_primary_muscle)


@app.route('/more_recommendations', methods=['GET', 'POST'])
def more_recommendations():
    exercise_data = []
    user_input = {}
    selected_primary_muscle = ""
    if request.method == 'POST':
        selected_primary_muscle = request.cookies.get('selectedPrimaryMuscle', "")
        # Retrieve user input data from the hidden input field
        user_input = json.loads(request.form.get('user_input', '{}'))

        # Extract and process the secondary muscles
        secondary_muscles = request.form.getlist('secondaryMuscles[]')
        secondary_muscles_str = ' '.join(secondary_muscles)
        user_content = (
            selected_primary_muscle * 20 + ' ' +
            ''.join(map(str, user_input.get('level', ''))) * priority_weights[0] + ' ' +
            ''.join(map(str, user_input.get('equipment', ''))) * priority_weights[1] + ' ' +
            secondary_muscles_str * priority_weights[2] + ' ' +
            ''.join(map(str, user_input.get('force', ''))) * priority_weights[3] + ' ' +
            ''.join(map(str, user_input.get('mechanic', ''))) * priority_weights[4] + ' ' +
            ''.join(map(str, user_input.get('category', ''))) * priority_weights[5]
        )

        # Convert user content into TF-IDF vector for recommendation
        user_tfidf_matrix = tfidf_vectorizer.transform([user_content])
        user_cosine_sim = cosine_similarity(user_tfidf_matrix, tfidf_matrix)

        # Calculate the similarity between the user's preferences and exercises (item-based collaborative filtering)
        item_sim_scores = cosine_similarity(user_cosine_sim, tfidf_matrix.T)[0]
        
        # Get the indices of exercises based on item similarity
        exercise_indices = item_sim_scores.argsort()[-5:][::-1]

        # Convert exercise_indices to a list of exercise IDs
        exercise_ids = [str(df.iloc[index]["id"]) for index in exercise_indices]
        for exercise_id in exercise_ids:
            exercise_doc = collection.find_one({"id": exercise_id})
            if exercise_doc:
                if 'instructions' in exercise_doc:
                    # Replace "\n" with "<br>" to add line breaks in the instructions
                    exercise_doc['instructions'] = exercise_doc['instructions'].replace('.,', '<br>')
                exercise_data.append(exercise_doc)

        # Render the more_recommendations template with the results
        return render_template('more_recommendations.html', recommendations=exercise_data, user_input=user_input,
                               selectedPrimaryMuscle=selected_primary_muscle)
    
    # Handle the case where there's no POST data (initial page load or form submission)
    return render_template('more_recommendations.html', recommendations=exercise_data, user_input=user_input,
                           selectedPrimaryMuscle=selected_primary_muscle)


@app.route("/calories", methods=['GET', 'POST'])
def calories():
    """
    calorie() function displays the Calorieform (calories.html) template
    route "/calories" will redirect to calories() function.
    CalorieForm() called and if the form is submitted then various values are fetched and updated into the database entries
    Input: Email, date, food, burnout
    Output: Value update in database and redirected to home page
    """
    now = datetime.now()
    now = now.strftime('%Y-%m-%d')

    get_session = session.get('email')
    if get_session is not None:
        form = CalorieForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                email = session.get('email')
                food = request.form.get('food')
                cals = food.split(" ")
                cals = int(cals[-1][1:-1])
                burn = request.form.get('burnout')

                temp = mongo.db.calories.find_one({'email': email}, {'email', 'calories', 'burnout', 'date'})
                if temp is not None and temp['date']==str(now):
                    mongo.db.calories.update_many({'email': email}, {'$set': {'calories': temp['calories'] + cals, 'burnout': temp['burnout'] + int(burn)}})
                else:
                    mongo.db.calories.insert({'date': now, 'email': email, 'calories': cals, 'burnout': int(burn)})
                flash(f'Successfully updated the data', 'success')
                return redirect(url_for('calories'))
    else:
        return redirect(url_for('home'))
    return render_template('calories.html', form=form, time=now)

@app.route("/progress_monitor", methods=['GET', 'POST'])
def progress_monitor():
    """
    Handles user progress tracking and data entry on the progress monitor page.

    This function renders a form for users to enter their daily progress data. If the user 
    submits the form data, it checks for an existing entry for the current date. If an entry 
    already exists, it updates it; otherwise, it inserts a new record.

    Returns:
        If the user is logged in and submits valid form data:
            - Updates or inserts user progress data in the MongoDB 'progress' collection.
            - Redirects back to the progress monitor page with a success message.
        If the user is not logged in:
            - Redirects the user to the home page.

    Context Variables:
        form: Instance of ProgressForm, used to capture the user's input for progress data.
        date: String, today's date in 'YYYY-MM-DD' format.
    """
    now = datetime.now().strftime('%Y-%m-%d')
    email = session.get('email')

    if email is not None:
        form = ProgressForm()
        if form.validate_on_submit():
            if request.method == 'POST':

                # Retrieve form data
                weight = float(form.current_weight.data)
                goal_weight = float(form.goal_weight.data)
                measurements = {
                    'waist': float(form.waist.data),
                    'hips': float(form.hips.data),
                    'chest': float(form.chest.data),
                }
                notes = form.notes.data

                existing_entry = mongo.db.progress.find_one({'email': email, 'date': now})
                if existing_entry:
                    # Update existing entry
                    mongo.db.progress.update_one(
                        {'email': email, 'date': now},
                        {'$set': {
                            'weight': weight,
                            'goal_weight': goal_weight,
                            'measurements': measurements,
                            'notes': notes
                        }}
                    )
                else:
                    # Insert new entry
                    mongo.db.progress.insert_one({
                        'date': now,
                        'email': email,
                        'weight': weight,
                        'goal_weight': goal_weight,
                        'measurements': measurements,
                        'notes': notes
                    })

                flash('Progress successfully saved', 'success')
                print("success")
                return redirect(url_for('progress_monitor'))
    else:
        return redirect(url_for('home'))

    return render_template('progress.html', form=form, date=now)

@app.route("/progress_history", methods=['GET'])
def progress_history():
    """
    Displays the user's progress history page.

    This function retrieves all progress entries for the logged-in user from the 
    MongoDB 'progress' collection, sorted in descending order by date. The retrieved 
    entries include data on daily weight, goal weight, measurements, and notes. If 
    the user is not logged in, they are redirected to the home page.

    Returns:
        If the user is logged in:
            - Renders 'progress_history.html' with progress data for the user.
        If the user is not logged in:
            - Redirects the user to the home page.

    Context Variables:
        progress_data: List of dictionaries, each representing a progress entry 
                       for the user, sorted from the most recent to oldest entry.
    """
    email = session.get('email')
    
    if email is not None:
        progress_entries = mongo.db.progress.find({'email': email}).sort("date", -1)
        
        progress_data = list(progress_entries)
        
        return render_template('progress_history.html', progress_data=progress_data)
    else:
        return redirect(url_for('home'))
    
@app.route("/wellness_log", methods=['GET', 'POST'])
def wellness_log():
    """
    Renders the wellness log page.
    Returns:
        Renders 'wellness_log.html', the template for the wellness log page.
    """
    return render_template('wellness_log.html')

@app.route("/update_streak", methods=['GET', 'POST'])
def update_streak():
    """
    Updates the user's workout streak based on their activity.

    Allows users to either increment or reset their workout streak. If the last recorded 
    workout was yesterday, the streak is incremented; otherwise, it resets to 1. If "reset" 
    is selected, the streak is set to zero. The streak data is saved in the 'streaks' 
    collection in MongoDB.

    Returns:
        Redirects to the home page if the user is not logged in.
        On POST, updates the streak data and redirects to the streak page.
        On GET, renders 'workout_streak.html' with the current streak.

    Context Variables:
        form: StreakForm for capturing user input.
        current_streak: Integer, the current streak value.
    """
    email = session.get('email')
    if email is None:
        return redirect(url_for('home'))
    today = datetime.now().strftime('%Y-%m-%d')
    form = StreakForm()
    last_entry = mongo.db.streaks.find_one({'email': email}, sort=[('date', -1)])
    current_streak = last_entry.get('streak', 0) if last_entry else 0
    last_date = datetime.strptime(last_entry['date'], '%Y-%m-%d') if last_entry else None
    if form.validate_on_submit() and request.method == 'POST':
        action = request.form.get('action') 
        if action == "update":
            if last_entry and (datetime.now() - last_date).days == 1:
                current_streak += 1  
            else:
                current_streak = 1 
        elif action == "reset":
            current_streak = 0
            print("inside reset")
        mongo.db.streaks.update_one(
            {'email': email, 'date': today},
            {
                '$set': {
                    'streak': current_streak,
                    'date': today
                }
            },
            upsert=True  # Create a new entry if it doesn't exist
        )
        flash(f'Your workout streak is now {current_streak} days!', 'success')
        return redirect(url_for('update_streak'))
    last_entry = mongo.db.streaks.find_one({'email': email}, sort=[('date', -1)])
    current_streak = last_entry.get('streak', 0) if last_entry else 0
    print(current_streak)
    return render_template('workout_streak.html', form=form, current_streak=current_streak)

@app.route("/workout_streak", methods=['GET', 'POST'])
def workout_streak():
    return render_template('workout_streak.html')

@app.route("/display_profile", methods=['GET', 'POST'])
def display_profile():
    """
    Display user profile and graph
    """
    now = datetime.now()
    now = now.strftime('%Y-%m-%d')

    if session.get('email'):
        email = session.get('email')
        user_data = mongo.db.profile.find_one({'email': email})
        target_weight=float(user_data['target_weight'])
        user_data_hist = list(mongo.db.profile.find({'email': email}))

        for entry in user_data_hist:
            entry['date'] = datetime.strptime(entry['date'], '%Y-%m-%d').date()

        sorted_user_data_hist = sorted(user_data_hist, key=lambda x: x['date'])
        # Extracting data for the graph
        dates = [entry['date'] for entry in sorted_user_data_hist]
        weights = [float(entry['weight']) for entry in sorted_user_data_hist]

        # Plotting Graph 
        fig = px.line(x=dates, y=weights, labels={'x': 'Date', 'y': 'Weight'}, title='Progress',markers=True,line_shape='spline')
        fig.add_trace(go.Scatter(x=dates, y=[target_weight] * len(dates),mode='lines', line=dict(color='green', width=1, dash='dot'), name='Target Weight'))
        fig.update_yaxes(range=[min(min(weights),target_weight) - 5, max(max(weights),target_weight) + 5])
        fig.update_xaxes(range=[min(dates),now]) 
        # Converting to JSON
        graph_html = fig.to_html(full_html=False)

        last_10_entries = sorted_user_data_hist[-10:]

        return render_template('display_profile.html', status=True, user_data=user_data, graph_html=graph_html, last_10_entries=last_10_entries)
    else:
        return redirect(url_for('login'))
    #return render_template('user_profile.html', status=True, form=form)#


@app.route("/user_profile", methods=['GET', 'POST'])
def user_profile():
    """
    user_profile() function displays the UserProfileForm (user_profile.html) template
    route "/user_profile" will redirect to user_profile() function.
    user_profile() called and if the form is submitted then various values are fetched and updated into the database entries
    Input: Email, height, weight, goal, Target weight
    Output: Value update in database and redirected to home login page.
    """
    now = datetime.now()
    now = now.strftime('%Y-%m-%d')

    if session.get('email'):
        form = UserProfileForm()
        if form.validate_on_submit():
            print('validated')
            if request.method == 'POST':
                print('post')
                email = session.get('email')
                weight = request.form.get('weight')
                height = request.form.get('height')
                goal = request.form.get('goal')
                target_weight = request.form.get('target_weight')
                temp = mongo.db.profile.find_one({'email': email, 'date': now}, {'height', 'weight', 'goal', 'target_weight'})
                if temp is not None:
                    mongo.db.profile.update_one({'email': email, 'date': now},
                                            {'$set': {
                                                'weight': weight,
                                                'height': height,
                                                'goal': goal,
                                                'target_weight':target_weight}})
                else:
                    mongo.db.profile.insert({'email': email,
                                             'date': now,
                                             'height': height,
                                             'weight': weight,
                                             'goal': goal,
                                             'target_weight': target_weight})
                
                flash(f'User Profile Updated', 'success')

                return redirect(url_for('display_profile'))
    else:
        return redirect(url_for('login'))
    return render_template('user_profile.html', status=True, form=form)


@app.route("/history", methods=['GET'])
def history():
    # ############################
    # history() function displays the Historyform (history.html) template
    # route "/history" will redirect to history() function.
    # HistoryForm() called and if the form is submitted then various values are fetched and update into the database entries
    # Input: Email, date
    # Output: Value fetched and displayed
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = HistoryForm()
    return render_template('history.html', form=form)

@app.route('/water', methods=['GET','POST'])
def water():
    email = session.get('email')
    intake = request.form.get('intake')
    if request.method == 'POST':

        current_time = datetime.now()
        # Insert the new record
        mongo.db.intake_collection.insert_one({'intake': intake, 'time': current_time, 'email': email})

    # Retrieving records for the logged-in user
    records = mongo.db.intake_collection.find({"email": email}).sort("time", -1)

    # IMPORTANT: We need to convert the cursor to a list to iterate over it multiple times
    records_list = list(records)
    if records_list:
        average_intake = sum(int(record['intake']) for record in records_list) / len(records_list)
    else:
        average_intake = 0
    # Calculate total intake
    total_intake = sum(int(record['intake']) for record in records_list)

    # Render template with records and total intake
    return render_template('water_intake.html', records=records_list, total_intake=total_intake,average_intake=average_intake)

@app.route('/clear-intake', methods=['POST'])
def clear_intake():
    email = session.get('email')
    # 清除当前用户的所有水摄入量记录
    mongo.db.intake_collection.delete_many({"email": email})

    # 重定向回水摄入量追踪页面
    return redirect(url_for('water'))

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route("/ajaxhistory", methods=['POST'])
def ajaxhistory():
    # ############################
    # ajaxhistory() is a POST function displays the fetches the various information from database
    # route "/ajaxhistory" will redirect to ajaxhistory() function.
    # Details corresponding to given email address are fetched from the database entries
    # Input: Email, date
    # Output: date, email, calories, burnout
    # ##########################
    email = get_session = session.get('email')
    print(email)
    if get_session is not None:
        if request.method == "POST":
            date = request.form.get('date')
            res = mongo.db.calories.find_one({'email': email, 'date': date}, {
                                             'date', 'email', 'calories', 'burnout'})
            if res:
                return json.dumps({'date': res['date'], 'email': res['email'], 'burnout': res['burnout'], 'calories': res['calories']}), 200, {
                    'ContentType': 'application/json'}
            else:
                return json.dumps({'date': "", 'email': "", 'burnout': "", 'calories': ""}), 200, {
                    'ContentType': 'application/json'}


@app.route("/community", methods=['GET'])
def friends():
    # ############################
    # friends() function displays the list of friends corrsponding to given email
    # route "/friends" will redirect to friends() function which redirects to friends.html page.
    # friends() function will show a list of "My friends", "Add Friends" functionality, "send Request" and Pending Approvals" functionality
    # Details corresponding to given email address are fetched from the database entries
    # Input: Email
    # Output: My friends, Pending Approvals, Sent Requests and Add new friends
    # ##########################
    email = session.get('email')

    #Create friends collection
    if 'friends' not in mongo.db.list_collection_names():
        # Create the collection if it does not exist
        mongo.db.create_collection('friends')

    myFriends = list(mongo.db.friends.find(
        {'sender': email, 'accept': True}, {'sender', 'receiver', 'accept'}))
    myFriendsList = list()
    for f in myFriends:
        myFriendsList.append(f['receiver'])

    print('My friends:  ', myFriends)

    allUsers = list(mongo.db.user.find({}, {'name', 'email'}))
    allUsersList = list()
    for u in allUsers:
        allUsersList.append(u['email'])

    pendingRequests = list(mongo.db.friends.find(
        {'sender': email, 'accept': False}, {'sender', 'receiver', 'accept'}))
    pendingReceivers = list()
    for p in pendingRequests:
        pendingReceivers.append(p['receiver'])

    print('Pending Requests: ', pendingReceivers)

    pendingApproves = list()
    pendingApprovals = list(mongo.db.friends.find(
        {'receiver': email, 'accept': False}, {'sender', 'receiver', 'accept'}))
    for p in pendingApprovals:
        pendingApproves.append(p['sender'])

    print('Pending Approvals: ', pendingApproves)

    return render_template('friends.html', allUsers=allUsersList, pendingRequests=pendingRequests, active=email,
                           pendingReceivers=pendingReceivers, pendingApproves=pendingApproves, myFriends=myFriends, myFriendsList=myFriendsList)


@app.route('/delete_friend', methods=['GET', 'POST'])
def delete_friend():
    email = session.get('email')
    friend_email = request.form.get('friend_email')
    mongo.db.friends.delete_one({'sender': email, 'receiver': friend_email})
    flash('Friendship deleted successfully!', 'success')

    return redirect(url_for('friends'))


@app.route('/bmi_calc', methods=['GET', 'POST'])
def bmi_calci():
    bmi = ''
    bmi_category = ''
    
    if request.method == 'POST' and 'weight' in request.form:
        weight = float(request.form.get('weight'))
        height = float(request.form.get('height'))
        bmi = calc_bmi(weight, height)
        bmi_category = get_bmi_category(bmi)
    
    return render_template("bmi_cal.html", bmi=bmi, bmi_category=bmi_category)

def calc_bmi(weight, height):
    return round((weight / ((height / 100) ** 2)), 2)

def get_bmi_category(bmi):
    if bmi < 18.5:
        return 'Underweight'
    elif bmi < 24.9:
        return 'Normal Weight'
    elif bmi < 29.9:
        return 'Overweight'
    else:
        return 'Obese'


@app.route("/send_email", methods=['GET','POST'])
def send_email():
    # ############################
    # send_email() function shares Calorie History with friend's email
    # route "/send_email" will redirect to send_email() function which redirects to friends.html page.
    # Input: Email
    # Output: Calorie History Received on specified email
    # ##########################
    email = session.get('email')
    temp = mongo.db.user.find_one({'email': email}, {'name'})
    data = list(mongo.db.calories.find({'email': email}, {'date','email','calories','burnout'}))
    table = [['Date','Email ID','Calories','Burnout']]
    for a in data:
        tmp = [a['date'],a['email'],a['calories'],a['burnout']] 
        table.append(tmp) 
    
    friend_email = str(request.form.get('share')).strip()
    server = smtplib.SMTP_SSL("smtp.gmail.com",465)
    #Storing sender's email address and password
    sender_email = "burnoutapp2023@gmail.com"
    sender_password = "jgny mtda gguq shnw"
    
    #Logging in with sender details
    server.login(sender_email,sender_password)
    message = 'Subject: Calorie History\n\n Your Friend '+str(temp['name'])+' has shared their calorie history with you!\n {}'.format(tabulate(table))
    server.sendmail(sender_email, friend_email, message)

    #Success message for the user
    flash('Calorie history shared successfully!', 'success')
    
    server.quit()
    
    return redirect(url_for('friends'))


@app.route("/ajaxsendrequest", methods=['POST'])
def ajaxsendrequest():
    # ############################
    # ajaxsendrequest() is a function that updates friend request information into database
    # route "/ajaxsendrequest" will redirect to ajaxsendrequest() function.
    # Details corresponding to given email address are fetched from the database entries and send request details updated
    # Input: Email, receiver
    # Output: DB entry of receiver info into database and return TRUE if success and FALSE otherwise
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        receiver = request.form.get('receiver')
        res = mongo.db.friends.insert_one(
            {'sender': email, 'receiver': receiver, 'accept': False})
        if res:
            #Success message for the user
            flash('Request sent!', 'success')

            return json.dumps({'status': True}), 200, {
                'ContentType': 'application/json'}
    return json.dumps({'status': False}), 500, {
        'ContentType:': 'application/json'}


@app.route("/ajaxcancelrequest", methods=['POST'])
def ajaxcancelrequest():
    # ############################
    # ajaxcancelrequest() is a function that updates friend request information into database
    # route "/ajaxcancelrequest" will redirect to ajaxcancelrequest() function.
    # Details corresponding to given email address are fetched from the database entries and cancel request details updated
    # Input: Email, receiver
    # Output: DB deletion of receiver info into database and return TRUE if success and FALSE otherwise
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        receiver = request.form.get('receiver')
        res = mongo.db.friends.delete_many(
            {'sender': email, 'receiver': receiver})
        if res:
            #Success message for the user
            flash('Request cancelled!', 'success')

            return json.dumps({'status': True}), 200, {
                'ContentType': 'application/json'}
    return json.dumps({'status': False}), 500, {
        'ContentType:': 'application/json'}


@app.route("/ajaxapproverequest", methods=['POST'])
def ajaxapproverequest():
    # ############################
    # ajaxapproverequest() is a function that updates friend request information into database
    # route "/ajaxapproverequest" will redirect to ajaxapproverequest() function.
    # Details corresponding to given email address are fetched from the database entries and approve request details updated
    # Input: Email, receiver
    # Output: DB updation of accept as TRUE info into database and return TRUE if success and FALSE otherwise
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        receiver = request.form.get('receiver')
        print(email, receiver)
        res = mongo.db.friends.update_one({'sender': receiver, 'receiver': email}, {
                                          "$set": {'sender': receiver, 'receiver': email, 'accept': True}})
        mongo.db.friends.insert_one(
            {'sender': email, 'receiver': receiver, 'accept': True})
        if res:
            #Success message for the user
            flash('Request approved!', 'success')

            return json.dumps({'status': True}), 200, {
                'ContentType': 'application/json'}
    return json.dumps({'status': False}), 500, {
        'ContentType:': 'application/json'}


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    # ############################
    # dashboard() function displays the dashboard.html template
    # route "/dashboard" will redirect to dashboard() function.
    # dashboard() called and displays the list of activities
    # Output: redirected to dashboard.html
    # ##########################
    email = session.get('email')
    if email:
        student = mongo.db.profile.find_one({"email": email})

        if student:
            print('671ea6c405d47736f9539064' ,student["_id"])
            student_id = student["_id"]
            # Fetch the meetings where the student ID matches the profile's _id
            upcoming_meetings = list(mongo.db.meetings.find({
                "student_id": str(student["_id"]) # Using the ObjectId directly
            }).sort("created_at", -1).limit(5))
            print("upc",upcoming_meetings)
            # List of exercises (example data)
            exercises = [
                {"id": 1, "name": "Yoga"},
                {"id": 2, "name": "Swimming"},
            ]
        else:
            upcoming_meetings = []
            exercises = []
    else:
        upcoming_meetings = []
        exercises = []

    return render_template('dashboard.html', title='Dashboard', exercises=exercises, upcoming_meetings = upcoming_meetings)


@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    email = get_session = session.get('email')
    if session.get('email'):
        data = request.get_json()
        exercise_id = data.get('exercise_id')
        print(exercise_id)
        action = data.get('action')
        exercise = mongo.db.your_exercise_collection.find_one({"exercise_id": exercise_id})
        print(exercise)
        if exercise:
            if action=="add":
            # Create a new document in the favorites schema (you can customize this schema)
                favorite = {
                    "exercise_id":exercise.get("exercise_id"),
                    "email": email,
                    "image": exercise.get("image"),
                    "video_link": exercise.get("video_link"),
                    "name": exercise.get("name"),
                    "description": exercise.get("description"),
                    "href": exercise.get("href")
                }

            # Insert the exercise into the favorites collection
                mongo.db.favorites.insert_one(favorite)
                return jsonify({"status": "success"})
            elif action=="remove":
                print(exercise.get("exercise_id"))
                print("iamhere1")
                mongo.db.favorites.delete_one({"email": email, "exercise_id": exercise.get("exercise_id")})
                return jsonify({"status": "success"})


        else:
            return jsonify({"status": "error", "message": "Exercise not found"})
    else:
        return redirect(url_for('login'))

    return json.dumps({'status': False}), 500, {
        'ContentType:': 'application/json'
    }

@app.route('/favorites')
def favorites():
    email = session.get('email')
    if not email:
        # Redirect the user to the login page or show an error message
        return redirect(url_for('login'))

    # Query MongoDB to get the user's favorite exercises
    favorite_exercises = mongo.db.favorites.find({"email": email})

    return render_template('favorites.html', favorite_exercises=favorite_exercises)
    

@app.route("/yoga", methods=['GET', 'POST'])
def yoga():
    # ############################
    # yoga() function displays the yoga.html template
    # route "/yoga" will redirect to yoga() function.
    # A page showing details about yoga is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "yoga"
                mongo.db.user.insert({'Email': email, 'Status': enroll})
            flash(
                f' You have succesfully enrolled in our {enroll} plan!',
                'success')
            return render_template('new_dashboard.html', form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('yoga.html', title='Yoga', form=form)


@app.route("/headspace", methods=['GET', 'POST'])
def headspace():
    # ############################
    # headspace() function displays the headspace.html template
    # route "/headspace" will redirect to headspace() function.
    # A page showing details about headspace is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "headspace"
                mongo.db.user.insert({'Email': email, 'Status': enroll})
            flash(
                f' You have succesfully enrolled in our {enroll} plan!',
                'success')
            return render_template('new_dashboard.html', form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('Headspace.html', title='Headspace', form=form)


@app.route("/mbsr", methods=['GET', 'POST'])
def mbsr():
    # ############################
    # headspace() function displays the headspace.html template
    # route "/headspace" will redirect to headspace() function.
    # A page showing details about headspace is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "mbsr"
                mongo.db.user.insert({'Email': email, 'Status': enroll})
            flash(
                f' You have succesfully enrolled in our {enroll} plan!',
                'success')
            return render_template('new_dashboard.html', form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('mbsr.html', title='mbsr', form=form)


@app.route("/swim", methods=['GET', 'POST'])
def swim():
    # ############################
    # swim() function displays the swim.html template
    # route "/swim" will redirect to swim() function.
    # A page showing details about swimming is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "swimming"
                mongo.db.user.insert({'Email': email, 'Status': enroll})
            flash(
                f' You have succesfully enrolled in our {enroll} plan!',
                'success')
            return render_template('new_dashboard.html', form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('swim.html', title='Swim', form=form)


@app.route("/abbs", methods=['GET', 'POST'])
def abbs():
    # ############################
    # abbs() function displays the abbs.html template
    # route "/abbs" will redirect to abbs() function.
    # A page showing details about abbs workout is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "abbs"
                mongo.db.user.insert({'Email': email, 'Status': enroll})
            flash(
                f' You have succesfully enrolled in our {enroll} plan!',
                'success')
            return render_template('new_dashboard.html', form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('abbs.html', title='Abbs Smash!', form=form)


@app.route("/belly", methods=['GET', 'POST'])
def belly():
    # ############################
    # belly() function displays the belly.html template
    # route "/belly" will redirect to belly() function.
    # A page showing details about belly workout is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "belly"
                mongo.db.user.insert({'Email': email, 'Status': enroll})
            flash(
                f' You have succesfully enrolled in our {enroll} plan!',
                'success')
            return render_template('new_dashboard.html', form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('belly.html', title='Belly Burner', form=form)


@app.route("/core", methods=['GET', 'POST'])
def core():
    # ############################
    # core() function displays the belly.html template
    # route "/core" will redirect to core() function.
    # A page showing details about core workout is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "core"
                mongo.db.user.insert({'Email': email, 'Status': enroll})
            flash(
                f' You have succesfully enrolled in our {enroll} plan!',
                'success')
            return render_template('new_dashboard.html', form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('core.html', title='Core Conditioning', form=form)


@app.route("/gym", methods=['GET', 'POST'])
def gym():
    # ############################
    # gym() function displays the gym.html template
    # route "/gym" will redirect to gym() function.
    # A page showing details about gym plan is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "gym"
                mongo.db.user.insert({'Email': email, 'Status': enroll})
            flash(
                f' You have succesfully enrolled in our {enroll} plan!',
                'success')
            return render_template('new_dashboard.html', form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('gym.html', title='Gym', form=form)

@app.route("/walk", methods=['GET', 'POST'])
def walk():
    # ############################
    # walk() function displays the walk.html template
    # route "/walk" will redirect to walk() function.
    # A page showing details about walk plan is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "walk"
                mongo.db.user.insert({'Email': email, 'Status': enroll})
            flash(
                f' You have succesfully enrolled in our {enroll} plan!',
                'success')
            return render_template('new_dashboard.html', form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('walk.html', title='Walk', form=form)

@app.route("/dance", methods=['GET', 'POST'])
def dance():
    # ############################
    # dance() function displays the dance.html template
    # route "/dance" will redirect to dance() function.
    # A page showing details about dance plan is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "dance"
                mongo.db.user.insert({'Email': email, 'Status': enroll})
            flash(
                f' You have succesfully enrolled in our {enroll} plan!',
                'success')
            return render_template('new_dashboard.html', form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('dance.html', title='Dance', form=form)

@app.route("/hrx", methods=['GET', 'POST'])
def hrx():
    # ############################
    # hrx() function displays the hrx.html template
    # route "/hrx" will redirect to hrx() function.
    # A page showing details about hrx plan is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "hrx"
                mongo.db.user.insert({'Email': email, 'Status': enroll})
            flash(
                f' You have succesfully enrolled in our {enroll} plan!',
                'success')
            return render_template('new_dashboard.html', form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('hrx.html', title='HRX', form=form)

# @app.route("/ajaxdashboard", methods=['POST'])
# def ajaxdashboard():
#     # ############################
#     # login() function displays the Login form (login.html) template
#     # route "/login" will redirect to login() function.
#     # LoginForm() called and if the form is submitted then various values are fetched and verified from the database entries
#     # Input: Email, Password, Login Type
#     # Output: Account Authentication and redirecting to Dashboard
#     # ##########################
#     email = get_session = session.get('email')
#     print(email)
#     if get_session is not None:
#         if request.method == "POST":
#             result = mongo.db.user.find_one(
#                 {'email': email}, {'email', 'Status'})
#             if result:
#                 return json.dumps({'email': result['email'], 'Status': result['result']}), 200, {
#                     'ContentType': 'application/json'}
#             else:
#                 return json.dumps({'email': "", 'Status': ""}), 200, {
#                     'ContentType': 'applicration/json'}

@app.route("/submit_review", methods=["GET", "POST"])
def submit_review():
    if not session.get("email"):
        return redirect(url_for("login"))

    student_email = session["email"]

    # Retrieve the student's profile to get the assigned coach's ID
    student_profile = mongo.db.profile.find_one({"email": student_email, "user_type": "student"})


    # Retrieve coach's ID from student's profile and then get coach's details
    coach_name = student_profile["coach"]

    if request.method == "POST":
        # Handle form submission
        student_name = request.form["name"]
        review_text = request.form["review"]

        # Insert the review into the coach's profile
        mongo.db.profile.update_one(
            {"name": coach_name, "user_type": "coach"},
            {"$push": {
                "reviews": {
                    "name": student_name,
                    "review": review_text,
                    "student_email": student_email
                }
            }}
        )

        flash("Review submitted successfully!", "success")
        return redirect(url_for("dashboard"))

    # Render the form and pass coach_name to the template
    return render_template("review.html", title="Submit Review", coach_name=coach_name)



@app.route('/blog')
def blog():
    # 处理 "blog" 页面的逻辑
    return render_template('blog.html')


from flask import render_template, session, redirect, url_for, request, flash
from datetime import datetime
from bson.objectid import ObjectId

@app.route("/coach_dashboard", methods=["GET"])
def coach_dashboard():
    if not session.get("email"):
        return redirect(url_for("login"))

    coach_email = session["email"]
    coach_data = mongo.db.user.find_one({"email": coach_email})
    students = list(mongo.db.user.find({"user_type": "student", "coach": coach_data["name"]}))
    form_reviews = list(mongo.db.form_reviews.find({"coach_email": coach_email}))
    reminders = list(mongo.db.reminders.find({"coach_email": coach_email}))

    # Retrieve upcoming meetings, limited to next 5, sorted by date
    upcoming_meetings = list(mongo.db.meetings.find({
        "coach_email": coach_email
    }).sort("created_at", -1).limit(5))
    
    print(upcoming_meetings)
    return render_template(
        "coach_dashboard.html",
        title="Coach Dashboard",
        students=students,
        form_reviews=form_reviews,
        upcoming_meetings=upcoming_meetings,
        reminders=reminders,
        coach=coach_data
    )

@app.route("/schedule_meeting", methods=["GET", "POST"])
def schedule_meeting():
    if not session.get("email"):
        return redirect(url_for("login"))

    coach_email = session["email"]

    if request.method == "POST":
        # Handle form submission
        student_id = request.form["student_id"]
        meeting_date = request.form["date"]
        meeting_time = request.form["time"]
        meeting_link = request.form["link"]

        # Insert the meeting into the database for the specific student
        mongo.db.meetings.insert_one({
            "coach_email": coach_email,
            "student_id": student_id,
            "date": meeting_date,
            "time": meeting_time,
            "link": meeting_link
        })
        flash("Meeting scheduled successfully!", "success")
        return redirect(url_for("coach_dashboard"))

    # Fetch all students of the coach
    coach_data = mongo.db.user.find_one({"email": coach_email})
    students = list(mongo.db.profile.find({"user_type": "student", "coach": coach_data["name"]}))

    return render_template("schedule_meetings.html", title="Schedule Meeting", students=students)

# Route to Submit Feedback on Form Review
@app.route("/submit_feedback", methods=["GET", "POST"])
def submit_feedback():
    if not session.get("email"):
        return redirect(url_for("login"))

    if request.method == "POST":
        # Handle form submission
        review_id = request.form.get("review_id")
        feedback = request.form["feedback"]

        mongo.db.form_reviews.update_one(
            {"_id": ObjectId(review_id)},
            {"$set": {"feedback": feedback, "reviewed": True, "feedback_date": datetime.now()}}
        )
        flash("Feedback submitted successfully!", "success")
        return redirect(url_for("coach_dashboard"))
    
    # Render the feedback submission form
    return render_template("submit_feedback.html", title="Submit Feedback")

# Route to Set a Reminder
@app.route("/set_reminder", methods=["GET", "POST"])
def set_reminder():
    if not session.get("email"):
        return redirect(url_for("login"))

    coach_email = session["email"]

    if request.method == "POST":
        # Handle form submission
        student_id = request.form["student_id"]
        reminder_text = request.form["reminder"]
        reminder_date = request.form["date"]
        reminder_time = request.form["time"]

        # Insert the reminder into the database for the specific student
        mongo.db.reminders.insert_one({
            "coach_email": coach_email,
            "student_id": student_id,
            "reminder_text": reminder_text,
            "date": reminder_date,
            "time": reminder_time
        })
        flash("Reminder set successfully!", "success")
        return redirect(url_for("coach_dashboard"))

    # If GET request, fetch all students of the coach
    coach_data = mongo.db.user.find_one({"email": coach_email})
    students = list(mongo.db.profile.find({"user_type": "student", "coach": coach_data["name"]}))

    return render_template("set_reminder.html", title="Set Reminder", students=students)


@app.route("/coach_reviews")
def coach_reviews():
    if not session.get("email"):
        return redirect(url_for("login"))

    # Fetch the coach's name from the session or profile
    coach_email = session["email"]
    coach_profile = mongo.db.profile.find_one({"email": coach_email})
    coach_name = coach_profile["name"]  # assuming coach's name is stored here
    
    # Get form reviews assigned to this coach
    reviews = list(mongo.db.form_reviews.find({"coach_name": coach_name}))

    # Get students with their progress
    students_progress = list(mongo.db.profile.find(
        {"coach": coach_name, "user_type": "student"},
        {"name": 1, "progress": 1}  # only retrieve relevant fields
    ))

    print(students_progress)

    # Pass reviews and students' progress to the template
    return render_template("coach_reviews.html", reviews=reviews, students_progress=students_progress)

@app.route("/upload_exercise_video", methods=["POST", "GET"])
def upload_exercise_video():
    if not session.get("email"):
        return redirect(url_for("login"))

    student_email = session["email"]
    
    if request.method == "POST":
        # Get form data
        exercise_type = request.form.get("exercise_type")
        video_link = request.form.get("video_link")

        # Fetch the assigned coach for the student
        student_profile = mongo.db.profile.find_one({"email": student_email})
        coach_name = student_profile["coach"]  # assuming the coach's name is stored here

        # Insert data into MongoDB with coach details and initialize comments to null
        mongo.db.form_reviews.insert_one({
            "student_email": student_email,
            "exercise_type": exercise_type,
            "video_link": video_link,
            "reviewed": False,
            "submission_date": datetime.now(),
            "coach_name": coach_name,
            "comments": None,  # Initialize comments as null
            "feedback": None,  # Initialize feedback as null
            "feedback_date": None  # Initialize feedback_date as null
        })

        flash("Video submitted successfully for review!", "success")
        return redirect(url_for("upload_exercise_video"))  # Redirect to the same page to show updated list

    # Fetch all reviews for the logged-in student to display on the page
    reviews = list(mongo.db.form_reviews.find({"student_email": student_email}))

    # Render the upload form template with the reviews data
    return render_template("student_review_form.html", reviews=reviews)

@app.route("/coach_profile", methods=["GET", "POST"])
def coach_profile():
    if not session.get("email"):
        return redirect(url_for("login"))

    coach_email = session["email"]
    # Retrieve the coach profile
    coach_data = mongo.db.profile.find_one({"email": coach_email})

    # Get students assigned to this coach
    students = list(mongo.db.profile.find({"user_type": "student", "coach": coach_data["name"]}))

    # Fetch reviews directly from the coach's profile
    reviews = coach_data.get("reviews", [])

    # If it's a POST request, handle the review submission
    if request.method == "POST":
        review_content = request.form.get("review")
        student_name = request.form.get("student_name")

        # Update the coach's profile by adding the new review
        mongo.db.profile.update_one(
            {"email": coach_email},
            {"$push": {
                "reviews": {
                    "name": student_name,
                    "review": review_content,
                    "student_email": session["email"],
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
            }}
        )

        flash("Review submitted successfully!", "success")
        return redirect(url_for("coach_profile"))

    return render_template(
        "coach_profile.html",
        title="Coach Profile",
        coach=coach_data,
        students=students,
        reviews=reviews
    )


@app.route("/upload_tutorial", methods=["GET", "POST"])
def upload_tutorial():
    if not session.get("email"):
        return redirect(url_for("login"))

    # Fetch coach's students based on the logged-in coach's email
    coach_email = session["email"]
    coach_data = mongo.db.user.find_one({"email": coach_email})
    print(coach_data)  # This will help confirm the structure of the returned document

    # Access the coach's name correctly using dictionary indexing
    students = list(mongo.db.profile.find({"coach": coach_data["name"]}))


    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        video_link = request.form.get("video_link")
        assigned_students = request.form.getlist("assigned_students")  # List of student IDs

        # Insert tutorial details in the `tutorials` collection
        tutorial_id = mongo.db.tutorials.insert_one({
            "title": title,
            "description": description,
            "video_link": video_link,
            "upload_date": datetime.now(),
            "coach_email": coach_email,
        }).inserted_id

        # Assign the tutorial to each selected student
        for student_id in assigned_students:
            mongo.db.profile.update_one(
                {"_id": ObjectId(student_id)},
                {"$push": {
                    "assigned_tutorials": {
                        "tutorial_id": tutorial_id,
                        "status": "Not Started"
                    }
                }}
            )

        flash("Tutorial uploaded and assigned successfully!", "success")
        return redirect(url_for("upload_tutorial"))

    return render_template("upload_tutorial.html", title="Upload Tutorial", students=students)

@app.route("/view_assigned_tutorials", methods=["GET", "POST"])
def view_assigned_tutorials():
    if not session.get("email"):
        return redirect(url_for("login"))

    # Get the logged-in student's profile
    student_email = session["email"]
    student = mongo.db.profile.find_one({"email": student_email})

    # Retrieve assigned tutorials with their completion status
    tutorials = []
    for tutorial_entry in student.get("assigned_tutorials", []):
        # Fetch full tutorial details
        tutorial = mongo.db.tutorials.find_one({"_id": tutorial_entry["tutorial_id"]})
        if tutorial:
            tutorial["status"] = tutorial_entry["status"]
            tutorials.append(tutorial)

    # Handle marking a tutorial as completed
    if request.method == "POST":
        tutorial_id = request.form.get("tutorial_id")

        # Update the tutorial status to "Completed"
        mongo.db.profile.update_one(
            {"_id": student["_id"], "assigned_tutorials.tutorial_id": ObjectId(tutorial_id)},
            {"$set": {"assigned_tutorials.$.status": "Completed"}}
        )

        # Re-fetch the updated student data to recalculate progress
        student = mongo.db.profile.find_one({"_id": student["_id"]})
        completed_count = sum(1 for t in student["assigned_tutorials"] if t["status"] == "Completed")
        total_tutorials = len(student["assigned_tutorials"])
        progress = (completed_count / total_tutorials) * 100 if total_tutorials > 0 else 0

        # Update the progress in the student's profile
        mongo.db.profile.update_one(
            {"_id": student["_id"]},
            {"$set": {"progress": progress}}
        )

        flash("Tutorial marked as completed!", "success")
        return redirect(url_for("view_assigned_tutorials"))

    return render_template("view_assigned_tutorials.html", tutorials=tutorials, progress=student.get("progress", 0))

@app.route("/manage_plans", methods=["GET", "POST"])
def manage_plans():
    if not session.get("email"):
        return redirect(url_for("login"))

    coach_email = session["email"]
    coach = mongo.db.profile.find_one({"email": coach_email, "user_type": "coach"})

    # Check if we are editing an existing plan
    edit_plan_id = request.args.get("edit_plan_id")  # Fetch the ID if provided
    plan = mongo.db.plans.find_one({"_id": ObjectId(edit_plan_id)}) if edit_plan_id else None

    if request.method == "POST":
        if "create_or_edit_plan" in request.form:
            # Handle creation or editing
            title = request.form.get("title")
            description = request.form.get("description")
            plan_type = request.form.get("type")
            duration_weeks = int(request.form.get("duration_weeks"))

            # Get steps
            steps = []
            step_count = int(request.form.get("step_count", 0))
            for i in range(1, step_count + 1):
                step_description = request.form.get(f"step_description_{i}")
                target_duration = request.form.get(f"target_duration_{i}")
                frequency = request.form.get(f"frequency_{i}")
                exercises = request.form.get(f"exercises_{i}").split(",") if request.form.get(f"exercises_{i}") else []
                meal_plan = request.form.get(f"meal_plan_{i}").split(",") if request.form.get(f"meal_plan_{i}") else []

                steps.append({
                    "step_id": i,
                    "description": step_description,
                    "target_duration": target_duration,
                    "frequency": frequency,
                    "exercises": exercises,
                    "meal_plan": meal_plan
                })

            # Check if we are editing an existing plan
            if edit_plan_id:
                # Update the existing plan
                mongo.db.plans.update_one(
                    {"_id": ObjectId(edit_plan_id)},
                    {"$set": {
                        "title": title,
                        "description": description,
                        "type": plan_type,
                        "duration_weeks": duration_weeks,
                        "steps": steps
                    }}
                )

                # Update the plan details in students' profiles if the plan was assigned
                mongo.db.profile.update_many(
                    {"user_type": "student", "assigned_plans.plan_id": edit_plan_id},
                    {"$set": {
                        "assigned_plans.$[elem].title": title,
                        "assigned_plans.$[elem].description": description,
                        "assigned_plans.$[elem].type": plan_type,
                        "assigned_plans.$[elem].duration_weeks": duration_weeks,
                        "assigned_plans.$[elem].steps": steps
                    }},
                    array_filters=[{"elem.plan_id": edit_plan_id}]
                )

                flash("Plan updated successfully!", "success")

            else:
                # If no `edit_plan_id`, insert a new plan
                mongo.db.plans.insert_one({
                    "title": title,
                    "description": description,
                    "type": plan_type,
                    "duration_weeks": duration_weeks,
                    "steps": steps,
                    "coach_id": coach["_id"],
                    "coach_name": coach["name"]
                })
                flash("Plan created successfully!", "success")

            return redirect(url_for("manage_plans"))

        elif "assign_plan" in request.form:
            # Assign Plan to Students
            plan_id = request.form.get("plan_id")
            selected_students = request.form.getlist("students")
            plan = mongo.db.plans.find_one({"_id": ObjectId(plan_id)})

            for student_id in selected_students:
                mongo.db.profile.update_one(
                    {"_id": ObjectId(student_id), "user_type": "student"},
                    {"$addToSet": {
                        "assigned_plans": {
                            "plan_id": plan_id,
                            "title": plan["title"],
                            "description": plan["description"],
                            "type": plan["type"],
                            "duration_weeks": plan["duration_weeks"],
                            "steps": plan["steps"],
                            "status": "assigned"
                        }
                    }}
                )

            flash("Plan assigned to selected students!", "success")
            return redirect(url_for("manage_plans"))

    # Fetch all plans and students for the coach
    plans = list(mongo.db.plans.find({"coach_id": coach["_id"]}))
    students = list(mongo.db.profile.find({"coach": coach["name"], "user_type": "student"}))

    return render_template("manage_plans.html", plans=plans, students=students, edit_plan=plan, edit_plan_id=edit_plan_id)

@app.route("/student_plans", methods=["GET"])
def student_plans():
    if not session.get("email"):
        return redirect(url_for("login"))

    student_email = session["email"]
    student = mongo.db.profile.find_one({"email": student_email, "user_type": "student"})

    # Retrieve assigned plans for the student
    assigned_plans = student.get("assigned_plans", [])

    return render_template("student_plans.html", assigned_plans=assigned_plans)


if __name__ == '__main__':
    app.run(debug=True)