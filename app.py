import os
from flask import Flask

from config import Config
from extensions import db, login_manager, oauth
from models import User
from routes import main_bp
from auth import auth_bp


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)
oauth.init_app(app)

oauth.register(
    name="google",
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}
)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port
    )