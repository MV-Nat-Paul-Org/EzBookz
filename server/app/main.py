# routes and endpoints
from flask import Flask, request, jsonify, redirect, render_template, session, url_for
from config import app, db  # added space after comma
# import modules: from models import <Model>
from models import User, Appointment
from os import environ as env
from dotenv import find_dotenv, load_dotenv
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
import json
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

# Decorators (checks if the user is logged in before allowing them to access the route)
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            # No user is logged in
            abort(401)  # Unauthorized
        return f(*args, **kwargs)
    return decorated


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
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

# @app.route("/callback", methods=["GET", "POST"])
# def callback():
#     try:
#         #Retrieve access token
#         token = oauth.auth0.authorize_access_token()
        
#         #Retrieve user information
#         resp = oauth.auth0.get('userinfo')
#         userinfo = resp.json() 
        
#         #Check if user exists in database 
#         user = User.query.filter_by(auth0_user_id=userinfo['sub']).first()
    
#         #If user does not exist, add user to database
#         if user is None:
#             user = User(
#                 auth0_user_id=userinfo['sub'],
#                 name=userinfo['name'],
#                 email=userinfo['email']
#             )
#             db.session.add(user)
#             db.session.commit() 
        
#         # Save the user information in the session
#         session['jwt_payload'] = userinfo
#         session['profile'] = {
#             'user_id': user.id,
#             'name': userinfo['name'],
#             'email': userinfo['email'],
#             'picture': userinfo['picture']
#         }
#         return redirect('/')
#     except Exception as e:
#         print(e)
#         return redirect('/Error')
        
# @app.route("/api/slots", methods=["GET"])
@requires_auth
def get_slots():
        slots = Appointment.query.filter_by(available=True).all()
        return jsonify([slot.serialize() for slot in slots])


@app.route("/api/slots/<int:slot_id>/book", methods=["POST"])
@requires_auth
def book_slot(slot_id):
    slot = Appointment.query.get(slot_id)
    if slot is None or not slot.available:
        abort(404, description="Slot not found or not available")
    slot.available = False
    slot.user_id = session['profile']['user_id']
    db.session.commit()
    return jsonify(slot.serialize())

@app.route("/api/slots/<int:slot_id>/cancel", methods=["POST"])
@requires_auth
def cancel_slot(slot_id):
    slot = Appointment.query.get(slot_id)
    if slot is None or slot.available or slot.user_id != session['profile']['user_id']:
        abort(404, description="Slot not found, not booked, or not booked by this user")
    slot.available = True
    slot.user_id = None
    db.session.commit()
    return jsonify(slot.serialize())

@app.route("/api/slots/<int:slot_id>/open", methods=["POST"])
@requires_auth
def open_slot(slot_id):
    try:
        token_info = oauth.auth0.parse_id_token(oauth.auth0.token)
        user_role = token_info['https://example.com/role']
    except TokenError:
        abort(403, description="Invalid token")

    if user_role != 'admin':
        abort(403, description="Only admins can open slots")

    slot = Appointment.query.get(slot_id)
    if slot is None or slot.available:
        abort(404, description="Slot not found or already available")
    slot.available = True
    slot.user_id = None
    db.session.commit()
    return jsonify(slot.serialize())

# This doesn't need authentication
@app.route("/api/public")
@cross_origin(headers=["Content-Type", "Authorization"])
def public():
    response = "Hello from a public endpoint! You don't need to be authenticated to see this."
    return jsonify(message=response)

# This needs authentication
@app.route("/api/private")
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def private():
    response = "Hello from a private endpoint! You need to be authenticated to see this."
    return jsonify(message=response)

# This needs authorization
@app.route("/api/private-scoped")
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def private_scoped():
    if requires_scope("read:messages"):
        response = "Hello from a private endpoint! You need to be authenticated and have a scope of read:messages to see this."
        return jsonify(message=response)
    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))