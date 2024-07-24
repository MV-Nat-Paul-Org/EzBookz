import os
from dotenv import load_dotenv
from app.models import Appointment, User
from app import create_app
from . import db
from datetime import datetime, timedelta

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

def seed_database():
    # Ensure the necessary environment variable is available
    db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    if not db_uri:
        raise EnvironmentError("SQLALCHEMY_DATABASE_URI is not set in environment variables")

    print("Database URI in seed.py:", db_uri)
    print("Absolute path to database:", os.path.abspath(os.path.join('instance', 'mydatabase.db')))

    app = create_app()
    with app.app_context():
        try:
            # Check if the database is already seeded
            if Appointment.query.first() is not None:
                print("Database already seeded. No changes made.")
                return

            db.session.query(Appointment).delete()  # Clear existing data, if any
            db.session.query(User).delete()  # Clear existing data, if any
            
            # Add new sample data
            user1 = User(auth0_id="auth0|example1", name="John Doe", email="john@example.com")
            user2 = User(auth0_id="auth0|example2", name="Jane Smith", email="jane@example.com")
            db.session.add(user1)
            db.session.add(user2)

            today = datetime.now()
            appointments = [
                Appointment(title="Consultation", start_time=today + timedelta(days=1, hours=10), end_time=today + timedelta(days=1, hours=11), user_id=user1.id, type="available"),
                Appointment(title="Follow-up", start_time=today + timedelta(days=2, hours=14), end_time=today + timedelta(days=2, hours=15), user_id=user2.id, type="unavailable"),
                Appointment(title="Routine Check", start_time=today + timedelta(days=3, hours=9), end_time=today + timedelta(days=3, hours=10), user_id=user1.id, type="available"),
                Appointment(title="Emergency", start_time=today + timedelta(days=4, hours=13), end_time=today + timedelta(days=4, hours=14), user_id=user2.id, type="unavailable"),
                Appointment(title="Dental Checkup", start_time=today + timedelta(days=5, hours=8), end_time=today + timedelta(days=5, hours=9), user_id=user1.id, type="available"),
                Appointment(title="Therapy Session", start_time=today + timedelta(days=6, hours=16), end_time=today + timedelta(days=6, hours=17), user_id=user2.id, type="unavailable")
            ]
            db.session.add_all(appointments)
            db.session.commit()
            print("Database successfully seeded.")
        except Exception as e:
            print(f"An error occurred while seeding the database: {e}")

if __name__ == '__main__':
    seed_database()