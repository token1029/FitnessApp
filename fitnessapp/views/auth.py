import smtplib
import time
import logging
from threading import Thread

import requests
import schedule
from flask import (Blueprint, Flask, current_app, flash, json, jsonify,
                   redirect, render_template, request, session, url_for)
from flask_mail import Mail, Message
from flask_pymongo import PyMongo
from tabulate import tabulate
LOGGER = logging.getLogger(__name__)

def get_google_provider_cfg():
    return requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()


bp = Blueprint('auth', __name__, url_prefix='')


@bp.route("/google-login")
def google_login():
    # get the url to hit for google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # construct request for google login and specify the fields on the account we want
    request_uri = current_app.oauthclient.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=current_app.config['GOOGLE_SIGN_IN_REDIRECT_URI'],
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@bp.route("/login/callback")
def google_loign_callback():
    # Get authorization code from url returned by google
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # return "User email not available or not verified by Google.", 400
    LOGGER.info(request.url)
    token_url, headers, body = current_app.oauthclient.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    # return "User email not available or not verified by Google.", 400
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config['GOOGLE_CLIENT_ID'],
              current_app.config['GOOGLE_CLIENT_SECRET'],
              ),
    )


    # parse the tokens

    current_app.oauthclient.parse_request_body_response(json.dumps(token_response.json()))


    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = current_app.oauthclient.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        user_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        username = userinfo_response.json()["given_name"]

        user_from_db = current_app.mongo.db.user.find_one({'email': user_email})
        LOGGER.info(user_from_db)
        if user_from_db is None:
            # create new profile for the user it does not exists.
            current_app.mongo.db.user.insert({
                'name': username,
                'email': user_email,
                'pwd': '',
            })
            session['email'] = user_email
            session['name'] = username
        else:
            # user already exists, set session info to log them in
            session['email'] = user_from_db['email']
            session['name'] = user_from_db['name']

        return redirect(url_for('dashboard'))

    else:
        return "User email not available or not verified by Google.", 400
