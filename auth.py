from flask import Blueprint, request, jsonify, redirect, url_for
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db, oauth
from models import User


auth_bp = Blueprint("auth", __name__)


def _generate_username_from_email(email):
    """username part before @ as base, add number if taken"""
    base = email.split("@")[0].strip() or "user"
    username = base
    counter = 1
    while User.query.filter(db.func.lower(User.username) == username.lower()).first():
        username = f"{base}{counter}"
        counter += 1
    return username


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not first_name or not email or not password:
            return jsonify({
                "error": "First name, email, and password are required."
            }), 400

        if "@" not in email:
            return jsonify({
                "error": "Please enter a valid email."
            }), 400

        if len(password) < 6:
            return jsonify({
                "error": "Password must be at least 6 characters."
            }), 400

        postoji_email = User.query.filter(
            db.func.lower(User.email) == email.lower()
        ).first()

        if postoji_email:
            return jsonify({
                "error": "Email already registered."
            }), 400

                                                                                     
        username = _generate_username_from_email(email)

        user = User(
            username=username,
            password_hash=generate_password_hash(
                password,
                method="pbkdf2:sha256"
            ),
            email=email,
            first_name=first_name,
            last_name=last_name or None,
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)

        return jsonify({
            "message": "Registration successful!",
            "username": user.username
        })
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
                                                                                     
                                                                
        identifier = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not identifier or not password:
            return jsonify({
                "error": "Username and password are required."
            }), 400

        if "@" in identifier:
            user = User.query.filter(
                db.func.lower(User.email) == identifier.lower()
            ).first()
        else:
            user = User.query.filter(
                db.func.lower(User.username) == identifier.lower()
            ).first()

        if user and user.password_hash is None:
            return jsonify({
                "error": "This account was created via Google - use the Google button to log in."
            }), 401

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return jsonify({
                "message": "Uspješna prijava!",
                "username": user.username
            })

        return jsonify({
            "error": "Invalid username/email or password."
        }), 401
    except Exception as e:
                                            
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("main.index")
    )


                                                        
                                                                  
                                                                   

@auth_bp.route("/login/google")
def login_google():
    redirect_uri = url_for("auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/login/google/callback")
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = token.get("userinfo")

    google_id = user_info["sub"]
    email = user_info.get("email", "")
    first_name = user_info.get("given_name", "")
    last_name = user_info.get("family_name", "")

    user = User.query.filter_by(google_id=google_id).first()

    if not user and email:
                                                                                     
                                                                            
        user = User.query.filter(
            db.func.lower(User.email) == email.lower()
        ).first()

    if not user:
        user = User(
            username=_generate_username_from_email(email or f"user{google_id[:8]}"),
            password_hash=None,
            email=email or None,
            first_name=first_name,
            last_name=last_name or None,
            google_id=google_id,
        )
        db.session.add(user)
    else:
        user.google_id = google_id

    db.session.commit()
    login_user(user)

    return redirect(url_for("main.index"))