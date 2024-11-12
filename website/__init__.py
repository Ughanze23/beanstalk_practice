from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import LoginManager
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")


db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    load_dotenv()
    """Create Flask application"""
    application = Flask(__name__)
    application.config["SECRET_KEY"] = "Hash-session-data"
    application.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    
    #DB_USER = os.environ.get("DB_USER")
    #DB_PASSWORD = os.environ.get("DB_PASSWORD")
    #DB_HOST = os.environ.get("DB_HOST")
    #DB_NAME = os.environ.get("DB_NAME")
    
    #application.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    
    # init database
    db.init_app(application)

    from .views import views
    from .auth import auth
    from .models import User, Glossary

    # register blueprints
    application.register_blueprint(views, url_prefix="/")
    application.register_blueprint(auth, url_prefix="/")

    # Create database and tables
    create_database(application)

    # Add roles and admin user
    create_roles(application)
    create_admin(application)
    
    # Configure login manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(application)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return application

def create_database(application):
    if not path.exists('website/' + DB_NAME):
        with application.app_context():
            db.create_all()
            logging.info("Database created successfully")
    else:
        logging.info("db exists already")

def create_roles(application):
    """Insert roles into the Role table only if they don't already exist."""
    from .models import Role

    with application.app_context():
        roles = [
            {"id": 1, "role_name": "admin"},
            {"id": 2, "role_name": "editor"},
            {"id": 3, "role_name": "viewer"},
        ]

        for role_data in roles:
            # Check if role already exists
            role = Role.query.filter_by(role_name=role_data["role_name"]).first()

            if not role:
                # If role doesn't exist, create and add it to the session
                new_role = Role(id=role_data["id"], role_name=role_data["role_name"])
                db.session.add(new_role)
                logging.info(f"Role '{role_data['role_name']}' added successfully!")
            else:
                logging.info(f"Role '{role_data['role_name']}' already exists.")

        # Commit the session to save the new roles
        db.session.commit()


def create_admin(application):
    """create an admin user"""
    from .models import User
    from werkzeug.security import generate_password_hash, check_password_hash

    with application.app_context():
        user = User.query.filter_by(username="superadmin").first()

        if not user:
            admin = User(
                email="admin@gmail.com",
                username="superadmin",
                password=generate_password_hash("admin", method="pbkdf2:sha256"),
                role_id=1,
            )
            db.session.add(admin)
            db.session.commit()
            logging.info("admin created successfully")

        else:
            logging.info("Admin user already exists")
