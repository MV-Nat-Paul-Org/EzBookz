from flask import Flask
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_session import Session
import os

# Initialize the SQLAlchemy ORM
db = SQLAlchemy()
oauth = OAuth()
sess = Session()  # Session manager initialization

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    # Adjust the path to point to the .env file in the server directory
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)
    

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY', 'default_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_TYPE'] = 'filesystem'  # Configure session type


    # Initialize plugins
    db.init_app(app)
    
    # Initialize OAuth library
    oauth.init_app(app)
    
    sess.init_app(app)  # Initialize session

    # Auth0 configuration
    oauth.register(
        'auth0',
        client_id=os.getenv('AUTH0_CLIENT_ID'),
        client_secret=os.getenv('AUTH0_CLIENT_SECRET'),
        client_kwargs={
            'scope': 'openid profile email'
        },
        server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration'
    )
    
    # Specify the migrations directory when initializing Flask-Migrate
    migrate = Migrate(app, db, directory=os.path.join(os.path.dirname(__file__), 'migrations'))

    # Register the routes from routes.py
    from .routes import init_routes, setup_before_request_handlers
    setup_before_request_handlers(app)
    init_routes(app)

    return app