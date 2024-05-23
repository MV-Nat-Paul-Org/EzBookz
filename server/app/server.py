# /server.py

import json
from six.moves.urllib.request import urlopen
from functools import wraps

from flask import request, jsonify
from flask_cors import cross_origin
from jose import jwt

from main import app as APP  # import the Flask app from main.py

AUTH0_DOMAIN = 'dev-ygc148tx5f5zikll.us.auth0.com'
API_AUDIENCE = 'https://ezbookz.com/api'
ALGORITHMS = ["RS256"]

# Error handler
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

@APP.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

@APP.route('/')
def home():
    return "Hello, World!"

if __name__ == '__main__':
    APP.run(debug=True)