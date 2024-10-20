import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from bson import ObjectId
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


def create_app(test_config=None):
    # create and configure the app
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
    mail = Mail(app)

    from .insert_db_data import insertexercisedata, insertfooddata
    insertfooddata()
    insertexercisedata()

    from . import application
    app.register_blueprint(application.bp)
    return app
