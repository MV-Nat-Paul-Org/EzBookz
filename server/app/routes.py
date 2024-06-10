import os
import json
import requests 
from datetime import datetime
from urllib.parse import urlencode, quote_plus
from flask import Flask, redirect, render_template, session, url_for, Blueprint, request, jsonify
from . import oauth
from . import db
from .models import User, Appointment


# Create a Blueprint
api = Blueprint('api', __name__)

def is_logged_in():
    '''Check if the user is logged in.'''
    return 'user' in session

def get_user_info_from_auth0(token):
    """Retrieve user info from Auth0's User Info endpoint."""
    auth_header = {'Authorization': f'Bearer {token}'}
    auth0_domain = os.getenv('AUTH0_DOMAIN')
    user_info_url = f"{auth0_domain}/userinfo"  # Correct endpoint for Auth0 User Info
    response = requests.get(user_info_url, headers=auth_header)
    return response.json()

@api.route('/')
def home():
    # return "Welcome to the Appointment System!"
    return render_template("home.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@api.route("/login")
def login():
    try:
        # Build the redirect URI dynamically
        redirect_uri = url_for("api.callback", _external=True)
        return oauth.auth0.authorize_redirect(redirect_uri=redirect_uri)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
    
@api.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/") 
    
@api.route("/logout")
def logout():
    session.clear()
    # When logged out redirect to home screen to promp login again
    return redirect("/")
    
@api.route('/users', methods=['GET'])
def get_users():
    if not is_logged_in():
        return jsonify({'message': 'Please log in'}), 401
    users = User.query.all()
    return jsonify([{'id': u.id, 'name': u.name, 'email': u.email, 'role': u.role} for u in users])

@api.route('/users', methods=['POST'])
def create_user():
    # Assuming the user is logged in through Auth0 and you have the token
    if not is_logged_in():
        return jsonify({'message': 'Please log in'}), 401
    
    data = request.get_json()
    
    # Check if the user already exists in the database
    existing_user = User.query.filter_by(auth0_id=data['auth0_id']).first()
    if existing_user:
        return jsonify({'message': 'User already exists'}), 409

    if not data or not data.get('auth0_id') or not data.get('name') or not data.get('email'):
        return jsonify({'message': 'Missing data'}), 400
    
    new_user = User(auth0_id=data['auth0_id'], name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201

@api.route('/appointments', methods=['GET'])
def get_appointments():
    if not is_logged_in():
        return jsonify({'message': 'Please log in'}), 401
    appointments = Appointment.query.all()
    return jsonify([{'id': a.id, 'title': a.title, 'start_time': a.start_time, 'end_time': a.end_time, 'user_id': a.user_id, 'type': a.type} for a in appointments])

@api.route('/appointments/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    if not is_logged_in():
        return jsonify({'message': 'Please log in'}), 401
    appointment = Appointment.query.get_or_404(appointment_id)
    return jsonify({
        'id': appointment.id,
        'title': appointment.title,
        'start_time': appointment.start_time.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        'end_time': appointment.end_time.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        'user_id': appointment.user_id,
        'type': appointment.type
    }), 200

@api.route('/appointments', methods=['POST'])
def create_appointment():
    if not is_logged_in():
        return jsonify({'message': 'Please log in'}), 401
    data = request.get_json()
    try:
        if not data or not data.get('title') or not data.get('start_time') or not data.get('end_time'):
            return jsonify({'message': 'Missing data'}), 400

        # Convert start_time and end_time from string to datetime
        start_time = datetime.strptime(data['start_time'], "%a, %d %b %Y %H:%M:%S GMT")
        end_time = datetime.strptime(data['end_time'], "%a, %d %b %Y %H:%M:%S GMT")

        new_appointment = Appointment(
            title=data['title'],
            start_time=start_time,
            end_time=end_time,
            user_id=data.get('user_id'),
            type=data['type']
        )
        db.session.add(new_appointment)
        db.session.commit()
        return jsonify({'message': 'Appointment created'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/appointments/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    if not is_logged_in():
        return jsonify({'message': 'Please log in'}), 401
    appointment = Appointment.query.get_or_404(appointment_id)
    data = request.get_json()
    try:
        if 'title' in data:
            appointment.title = data['title']
        if 'start_time' in data:
            appointment.start_time = datetime.strptime(data['start_time'], "%a, %d %b %Y %H:%M:%S GMT")
        if 'end_time' in data:
            appointment.end_time = datetime.strptime(data['end_time'], "%a, %d %b %Y %H:%M:%S GMT")
        if 'user_id' in data:
            appointment.user_id = data['user_id']
        if 'type' in data:
            appointment.type = data['type']
            
        db.session.commit()
        return jsonify({'message': 'Appointment updated'}), 200
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': 'Invalid datetime format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    if not is_logged_in():
        return jsonify({'message': 'Please log in'}), 401
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment deleted'}), 200