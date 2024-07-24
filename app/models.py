from datetime import datetime, timedelta
from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auth0_id = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    @classmethod
    def find_or_create(cls, auth0_id):
        """
        Find or create a user based on their Auth0 ID.
        """
        user = cls.query.filter_by(auth0_id=auth0_id).first()
        if not user:
            user = cls(auth0_id=auth0_id)
            db.session.add(user)
            db.session.commit()
        return user

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('appointments', lazy=True))
    type = db.Column(db.String(50), nullable=False, default='available')
    
    @staticmethod
    def generate_available_slots(start_date, end_date, interval_minutes):
        """
        Generate available appointment slots within a given date range
        with the specified time interval, considering office hours,
        lunch breaks, and weekend closures.
        """
        slots = []
        current_time = start_date

        # Define office hours and lunch break time ranges
        office_hours_start = datetime.combine(start_date.date(), datetime.min.time()) + timedelta(hours=9)
        office_hours_end = datetime.combine(start_date.date(), datetime.min.time()) + timedelta(hours=17)
        lunch_start = datetime.combine(start_date.date(), datetime.min.time()) + timedelta(hours=12)
        lunch_end = datetime.combine(start_date.date(), datetime.min.time()) + timedelta(hours=13)

        # Generate slots for each day within the date range
        while current_time < end_date:
            # Skip weekends
            if current_time.weekday() >= 5:  # Saturday or Sunday
                current_time += timedelta(days=1)
                continue

            # Skip lunch break
            if lunch_start <= current_time < lunch_end:
                current_time = lunch_end
                continue

            # Check if within office hours
            if office_hours_start <= current_time < office_hours_end:
                slots.append(current_time)

            current_time += timedelta(minutes=interval_minutes)

        return slots