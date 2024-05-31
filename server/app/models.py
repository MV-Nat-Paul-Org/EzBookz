# Create Appointment Model here
# Create Appointment Model here
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auth0_user_id = db.Column(db.String(256), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    available = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('appointments', lazy=True))

