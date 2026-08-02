utf-8utf-8import os
import time

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user

from services.starmap import napravi_starmap_pro
from models import Poster
from extensions import db


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():

    fontovi = []

    if os.path.exists("fonts"):

        for root, dirs, files in os.walk("fonts"):

            for file in files:

                if file.endswith((".ttf", ".otf")):

                    path = os.path.relpath(
                        os.path.join(root, file),
                        "fonts"
                    ).replace("\\", "/")

                    fontovi.append(path)

    fontovi.sort()

    return render_template(
        "index.html",
        fontovi=fontovi
    )


@main_bp.route("/account")
def account():

    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    return render_template("login.html")


@main_bp.route("/update", methods=["POST"])
def update():

    path = napravi_starmap_pro(
        request.form.to_dict()
    )

    return jsonify({
        "image_url": f"/{path}?v={time.time()}"
    })


@main_bp.route("/save_poster", methods=["POST"])
@login_required
def save_poster():

    data = request.form.to_dict()

                                               
    user_folder = f"static/user_{current_user.id}"
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

                                         
    thumbnail_filename = f"poster_{int(time.time())}.png"
    thumbnail_path = os.path.join(user_folder, thumbnail_filename).replace('\\', '/')

                                                              
    preview_data = data.copy()
    preview_data['naslov_projekta'] = data.get('naslov_projekta', 'My Poster')
    napravi_starmap_pro(preview_data, width=400, height=566, output_path=thumbnail_path)

    poster = Poster(

        user_id=current_user.id,

        naslov_projekta=data.get(
            "naslov_projekta",
            "My Poster"
        ),

        ime_prezime=data.get("ime_prezime"),

        y_main=data.get("y_main"),
        ls_main=data.get("ls_main"),
        trans_main=data.get("trans_main"),

        podnaslov=data.get("podnaslov"),

        y_sub=data.get("y_sub"),
        ls_sub=data.get("ls_sub"),
        trans_sub=data.get("trans_sub"),

        y_info=data.get("y_info"),
        ls_info=data.get("ls_info"),
        trans_info=data.get("trans_info"),

        datum_raw=data.get("datum_raw"),
        vrijeme_raw=data.get("vrijeme_raw"),

        lat=data.get("lat"),
        lon=data.get("lon"),

        boja_pozadine=data.get("boja_pozadine"),
        boja_okvira=data.get("boja_okvira"),
        boja_zvijezda=data.get("boja_zvijezda"),
        boja_teksta=data.get("boja_teksta"),

        font_choice=data.get("font_choice"),

        lokacija=data.get("lokacija"),
        datum_txt=data.get("datum_txt"),

        oblik=data.get("oblik"),

        okvir="on" if "okvir" in data else "off",
        grid="on" if "grid" in data else "off",
        lines="on" if "lines" in data else "off",
        prikazi_mjesec="on" if "prikazi_mjesec" in data else "off",
        preview_path=thumbnail_path
    )

    db.session.add(poster)
    db.session.commit()

    return jsonify({
        "message": "Poster saved successfully."
    })


@main_bp.route("/get_posters")
@login_required
def get_posters():

    radovi = []

    for poster in current_user.posters:

        radovi.append({

            "id": poster.id,

            "naslov": poster.naslov_projekta,

            "ime_prezime": poster.ime_prezime,

            "lokacija": poster.lokacija,

            "datum_txt": poster.datum_txt,

            "preview_path": poster.preview_path.replace('\\', '/') if poster.preview_path else None

        })

    return jsonify({
        "posters": radovi
    })


@main_bp.route("/load_poster/<int:id>")
@login_required
def load_poster(id):

    poster = Poster.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    return jsonify({

        "ime_prezime": poster.ime_prezime,

        "y_main": poster.y_main,
        "ls_main": poster.ls_main,
        "trans_main": poster.trans_main,

        "podnaslov": poster.podnaslov,

        "y_sub": poster.y_sub,
        "ls_sub": poster.ls_sub,
        "trans_sub": poster.trans_sub,

        "y_info": poster.y_info,
        "ls_info": poster.ls_info,
        "trans_info": poster.trans_info,

        "datum_raw": poster.datum_raw,
        "vrijeme_raw": poster.vrijeme_raw,

        "lat": poster.lat,
        "lon": poster.lon,

        "boja_pozadine": poster.boja_pozadine,
        "boja_okvira": poster.boja_okvira,
        "boja_zvijezda": poster.boja_zvijezda,
        "boja_teksta": poster.boja_teksta,

        "font_choice": poster.font_choice,

        "lokacija": poster.lokacija,
        "datum_txt": poster.datum_txt,

        "oblik": poster.oblik,

        "okvir": poster.okvir,
        "grid": poster.grid,
        "lines": poster.lines,
        "prikazi_mjesec": poster.prikazi_mjesec
    })


@main_bp.route("/delete_poster/<int:id>", methods=["POST"])
@login_required
def delete_poster(id):

    poster = Poster.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(poster)

    db.session.commit()

    return jsonify({
        "message": "Poster deleted."
    })  