import logging

import requests
from flask import (Blueprint, current_app, json, redirect, request, session, url_for)
LOGGER = logging.getLogger(__name__)


def get_google_provider_cfg():
    '''
    get the google oauth provider url
    '''
    return requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()


bp = Blueprint('auth', __name__, url_prefix='')


@bp.route("/google-login")
def google_login():
    '''
    provides sign in with google
    '''
    # get the url to hit for google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # construct request for google login and specify the fields on the account
    # we want
    request_uri = current_app.oauthclient.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=current_app.config['GOOGLE_SIGN_IN_REDIRECT_URI'],
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@bp.route("/login/callback")
def google_loign_callback():
    '''
    handle callback data from google oauth and login user
    '''
    # Get authorization code from url returned by google
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = current_app.oauthclient.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config['GOOGLE_CLIENT_ID'],
              current_app.config['GOOGLE_CLIENT_SECRET'],
              ),
    )


    current_app.oauthclient.parse_request_body_response(
        json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = current_app.oauthclient.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        user_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        username = userinfo_response.json()["given_name"]

        user_from_db = current_app.mongo.db.user.find_one({'email': user_email})
        if user_from_db is None:
            # create new profile for the user it does not exists.
            current_app.mongo.db.user.insert_one({
                'name': username,
                'email': user_email,
                'pwd': '',
            })
            session['email'] = user_email
            session['name'] = username
            LOGGER.info("new user created")
        else:
            # user already exists, set session info to log them in
            session['email'] = user_from_db['email']
            session['name'] = user_from_db['name']
            LOGGER.info("user already existed")

        return redirect(url_for('dashboard'))

    else:
        LOGGER.info("email not verified")
        return "User email not available or not verified by Google.", 400
