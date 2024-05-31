# routes and endpoints
from flask import Flask, request, jsonify, redirect, render_template, session, url_for, g
from config import app, db  # added space after comma
import requests
# import modules: from models import <Model>
from models import User, Appointment
from os import environ as env
from dotenv import find_dotenv, load_dotenv
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from flask_cors import cross_origin
from functools import wraps

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")
oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    # When logged out redirect to home screen to promp login again
    return redirect("/")

@app.before_request
def load_logged_in_user():
    user = session.get('user')

    if user is None:
        g.user = None
    else:
        g.user = user

# Check if user is an Admin
def is_Admin():
     # get token
        token_url = f'https://{env.get("AUTH0_DOMAIN")}/oauth/token'
        token_payload = {
            'client_id': env.get("AUTH0_CLIENT_ID"),
            'client_secret': env.get("AUTH0_CLIENT_SECRET"),
            'audience': env.get("AUDIENCE"),
            'grant_type': 'client_credentials'
        }
        token_response = requests.post(token_url, json=token_payload)
        token_data = token_response.json()
        access_token = token_data['access_token']

        # get users for the admin role
        users_url = f'https://{env.get("AUTH0_DOMAIN")}/api/v2/roles/{env.get("ROLE_ID")}/users'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        admin_users_response = requests.get(users_url, headers=headers)
        admin_users_data = admin_users_response.json()

        # Get current users email
        user_email = g.get('user')['userinfo']['email']

        for user in admin_users_data:
            if user.get('email') == user_email:
                return True
        return False

@app.route("/")
def home():
    # if g.user:
    #   userToShow = g.get('user')['userinfo']['name']
    #   return f"<h1>Hello {userToShow}, to view appointments go to /appointments</h1>"
    # else:
    #   return f"<h1>Please login at /login</h1>"
    return render_template("home.html", session=session.get('user'))

    
@app.route("/admin")
def get_admin():
    if g.user: 
        return jsonify({"message": is_Admin()})
    else:
        return jsonify({"message": "Please log in"})
    

################ ORIGINAL /APPOINTMENTS ROUTE ################
# @app.route("/appointments")
# def get_appointments():
#     if g.user: 
#         # Run function to check if user is admin to display correct appointments
#         if is_Admin():
#             return render_template("all-appointments.html", session=session.get('user'))
#         else:
#             return render_template("available-appointments.html", session=session.get('user'))
#     else:
#         return render_template("home.html", session=session.get('user'))
############################################################

@app.route("/appointments", methods=["GET"])
def get_appointments():
    if g.user:
        if is_Admin():
            appointments = Appointment.query.all()
            return render_template("all-appointments.html", appointments=appointments, session=session.get('user'))
        else:
            appointments = Appointment.query.filter_by(available=True).all()
            return render_template("available-appointments.html", appointments=appointments, session=session.get('user'))
    else:
        return render_template("home.html", session=session.get('user'))

@app.route("/appointments", methods=["POST"])
def create_appointment():
    if g.user and is_Admin():
        try:
            data = request.get_json()
            new_appointment = Appointment(**data)
            db.session.add(new_appointment)
            db.session.commit()
            return redirect(url_for('get_appointments'))
        except Exception as e:
            return str(e), 400
    else:
        return render_template("home.html", session=session.get('user'))

@app.route("/appointments/<int:appointment_id>", methods=["GET"])
def get_appointment(appointment_id):
    if g.user:
        appointment = Appointment.query.get(appointment_id)
        if appointment:
            return render_template("appointment.html", appointment=appointment, session=session.get('user'))
        else:
            return "Appointment not found", 404
    else:
        return render_template("home.html", session=session.get('user'))

@app.route("/appointments/<int:appointment_id>", methods=["PUT"])
def update_appointment(appointment_id):
    if g.user and is_Admin():
        appointment = Appointment.query.get(appointment_id)
        if appointment:
            try:
                data = request.get_json()
                for key, value in data.items():
                    setattr(appointment, key, value)
                db.session.commit()
                return redirect(url_for('get_appointments'))
            except Exception as e:
                return str(e), 400
        else:
            return "Appointment not found", 404
    else:
        return render_template("home.html", session=session.get('user'))

@app.route("/appointments/<int:appointment_id>", methods=["DELETE"])
def delete_appointment(appointment_id):
    if g.user and is_Admin():
        appointment = Appointment.query.get(appointment_id)
        if appointment:
            db.session.delete(appointment)
            db.session.commit()
            return redirect(url_for('get_appointments'))
        else:
            return "Appointment not found", 404
    else:
        return render_template("home.html", session=session.get('user'))

@app.route("/appointments/<int:appointment_id>/book", methods=["POST"])
def book_appointment(appointment_id):
    if g.user:
        appointment = Appointment.query.get(appointment_id)
        if appointment and appointment.available:
            appointment.available = False
            db.session.commit()
            return redirect(url_for('get_appointments'))
        else:
            return "Appointment not available", 400
    else:
        return render_template("home.html", session=session.get('user'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))