# config.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth

db = SQLAlchemy()
oauth = OAuth()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = env.get("APP_SECRET_KEY")
    db.init_app(app)
    oauth.init_app(app)
    return app