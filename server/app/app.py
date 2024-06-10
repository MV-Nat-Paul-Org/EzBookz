import os
from . import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 3000)))








































################# Working AUTH0 ######################


# from flask import Flask, request, jsonify, render_template, session, redirect, url_for, g
# from extensions import db
# from models import User, Appointment
# from flask_caching import Cache
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from authlib.integrations.flask_client import OAuth
# import os
# import requests

# # def login_required(f):
# #     @wraps(f)
# #     def decorated_function(*args, **kwargs):
# #         if 'user' not in session:
# #             return redirect(url_for('login'))
# #         return f(*args, **kwargs)
# #     return decorated_function

# load_dotenv()

# def create_app():
#     app = Flask(__name__)
#     app.secret_key = os.getenv("APP_SECRET_KEY")
#     oauth = OAuth(app)
#     cache = Cache(app, config={'CACHE_TYPE': 'simple'})  # Configure cache

#     oauth.register(
#         "auth0",
#         client_id=os.getenv("AUTH0_CLIENT_ID"),
#         client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
#         client_kwargs={"scope": "openid profile email"},
#         server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration'
#     )
    

#     @app.before_request
#     def load_logged_in_user():
#         user = session.get('user')
        
#         if user is None:
#             g.user = None
#         else:
#             g.user = user    

#     @app.route("/")
#     def home():
#         return render_template("home.html", session=session.get('user'))

#     @app.route("/login")
#     def login():
#         return oauth.auth0.authorize_redirect(
#             redirect_uri=url_for("callback", _external=True)
#             )

#     @app.route("/callback", methods=["GET", "POST"])
#     def callback():
#         token = oauth.auth0.authorize_access_token()
#         session["user"] = token
#         return redirect("/")

#     @app.route("/logout")
#     def logout():
#         session.clear()
#         return redirect("/")

#     @app.route("/book-appointment", methods=['POST'])
#     @cross_origin()
#     def book_appointment():
#         if not session.get('user'):
#             return jsonify({'message': 'Please log in'}), 401
#         data = request.get_json()
#         appointment = Appointment.query.filter_by(id=data['appointment_id']).first()
#         if appointment and appointment.available:
#             appointment.user_id = session['user']['id']
#             appointment.available = False
#             db.session.commit()
#             return jsonify({'message': 'Appointment booked'}), 200
#         return jsonify({'message': 'This slot is no longer available'}), 400

#     @app.route("/appointments")
#     # @login_required
#     def get_appointments():
#         try:
#             if is_Admin():
#                 appointments = Appointment.query.all()
#                 return render_template("all-appointments.html", appointments=appointments)
#             else:
#                 appointments = Appointment.query.filter_by(available=True).all()
#                 return render_template("available-appointments.html", appointments=appointments)
#         except Exception as e:
#             app.logger.error(f"Error fetching appointments: {e}")
#             return jsonify({"error": "Unable to fetch appointments"}), 500
        
#     @app.route("/admin")
#     def admin():
#         if 'user' in session and is_Admin():
#             appointments = Appointment.query.all()
#             return jsonify([{'id': appt.id, 'start_time': appt.start_time, 'end_time': appt.end_time, 'available': appt.available, 'user_id': appt.user_id} for appt in appointments])
#         return jsonify({"message": "Unauthorized"}), 403

#     @cache.memoize(timeout=300)
#     def get_admin_users():
#         token_url = f'https://{os.getenv("AUTH0_DOMAIN")}/api/v2/roles/{os.getenv("ROLE_ID")}/users'
#         token_payload = {
#             'client_id': os.getenv("AUTH0_CLIENT_ID"),
#             'client_secret': os.getenv("AUTH0_CLIENT_SECRET"),
#             'audience': os.getenv("AUDIENCE"),
#             'grant_type': 'client_credentials'
#         }
#         token_response = requests.post(token_url, json=token_payload)
#         token_data = token_response.json()
#         access_token = token_data['access_token']

#         users_url = f'https://{os.getenv("AUTH0_DOMAIN")}/api/v2/roles/{os.getenv("ROLE_ID")}/users'
#         headers = {
#             'Authorization': f'Bearer {access_token}',
#             'Content-Type': 'application/json'
#         }
#         admin_users_response = requests.get(users_url, headers=headers)
#         admin_users_data = admin_users_response.json()
#         return [user['email'] for user in admin_users_data]

#     def is_Admin():
#         user_email = g.user['userinfo']['email'] if g.user and 'userinfo' in g.user else None
#         admin_users = get_admin_users()
#         return user_email in admin_users

#     return app

# if __name__ == "__main__":
#     app = create_app()
#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 3000)))