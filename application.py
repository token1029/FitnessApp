"""
Copyright (c) 2023 Rajat Chandak, Shubham Saboo, Vibhav Deo, Chinmay Nayak
This code is licensed under MIT license (see LICENSE for details)

@author: Burnout

This python file is used in and is part of the Burnout project.

For more information about the Burnout project, visit:
https://github.com/VibhavDeo/FitnessApp
"""
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from bson import ObjectId
import bcrypt
import smtplib
from flask import json, jsonify, Flask, render_template, session, url_for, flash, redirect, request
from flask_mail import Mail, Message
from flask_pymongo import PyMongo
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from tabulate import tabulate
from forms import HistoryForm, RegistrationForm, LoginForm, CalorieForm, UserProfileForm, EnrollForm, ReviewForm
from insert_db_data import insertfooddata, insertexercisedata
import schedule
from threading import Thread
import time
import os  # For environment variables

app = Flask(__name__, template_folder='templates')

# Security: Fetch secret key and mail password from environment variables
app.secret_key = os.environ.get('SECRET_KEY') or 'a_very_secure_secret_key'
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/test'
app.config['MONGO_CONNECT'] = False
mongo = PyMongo(app)

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "burnoutapp2023@gmail.com"
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') or "jgny mtda gguq shnw"  # Replace with secure method
mail = Mail(app)

# Initialize the serializer
s = URLSafeTimedSerializer(app.secret_key)

insertfooddata()
insertexercisedata()


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

            # Using Flask-Mail instead of smtplib for consistency
            with mail.connect() as conn:
                for e in recipientlst:
                    print(e)
                    msg = Message('Daily Reminder to Exercise',
                                  sender=app.config['MAIL_USERNAME'],
                                  recipients=[e])
                    msg.body = 'Hi,\n\nThis is your daily reminder to exercise. Stay fit and healthy!\n\nBest regards,\nThe Burnout Team'
                    conn.send(msg)
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
    """"
    login() function displays the Login form (login.html) template
    route "/login" will redirect to login() function.
    LoginForm() called and if the form is submitted then various values are fetched and verified from the database entries
    Input: Email, Password, Login Type
    Output: Account Authentication and redirecting to Dashboard
    """
    if not session.get('email'):
        form = LoginForm()
        if form.validate_on_submit():
            user = mongo.db.user.find_one({'email': form.email.data})
            if user:
                if not user.get('is_verified'):
                    flash('Please verify your email address before logging in.', 'warning')
                    return redirect(url_for('login'))
                if bcrypt.checkpw(form.password.data.encode("utf-8"), user['pwd']):
                    flash('You have been logged in!', 'success')
                    session['email'] = user['email']
                    session['name'] = user['name']
                    # session['login_type'] = form.type.data
                    return redirect(url_for('dashboard'))
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
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/sleep', methods=['GET','POST'])
def sleep():
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
    return render_template('sleep.html', records=records_list, total_intake=total_intake,average_intake=average_intake)

@app.route("/register", methods=['GET', 'POST'])
def register():
    """
    register() function displays the Registration portal (register.html) template
    route "/register" will redirect to register() function.
    RegistrationForm() called and if the form is submitted then various values are fetched and updated into database
    Input: Username, Email, Password, Confirm Password
    Output: Value update in database and redirected to home login page
    """
    now = datetime.now().strftime('%Y-%m-%d')

    if not session.get('email'):
        form = RegistrationForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                username = form.username.data
                email = form.email.data
                password = form.password.data

                # Check if the user already exists
                if mongo.db.user.find_one({'email': email}):
                    flash('Email address already exists. Please log in or use a different email.', 'danger')
                    return redirect(url_for('register'))

                # Hash the password
                hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

                # Generate a unique token for email verification
                token = s.dumps(email, salt='email-confirm')

                # Insert the new user with is_verified set to False
                mongo.db.user.insert_one({
                    'name': username,
                    'email': email,
                    'pwd': hashed_password,
                    'is_verified': False,
                    'verification_token': token
                })

                # Insert profile data
                weight = form.weight.data
                height = form.height.data
                goal = form.goal.data
                target_weight = form.target_weight.data
                mongo.db.profile.insert_one({
                    'email': email,
                    'date': now,
                    'height': height,
                    'weight': weight,
                    'goal': goal,
                    'target_weight': target_weight
                })

                # Send verification email
                verify_url = url_for('verify_email', token=token, _external=True)
                msg = Message('Please Confirm Your Email', sender=app.config['MAIL_USERNAME'], recipients=[email])
                msg.body = f'''Hi {username},

Thank you for registering at Burnout!

Please click the link below to verify your email address:

{verify_url}

If you did not make this request, please ignore this email.

Best regards,
The Burnout Team
'''
                mail.send(msg)

                flash('Account created successfully! Please check your email to verify your account.', 'success')
                return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/join", methods=['GET', 'POST'])
def join():
    """
    join() function displays the Registration portal (join.html) template
    route "/join" will redirect to join() function.
    RegistrationForm() called and if the form is submitted then various values are fetched and updated into database
    Input: Username, Email, Password, Confirm Password
    Output: Value update in database and redirected to home login page
    """
    now = datetime.now().strftime('%Y-%m-%d')

    if not session.get('email'):
        form = RegistrationForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                username = form.username.data
                email = form.email.data
                password = form.password.data

                # Check if the user already exists
                if mongo.db.user.find_one({'email': email}):
                    flash('Email address already exists. Please log in or use a different email.', 'danger')
                    return redirect(url_for('join'))

                # Hash the password
                hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

                # Generate a unique token for email verification
                token = s.dumps(email, salt='email-confirm')

                # Insert the new user with is_verified set to False
                mongo.db.user.insert_one({
                    'name': username,
                    'email': email,
                    'pwd': hashed_password,
                    'is_verified': False,
                    'verification_token': token
                })

                # Insert profile data
                weight = form.weight.data
                height = form.height.data
                goal = form.goal.data
                target_weight = form.target_weight.data
                mongo.db.profile.insert_one({
                    'email': email,
                    'date': now,
                    'height': height,
                    'weight': weight,
                    'goal': goal,
                    'target_weight': target_weight
                })

                # Send verification email
                verify_url = url_for('verify_email', token=token, _external=True)
                msg = Message('Please Confirm Your Email', sender=app.config['MAIL_USERNAME'], recipients=[email])
                msg.body = f'''Hi {username},

Thank you for registering at Burnout!

Please click the link below to verify your email address:

{verify_url}

If you did not make this request, please ignore this email.

Best regards,
The Burnout Team
'''
                mail.send(msg)

                flash('Account created successfully! Please check your email to verify your account.', 'success')
                return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))
    return render_template('join.html', title='Register', form=form)


@app.route('/verify_email/<token>')
def verify_email(token):
    """
    verify_email() function handles the email verification when a user clicks the link sent to their email.
    route "/verify_email/<token>" will redirect to verify_email() function.
    Input: Token
    Output: Account verification and redirecting to login page
    """
    try:
        # The token expires after 1 hour (3600 seconds)
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        flash('The verification link has expired. Please request a new one.', 'danger')
        return redirect(url_for('resend_verification'))
    except BadSignature:
        flash('Invalid verification token.', 'danger')
        return redirect(url_for('home'))

    user = mongo.db.user.find_one({'email': email})
    if user:
        if user.get('is_verified'):
            flash('Account already verified. Please log in.', 'info')
        else:
            mongo.db.user.update_one({'email': email}, {'$set': {'is_verified': True}})
            flash('Your account has been verified! You can now log in.', 'success')
    else:
        flash('Account not found.', 'danger')
    return redirect(url_for('login'))


@app.route('/resend_verification', methods=['GET', 'POST'])
def resend_verification():
    """
    resend_verification() function allows users to request a new verification email.
    route "/resend_verification" will redirect to resend_verification() function.
    Input: Email
    Output: Sends a new verification email if conditions are met
    """
    if request.method == 'POST':
        email = request.form.get('email')
        user = mongo.db.user.find_one({'email': email})
        if user:
            if not user.get('is_verified'):
                token = s.dumps(email, salt='email-confirm')
                verify_url = url_for('verify_email', token=token, _external=True)
                msg = Message('Please Confirm Your Email', sender=app.config['MAIL_USERNAME'], recipients=[email])
                msg.body = f'''Hi {user["name"]},

You requested a new verification email. Please click the link below to verify your email address:

{verify_url}

If you did not make this request, please ignore this email.

Best regards,
The Burnout Team
'''
                mail.send(msg)
                flash('A new verification email has been sent.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Account already verified. Please log in.', 'info')
        else:
            flash('Email address not found. Please register first.', 'danger')
    return render_template('resend_verification.html')


@app.route("/calories", methods=['GET', 'POST'])
def calories():
    """
    calorie() function displays the Calorieform (calories.html) template
    route "/calories" will redirect to calories() function.
    CalorieForm() called and if the form is submitted then various values are fetched and updated into the database entries
    Input: Email, date, food, burnout
    Output: Value update in database and redirected to home page
    """
    now = datetime.now().strftime('%Y-%m-%d')

    get_session = session.get('email')
    if get_session is not None:
        form = CalorieForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                email = session.get('email')
                food = form.food.data
                try:
                    cals = int(food.split(" ")[-1][1:-1])
                except (ValueError, IndexError):
                    flash('Invalid food input format. Please try again.', 'danger')
                    return redirect(url_for('calories'))
                burn = form.burnout.data

                temp = mongo.db.calories.find_one({'email': email, 'date': now})
                if temp:
                    mongo.db.calories.update_one({'email': email, 'date': now}, {
                        '$set': {
                            'calories': temp['calories'] + cals,
                            'burnout': temp['burnout'] + int(burn)
                        }
                    })
                else:
                    mongo.db.calories.insert_one({
                        'date': now,
                        'email': email,
                        'calories': cals,
                        'burnout': int(burn)
                    })
                flash('Successfully updated the data', 'success')
                return redirect(url_for('calories'))
    else:
        return redirect(url_for('home'))
    return render_template('calories.html', form=form, time=now)


@app.route("/display_profile", methods=['GET', 'POST'])
def display_profile():
    """
    Display user profile and graph
    """
    now = datetime.now().strftime('%Y-%m-%d')

    if session.get('email'):
        email = session.get('email')
        user_data = mongo.db.profile.find_one({'email': email})
        if not user_data:
            flash('User profile not found.', 'danger')
            return redirect(url_for('user_profile'))
        target_weight = float(user_data['target_weight'])
        user_data_hist = list(mongo.db.profile.find({'email': email}))

        for entry in user_data_hist:
            entry['date'] = datetime.strptime(entry['date'], '%Y-%m-%d').date()

        sorted_user_data_hist = sorted(user_data_hist, key=lambda x: x['date'])
        # Extracting data for the graph
        dates = [entry['date'] for entry in sorted_user_data_hist]
        weights = [float(entry['weight']) for entry in sorted_user_data_hist]

        # Plotting Graph 
        fig = px.line(x=dates, y=weights, labels={'x': 'Date', 'y': 'Weight'}, title='Progress', markers=True, line_shape='spline')
        fig.add_trace(go.Scatter(x=dates, y=[target_weight] * len(dates),
                                 mode='lines',
                                 line=dict(color='green', width=1, dash='dot'),
                                 name='Target Weight'))
        fig.update_yaxes(range=[min(min(weights), target_weight) - 5, max(max(weights), target_weight) + 5])
        fig.update_xaxes(range=[min(dates), datetime.strptime(now, '%Y-%m-%d').date()]) 
        # Converting to HTML
        graph_html = fig.to_html(full_html=False)

        last_10_entries = sorted_user_data_hist[-10:]

        return render_template('display_profile.html', status=True, user_data=user_data, graph_html=graph_html, last_10_entries=last_10_entries)
    else:
        return redirect(url_for('login'))
    # return render_template('user_profile.html', status=True, form=form) #


@app.route("/user_profile", methods=['GET', 'POST'])
def user_profile():
    """
    user_profile() function displays the UserProfileForm (user_profile.html) template
    route "/user_profile" will redirect to user_profile() function.
    user_profile() called and if the form is submitted then various values are fetched and updated into the database entries
    Input: Email, height, weight, goal, Target weight
    Output: Value update in database and redirected to home login page.
    """
    now = datetime.now().strftime('%Y-%m-%d')

    if session.get('email'):
        form = UserProfileForm()
        if form.validate_on_submit():
            email = session.get('email')
            weight = form.weight.data
            height = form.height.data
            goal = form.goal.data
            target_weight = form.target_weight.data
            temp = mongo.db.profile.find_one({'email': email, 'date': now})
            if temp:
                mongo.db.profile.update_one({'email': email, 'date': now}, {
                    '$set': {
                        'weight': weight,
                        'height': height,
                        'goal': goal,
                        'target_weight': target_weight
                    }
                })
            else:
                mongo.db.profile.insert_one({
                    'email': email,
                    'date': now,
                    'height': height,
                    'weight': weight,
                    'goal': goal,
                    'target_weight': target_weight
                })

            flash('User Profile Updated', 'success')
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
    email = session.get('email')
    if email:
        form = HistoryForm()
    else:
        return redirect(url_for('home'))
    return render_template('history.html', form=form)


@app.route('/water', methods=['GET', 'POST'])
def water():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))
    intake = request.form.get('intake')
    if request.method == 'POST':
        current_time = datetime.now()
        # Insert the new record
        try:
            intake_int = int(intake)
            mongo.db.intake_collection.insert_one({'intake': intake_int, 'time': current_time, 'email': email})
            flash('Water intake recorded successfully.', 'success')
        except (ValueError, TypeError):
            flash('Invalid intake value. Please enter a number.', 'danger')
            return redirect(url_for('water'))

    # Retrieving records for the logged-in user
    records = mongo.db.intake_collection.find({"email": email}).sort("time", -1)

    # Convert cursor to a list to iterate over it multiple times
    records_list = list(records)
    if records_list:
        average_intake = sum(int(record['intake']) for record in records_list) / len(records_list)
    else:
        average_intake = 0
    # Calculate total intake
    total_intake = sum(int(record['intake']) for record in records_list)

    # Render template with records and total intake
    return render_template('water_intake.html', records=records_list, total_intake=total_intake, average_intake=average_intake)


@app.route('/clear-intake', methods=['POST'])
def clear_intake():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))
    # 清除当前用户的所有水摄入量记录
    mongo.db.intake_collection.delete_many({"email": email})

    flash('All water intake records have been cleared.', 'success')
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
    email = session.get('email')
    print(email)
    if email and request.method == "POST":
        date = request.form.get('date')
        res = mongo.db.calories.find_one({'email': email, 'date': date}, {
                                         'date', 'email', 'calories', 'burnout'})
        if res:
            return json.dumps({'date': res['date'], 'email': res['email'], 'burnout': res['burnout'], 'calories': res['calories']}), 200, {
                'ContentType': 'application/json'}
        else:
            return json.dumps({'date': "", 'email': "", 'burnout': "", 'calories': ""}), 200, {
                'ContentType': 'application/json'}
    return json.dumps({'status': 'Invalid request'}), 400, {'ContentType': 'application/json'}


@app.route("/friends", methods=['GET'])
def friends():
    # ############################
    # friends() function displays the list of friends corresponding to given email
    # route "/friends" will redirect to friends() function which redirects to friends.html page.
    # friends() function will show a list of "My friends", "Add Friends" functionality, "send Request" and "Pending Approvals" functionality
    # Details corresponding to given email address are fetched from the database entries
    # Input: Email
    # Output: My friends, Pending Approvals, Sent Requests and Add new friends
    # ##########################
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    myFriends = list(mongo.db.friends.find(
        {'sender': email, 'accept': True}, {'sender', 'receiver', 'accept'}))
    myFriendsList = [f['receiver'] for f in myFriends]

    print(myFriends)
    allUsers = list(mongo.db.user.find({}, {'name', 'email'}))

    pendingRequests = list(mongo.db.friends.find(
        {'sender': email, 'accept': False}, {'sender', 'receiver', 'accept'}))
    pendingReceivers = [p['receiver'] for p in pendingRequests]

    pendingApproves = []
    pendingApprovals = list(mongo.db.friends.find(
        {'receiver': email, 'accept': False}, {'sender', 'receiver', 'accept'}))
    pendingApproves = [p['sender'] for p in pendingApprovals]

    print(pendingApproves)

    return render_template('friends.html', allUsers=allUsers, pendingRequests=pendingRequests, active=email,
                           pendingReceivers=pendingReceivers, pendingApproves=pendingApproves, myFriends=myFriends, myFriendsList=myFriendsList)


@app.route('/bmi_calc', methods=['GET', 'POST'])
def bmi_calci():
    bmi = ''
    bmi_category = ''

    if request.method == 'POST' and 'weight' in request.form:
        try:
            weight = float(request.form.get('weight'))
            height = float(request.form.get('height'))
            bmi = calc_bmi(weight, height)
            bmi_category = get_bmi_category(bmi)
        except (ValueError, TypeError):
            flash('Invalid input for weight or height. Please enter numeric values.', 'danger')

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


@app.route("/send_email", methods=['GET', 'POST'])
def send_email():
    # ############################
    # send_email() function shares Calorie History with friend's email
    # route "/send_email" will redirect to send_email() function which redirects to friends.html page.
    # Input: Email
    # Output: Calorie History Received on specified email
    # ##########################
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    user = mongo.db.user.find_one({'email': email}, {'name'})
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('friends'))

    data = list(mongo.db.calories.find({'email': email}, {'date', 'email', 'calories', 'burnout'}))
    table = [['Date', 'Email ID', 'Calories', 'Burnout']]
    for a in data:
        tmp = [a['date'], a['email'], a['calories'], a['burnout']]
        table.append(tmp)

    friend_emails = request.form.get('share')
    if not friend_emails:
        flash('Please enter at least one friend email.', 'danger')
        return redirect(url_for('friends'))

    friend_email_list = [e.strip() for e in friend_emails.split(',') if e.strip()]
    if not friend_email_list:
        flash('Please enter valid friend emails.', 'danger')
        return redirect(url_for('friends'))

    # Send email using Flask-Mail
    with mail.connect() as conn:
        for e in friend_email_list:
            msg = Message('Calorie History',
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[e])
            msg.body = f'''Hi,

Your friend {user["name"]} has shared their calorie history with you!

{tabulate(table)}

Best regards,
The Burnout Team
'''
            conn.send(msg)

    flash('Calorie history shared successfully!', 'success')

    # Refresh friends data
    myFriends = list(mongo.db.friends.find(
        {'sender': email, 'accept': True}, {'sender', 'receiver', 'accept'}))
    myFriendsList = [f['receiver'] for f in myFriends]

    allUsers = list(mongo.db.user.find({}, {'name', 'email'}))

    pendingRequests = list(mongo.db.friends.find(
        {'sender': email, 'accept': False}, {'sender', 'receiver', 'accept'}))
    pendingReceivers = [p['receiver'] for p in pendingRequests]

    pendingApproves = []
    pendingApprovals = list(mongo.db.friends.find(
        {'receiver': email, 'accept': False}, {'sender', 'receiver', 'accept'}))
    pendingApproves = [p['sender'] for p in pendingApprovals]

    print(pendingApproves)

    return render_template('friends.html', allUsers=allUsers, pendingRequests=pendingRequests, active=email,
                           pendingReceivers=pendingReceivers, pendingApproves=pendingApproves, myFriends=myFriends, myFriendsList=myFriendsList)


@app.route("/ajaxsendrequest", methods=['POST'])
def ajaxsendrequest():
    # ############################
    # ajaxsendrequest() is a function that updates friend request information into database
    # route "/ajaxsendrequest" will redirect to ajaxsendrequest() function.
    # Details corresponding to given email address are fetched from the database entries and send request details updated
    # Input: Email, receiver
    # Output: DB entry of receiver info into database and return TRUE if success and FALSE otherwise
    # ##########################
    email = session.get('email')
    if email and request.method == 'POST':
        receiver = request.form.get('receiver')
        if receiver:
            if mongo.db.friends.find_one({'sender': email, 'receiver': receiver}):
                return json.dumps({'status': False, 'message': 'Friend request already sent.'}), 400, {
                    'ContentType': 'application/json'}
            res = mongo.db.friends.insert_one(
                {'sender': email, 'receiver': receiver, 'accept': False})
            if res:
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
    email = session.get('email')
    if email and request.method == 'POST':
        receiver = request.form.get('receiver')
        if receiver:
            res = mongo.db.friends.delete_one(
                {'sender': email, 'receiver': receiver})
            if res.deleted_count > 0:
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
    email = session.get('email')
    if email and request.method == 'POST':
        sender = request.form.get('sender')
        if sender:
            res = mongo.db.friends.update_one({'sender': sender, 'receiver': email}, {
                "$set": {'accept': True}})
            # Also insert reciprocal friendship
            mongo.db.friends.insert_one({'sender': email, 'receiver': sender, 'accept': True})
            if res.modified_count > 0:
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
    exercises = [
        {"id": 1, "name": "Yoga"},
        {"id": 2, "name": "Swimming"},
    ]
    return render_template('dashboard.html', title='Dashboard', exercises=exercises)


@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    email = session.get('email')
    if email and request.method == 'POST':
        data = request.get_json()
        exercise_id = data.get('exercise_id')
        action = data.get('action')
        exercise = mongo.db.your_exercise_collection.find_one({"exercise_id": exercise_id})
        print(exercise)
        if exercise:
            if action == "add":
                # Check if already favorited
                existing = mongo.db.favorites.find_one({"email": email, "exercise_id": exercise_id})
                if existing:
                    return jsonify({"status": "already_favorited"}), 200
                # Create a new document in the favorites schema (you can customize this schema)
                favorite = {
                    "exercise_id": exercise.get("exercise_id"),
                    "email": email,
                    "image": exercise.get("image"),
                    "video_link": exercise.get("video_link"),
                    "name": exercise.get("name"),
                    "description": exercise.get("description"),
                    "href": exercise.get("href")
                }

                # Insert the exercise into the favorites collection
                mongo.db.favorites.insert_one(favorite)
                return jsonify({"status": "success"}), 200
            elif action == "remove":
                res = mongo.db.favorites.delete_one({"email": email, "exercise_id": exercise.get("exercise_id")})
                if res.deleted_count > 0:
                    return jsonify({"status": "success"}), 200
                else:
                    return jsonify({"status": "not_found"}), 404
        else:
            return jsonify({"status": "error", "message": "Exercise not found"}), 404

    return jsonify({"status": "failure"}), 400


@app.route('/favorites')
def favorites():
    email = session.get('email')
    if not email:
        # Redirect the user to the login page or show an error message
        return redirect(url_for('login'))

    # Query MongoDB to get the user's favorite exercises
    favorite_exercises = mongo.db.favorites.find({"email": email})

    return render_template('favorites.html', favorite_exercises=favorite_exercises)


# Enrollment Routes
def handle_enrollment(email, enroll):
    """
    Helper function to handle enrollment logic.
    """
    # Check if already enrolled
    existing = mongo.db.user.find_one({'Email': email, 'Status': enroll})
    if existing:
        flash(f'You are already enrolled in the {enroll} plan.', 'info')
        return
    mongo.db.user.insert_one({'Email': email, 'Status': enroll})
    flash(f'You have successfully enrolled in our {enroll} plan!', 'success')


@app.route("/yoga", methods=['GET', 'POST'])
def yoga():
    email = session.get('email')
    if email:
        form = EnrollForm()
        if form.validate_on_submit():
            handle_enrollment(email, "yoga")
            return render_template('new_dashboard.html', form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('yoga.html', title='Yoga', form=form)


@app.route("/headspace", methods=['GET', 'POST'])
def headspace():
    email = session.get('email')
    if email:
        form = EnrollForm()
        if form.validate_on_submit():
            handle_enrollment(email, "headspace")
            return render_template('new_dashboard.html', form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('Headspace.html', title='Headspace', form=form)


@app.route("/mbsr", methods=['GET', 'POST'])
def mbsr():
    email = session.get('email')
    if email:
        form = EnrollForm()
        if form.validate_on_submit():
            handle_enrollment(email, "mbsr")
            return render_template('new_dashboard.html', form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('mbsr.html', title='mbsr', form=form)


@app.route("/swim", methods=['GET', 'POST'])
def swim():
    email = session.get('email')
    if email:
        form = EnrollForm()
        if form.validate_on_submit():
            handle_enrollment(email, "swimming")
            return render_template('new_dashboard.html', form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('swim.html', title='Swim', form=form)


@app.route("/abbs", methods=['GET', 'POST'])
def abbs():
    email = session.get('email')
    if email:
        form = EnrollForm()
        if form.validate_on_submit():
            handle_enrollment(email, "abbs")
            return render_template('new_dashboard.html', form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('abbs.html', title='Abbs Smash!', form=form)


@app.route("/belly", methods=['GET', 'POST'])
def belly():
    email = session.get('email')
    if email:
        form = EnrollForm()
        if form.validate_on_submit():
            handle_enrollment(email, "belly")
            return render_template('new_dashboard.html', form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('belly.html', title='Belly Burner', form=form)


@app.route("/core", methods=['GET', 'POST'])
def core():
    email = session.get('email')
    if email:
        form = EnrollForm()
        if form.validate_on_submit():
            handle_enrollment(email, "core")
            return render_template('new_dashboard.html', form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('core.html', title='Core Conditioning', form=form)


@app.route("/gym", methods=['GET', 'POST'])
def gym():
    email = session.get('email')
    if email:
        form = EnrollForm()
        if form.validate_on_submit():
            handle_enrollment(email, "gym")
            return render_template('new_dashboard.html', form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('gym.html', title='Gym', form=form)


@app.route("/walk", methods=['GET', 'POST'])
def walk():
    email = session.get('email')
    if email:
        form = EnrollForm()
        if form.validate_on_submit():
            handle_enrollment(email, "walk")
            return render_template('new_dashboard.html', form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('walk.html', title='Walk', form=form)


@app.route("/dance", methods=['GET', 'POST'])
def dance():
    email = session.get('email')
    if email:
        form = EnrollForm()
        if form.validate_on_submit():
            handle_enrollment(email, "dance")
            return render_template('new_dashboard.html', form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('dance.html', title='Dance', form=form)


@app.route("/hrx", methods=['GET', 'POST'])
def hrx():
    email = session.get('email')
    if email:
        form = EnrollForm()
        if form.validate_on_submit():
            handle_enrollment(email, "hrx")
            return render_template('new_dashboard.html', form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('hrx.html', title='HRX', form=form)


@app.route("/review", methods=['GET', 'POST'])
def submit_reviews():
    # ############################
    # submit_reviews() function collects and displays the reviews submitted by different users
    # route "/review" will redirect to submit_review() function which redirects to review.html page.
    # Reviews are stored into a MongoDB collection and then retrieved immediately
    # Input: Email
    # Output: Name, Review
    # ##########################
    existing_reviews = mongo.db.reviews.find()
    if session.get('email'):
        print("Imhere2")
        if request.method == 'POST':  # Check if it's a POST request
            form = ReviewForm(request.form)  # Initialize the form with form data
            if form.validate_on_submit():
                print("imehere1")
                email = session.get('email')
                user = mongo.db.user.find_one({'email': email})
                name = form.name.data
                review = form.review.data  # Correct the field name
                mongo.db.reviews.insert_one({'name': name, 'review': review})
                flash('Your review has been submitted!', 'success')
                return redirect(url_for('submit_reviews'))
        else:
            form = ReviewForm()  # Create an empty form for GET requests
        return render_template('review.html', form=form, existing_reviews=existing_reviews)
    else:
        flash('Please log in to submit a review.', 'danger')
        return redirect(url_for('login'))


@app.route('/blog')
def blog():
    # 处理 "blog" 页面的逻辑
    return render_template('blog.html')

@app.route('/test_flash')
def test_flash():
    flash('This is a test flash message!', 'info')
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)
