# /server.py

import json
from six.moves.urllib.request import urlopen
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import cross_origin
from jose import jwt

AUTH0_DOMAIN = 'dev-ygc148tx5f5zikll.us.auth0.com'
API_AUDIENCE = 'https://ezbookz.com/api'
ALGORITHMS = ["RS256"]

APP = Flask(__name__)

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

