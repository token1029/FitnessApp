import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from bson import ObjectId
from dotenv import load_dotenv
import bcrypt
import smtplib
from flask import json, jsonify, Flask
from flask import render_template, session, url_for, flash, redirect, request, Flask
from flask_mail import Mail, Message
from flask_pymongo import PyMongo
from tabulate import tabulate
from .forms import HistoryForm, RegistrationForm, LoginForm, CalorieForm, UserProfileForm, EnrollForm, ReviewForm
from .insert_db_data import insertfooddata, insertexercisedata
import schedule
from threading import Thread
from flask import Flask
from oauthlib.oauth2 import WebApplicationClient


def create_app(test_config=None):
    # create and configure the app
    load_dotenv()
    app = Flask(__name__, template_folder='templates')
    app.secret_key = 'secret'
    app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/test'
    app.config['MONGO_CONNECT'] = False
    mongo = PyMongo(app)
    app.mongo = mongo

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = "burnoutapp2023@gmail.com"
    app.config['MAIL_PASSWORD'] = "jgny mtda gguq shnw"

    app.config['GOOGLE_CLIENT_ID'] = os.environ.get("GOOGLE_CLIENT_ID", None)
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get("GOOGLE_CLIENT_SECRET", None)
    app.config['GOOGLE_DISCOVERY_URL'] = os.environ.get("GOOGLE_DISCOVERY_URL", None)
    app.config['GOOGLE_SIGN_IN_REDIRECT_URI'] = os.environ.get("GOOGLE_SIGN_IN_REDIRECT_URI", None)



    mail = Mail(app)

    oauthclient = WebApplicationClient(app.config['GOOGLE_CLIENT_ID'])
    app.oauthclient = oauthclient

    from .insert_db_data import insertexercisedata, insertfooddata
    insertfooddata()
    insertexercisedata()

    from . import application
    app.register_blueprint(application.bp)
    return app
