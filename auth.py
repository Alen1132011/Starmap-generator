from flask import Blueprint, current_app, jsonify, redirect, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db, oauth
from models import User


auth_bp = Blueprint("auth", __name__)


def generateUsernameFromEmail(email):
    base = email.split("@", 1)[0].strip() or "user"
    base = base[:45]
    username = base
    counter = 1

    while User.query.filter(db.func.lower(User.username) == username.lower()).first():
        username = f"{base[:45]}{counter}"
        counter += 1

    return username


def googleError(errorCode):
    return redirect(url_for("main.account", auth_error=errorCode))


@auth_bp.route("/register", methods=["POST"])
def register():
    firstName = request.form.get("first_name", "").strip()
    lastName = request.form.get("last_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not firstName or not email or not password:
        return jsonify({"error": "First name, email, and password are required."}), 400

    if "@" not in email or email.startswith("@") or email.endswith("@"):
        return jsonify({"error": "Please enter a valid email."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    existingUser = User.query.filter(db.func.lower(User.email) == email).first()
    if existingUser:
        return jsonify({"error": "Email already registered."}), 400

    user = User(
        username=generateUsernameFromEmail(email),
        password_hash=generate_password_hash(password, method="pbkdf2:sha256"),
        email=email,
        first_name=firstName,
        last_name=lastName or None
    )

    try:
        db.session.add(user)
        db.session.commit()
        login_user(user)
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Account registration failed")
        return jsonify({"error": "Could not create the account. Please try again."}), 500

    return jsonify({"message": "Registration successful!", "username": user.username})


@auth_bp.route("/login", methods=["POST"])
def login():
    identifier = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not identifier or not password:
        return jsonify({"error": "Username/email and password are required."}), 400

    if "@" in identifier:
        user = User.query.filter(db.func.lower(User.email) == identifier.lower()).first()
    else:
        user = User.query.filter(db.func.lower(User.username) == identifier.lower()).first()

    if user and not user.password_hash:
        return jsonify({"error": "This account uses Google sign-in. Choose Continue with Google."}), 401

    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({"message": "Login successful!", "username": user.username})

    return jsonify({"error": "Invalid username/email or password."}), 401


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@auth_bp.route("/login/google")
def loginGoogle():
    if not current_app.config.get("GOOGLE_CLIENT_ID") or not current_app.config.get("GOOGLE_CLIENT_SECRET"):
        return googleError("google_unavailable")                      

    try:
        redirectUri = "https://starmap.alen.hackclub.app/login/google/callback"
        return oauth.google.authorize_redirect(redirectUri)
    except Exception:
        current_app.logger.exception("Google sign-in could not be started")
        return googleError("google_failed")


@auth_bp.route("/login/google/callback")
def googleCallback():
    try:
        token = oauth.google.authorize_access_token()
        userInfo = token.get("userinfo")
        if not userInfo:
            return googleError("google_failed")

        googleId = userInfo.get("sub") if userInfo else None
        email = (userInfo.get("email") or "").strip().lower() if userInfo else ""
        emailVerified = userInfo.get("email_verified") is True if userInfo else False

        if not googleId or not email or not emailVerified:
            return googleError("google_email_unverified")

        user = User.query.filter_by(google_id=googleId).first()

        if not user:
            user = User.query.filter(db.func.lower(User.email) == email).first()

        if user and user.google_id and user.google_id != googleId:
            return googleError("google_account_conflict")

        if not user:
            user = User(
                username=generateUsernameFromEmail(email),
                password_hash=None,
                email=email,
                first_name=(userInfo.get("given_name") or "")[:50],
                last_name=(userInfo.get("family_name") or "")[:50] or None,
                google_id=googleId
            )
            db.session.add(user)
        else:
            user.google_id = googleId
            if not user.first_name and userInfo.get("given_name"):
                user.first_name = userInfo.get("given_name")[:50]
            if not user.last_name and userInfo.get("family_name"):
                user.last_name = userInfo.get("family_name")[:50]

        db.session.commit()
        login_user(user)
        return redirect(url_for("main.index"))
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Google sign-in failed")
        return googleError("google_failed")
