from flask import Blueprint, render_template, redirect, url_for, request
from .models import User
from . import db
from flask import flash,current_app
from flask_login import login_user, logout_user, login_required, current_user
import re
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)


# --------------------- login -----------------------
@auth.route("/login", methods=["GET", "POST"])
def login():
    """User login page functionality"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Sucessfully logged in..", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password entered!!!", category="error")
        else:
            flash("Account does not exist!!, please sign up", category="error")

    return render_template("log-in.html", user=current_user)


# ---------------------- signup ------------------------------
@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    """Controls signup page and user signUp logic"""
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        try:
            # fetch username and password
            user_exists = User.query.filter_by(email=email).first()
            username_exists = User.query.filter_by(username=username).first()

            # check if username and email already in database
            if user_exists:
                flash("A user with this email already exists.", category="error")
            elif (
                re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email) is None
            ):
                flash("Enter a valid email.", category="error")
            elif username_exists:
                flash("A user with this username already exists.", category="error")
            elif password1 != password2:
                flash("Entered passwords don't match!", category="error")
            elif len(username) < 2:
                flash("Username is too short.", category="error")
            elif len(password1) < 6:
                flash("Password must be more than 6 characters!", category="error")
            # create account
            else:
                try:
                    hashed_password = generate_password_hash(password1, method="pbkdf2:sha256")
                    new_user = User(
                        email=email,
                        username=username,
                        password=hashed_password,
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    login_user(new_user, remember=True)
                    flash("User created Successfully!", category="success")
                    return redirect(url_for("views.home"))
                except Exception as e:
                    db.session.rollback()
                    flash("An error occurred while creating the user", category="error")
                    # Log the error for debugging
                    current_app.logger.error(f"Error creating user: {e}")
        except Exception as e:
            flash("Error with siging in , please contact admin", category="error")
            # Log the error for debugging
            current_app.logger.error(f"error in sign_up function: {e}")

    return render_template("sign-up.html", user=current_user)


# ----------------- logout ----------------------
@auth.route("/log-out")
@login_required
def log_out():
    """log out user"""
    logout_user()
    return redirect(url_for("auth.login"))
