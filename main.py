"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
import json

import flask
import httplib2

import uuid


from apiclient import discovery
from oauth2client import client

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
app = flask.Flask(__name__)
app.secret_key = str(uuid.uuid4())

@app.route('/')
def index():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        drive_service = discovery.build('drive', 'v2', http_auth)
        files = drive_service.files().list().execute()
        return json.dumps(files)


@app.route('/oauth2callback')
def oauth2callback():
    flow = client.flow_from_clientsecrets(
                                          'client_secret.json',
                                          scope='https://www.googleapis.com/auth/drive.metadata.readonly',
                                          redirect_uri=flask.url_for('oauth2callback', _external=True),
                                          )
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
    return flask.redirect(flask.url_for('index'))




 


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
