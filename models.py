utf-8utf-8from flask_login import UserMixin

from extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

                                                              
    password_hash = db.Column(db.String(256), nullable=True)

    email = db.Column(db.String(120), unique=True, nullable=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

                                                                                
    google_id = db.Column(db.String(100), unique=True, nullable=True)

    posters = db.relationship(
        "Poster",
        backref="author",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Poster(db.Model):
    __tablename__ = "poster"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    naslov_projekta = db.Column(db.String(100), default="Saved Work")

    ime_prezime = db.Column(db.String(100))

    y_main = db.Column(db.String(10))
    ls_main = db.Column(db.String(10))
    trans_main = db.Column(db.String(20))

    podnaslov = db.Column(db.String(150))

    y_sub = db.Column(db.String(10))
    ls_sub = db.Column(db.String(10))
    trans_sub = db.Column(db.String(20))

    y_info = db.Column(db.String(10))
    ls_info = db.Column(db.String(10))
    trans_info = db.Column(db.String(20))

    datum_raw = db.Column(db.String(20))
    vrijeme_raw = db.Column(db.String(20))

    lat = db.Column(db.String(20))
    lon = db.Column(db.String(20))

    boja_pozadine = db.Column(db.String(10))
    boja_okvira = db.Column(db.String(10))
    boja_zvijezda = db.Column(db.String(10))
    boja_teksta = db.Column(db.String(10))

    font_choice = db.Column(db.String(100))

    lokacija = db.Column(db.String(100))
    datum_txt = db.Column(db.String(100))

    oblik = db.Column(db.String(20))

    okvir = db.Column(db.String(5))
    grid = db.Column(db.String(5))
    lines = db.Column(db.String(5))
    prikazi_mjesec = db.Column(db.String(5))
    preview_path = db.Column(db.String(200))