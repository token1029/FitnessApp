import pytest
from fitnessapp import create_app
from unittest.mock import patch, MagicMock
import mongomock

class OAuth:
    def prepare_token_request(grant_type, body='', include_client_id=True, code_verifier=None, **kwargs):
        # Your function logic
        return (
            "something to do ",  # Return the original token endpoint
            {"Content-Type": "application/x-www-form-urlencoded"},  # Headers
            f"code=4223"  # Body of the request
        )

    def parse_request_body_response(a, b):
        pass

    def add_token(a, b):
        return ('uri', {'headers': 'value'}, "body")

    def prepare_request_uri(self, uri, redirect_uri=None, scope=None,
                            state=None, code_challenge=None, code_challenge_method='plain', **kwargs):
        return "/"


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    oauthclient = OAuth()
    # oauthclient['prepare_token_request'] = prepare_token_request
    app.oauthclient = oauthclient
    app.mongo = mongomock.MongoClient()
    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
