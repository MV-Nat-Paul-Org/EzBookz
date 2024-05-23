from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Initialize extensions
db = SQLAlchemy()
cors = CORS()

def create_app():
    
    # Load environment variables
    load_dotenv()
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY')
    app.config['AUTH0_CLIENT_ID'] = os.getenv('AUTH0_CLIENT_ID')
    app.config['AUTH0_CLIENT_SECRET'] = os.getenv('AUTH0_CLIENT_SECRET')
    app.config['AUTH0_DOMAIN'] = os.getenv('AUTH0_DOMAIN')
    app.config['AUTH0_CALLBACK_URL'] = os.getenv('AUTH0_CALLBACK_URL')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    
    # Initialize extensions
    db.init_app(app)
    cors.init_app(app)
    
    return app
