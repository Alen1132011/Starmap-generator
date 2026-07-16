from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import math, os, time
from skyfield.api import load
from skyfield.data import hipparcos
from PIL import Image, ImageDraw, ImageFont

# Biblioteke za bazu podataka i autentifikaciju
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'starmap_super_tajni_kljuc_987'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///starmap.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'  # Ako korisnik nije ulogovan, vraća ga na početnu

FONTS_DIR = 'fonts'
if not os.path.exists(FONTS_DIR): os.makedirs(FONTS_DIR)
if not os.path.exists('static'): os.makedirs('static')

# --- MODELI ZA BAZU PODATAKA ---

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    posters = db.relationship('Poster', backref='author', lazy=True, cascade="all, delete-orphan")

class Poster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    naslov_projekta = db.Column(db.String(100), default="Sačuvani Rad")
    
    # Parametri dizajna
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- MATEMATIKA, FIZIKA I PIL CRTANJE ---

VEZE_SAZVIJEZDA = [
    (53910, 58001), (58001, 59774), (59774, 62956), (62956, 65378), (65378, 67301), (67301, 65477), (65477, 62956),
    (11767, 85822), (85822, 82080), (82080, 79822), (79822, 77055), (77055, 75097), (75097, 72607), (72607, 70898),
    (3179, 3655), (3655, 4427), (4427, 6686), (6686, 8886), (27989, 26727), (26727, 25930), (25930, 25336), 
    (25336, 26311), (25930, 27366), (27366, 28691), (28691, 29426), (27989, 29038), (37279, 36850), (36850, 34693),
    (34693, 32246), (37826, 36188), (34029, 32349), (49669, 47908), (47908, 46390), (46390, 50583), (50583, 54879),
    (80763, 80112), (80112, 78820), (78820, 78401), (78265, 82396), (82396, 84143), (13531, 14328), (14328, 15863),
    (15863, 17358), (24608, 23015), (23015, 28380), (28380, 25428), (21421, 20889), (20889, 20648), (20648, 20205),
    (69673, 71075), (71075, 72105), (72105, 74666), (65474, 63613), (63613, 61941), (61941, 60129), (91262, 92420),
    (92420, 93194), (93194, 91919), (102098, 100453), (100453, 97165), (97165, 95853), (97649, 97278), (97278, 95501),
    (113963, 112029), (112029, 109427), (1067, 4436), (4436, 9640), (84345, 83207), (83207, 81693), (87585, 85670),
    (85670, 83895), (83895, 80331), (80331, 78527), (78527, 75458), (75458, 68756), (68756, 61281)
]

with load.open(hipparcos.URL) as f:
    stars_df = hipparcos.load_dataframe(f)
    stars_df = stars_df[stars_df['magnitude'] <= 6.5]

eph = load('de421.bsp')
sunce_tijelo, mjesec_tijelo, zemlja_tijelo = eph['sun'], eph['moon'], eph['earth']

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def generisi_tacke_srca(cx, cy, R):
    punti = []
    for stepen in range(0, 360, 1):
        ang = math.radians(stepen)
        t_x = 16 * math.sin(ang)**3
        t_y = 13 * math.cos(ang) - 5 * math.cos(2*ang) - 2 * math.cos(3*ang) - math.cos(4*ang)
        fx = cx + t_x * (R * 0.059)
        fy = cy - t_y * (R * 0.055) - (R * 0.22)
        punti.append((int(fx), int(fy)))
    return punti

def izracunaj_fazu_mjeseca(t):
    e = zemlja_tijelo.at(t)
    s = e.observe(sunce_tijelo).apparent()
    m = e.observe(mjesec_tijelo).apparent()
    ugao = s.separation_from(m).radians
    osvijetljenost = (1.0 + math.cos(math.pi - ugao)) / 2.0
    
    ts = load.timescale()
    t2 = ts.utc(t.utc.year, t.utc.month, t.utc.day, t.utc.hour, t.utc.minute + 1)
    e2 = zemlja_tijelo.at(t2)
    s2 = e2.observe(sunce_tijelo).apparent()
    m2 = e2.observe(mjesec_tijelo).apparent()
    ugao2 = s2.separation_from(m2).radians
    
    smer = 1 if ugao2 > ugao else -1
    return osvijetljenost, smer

def nacrtaj_mjesec(draw, cx, cy, r, osvijetljenost, smer, boja_mjeseca, boja_bg):
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=boja_bg, outline=boja_mjeseca, width=2)
    if osvijetljenost < 0.03: return 
    if osvijetljenost > 0.97:
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=boja_mjeseca)
        return
    k = abs(2 * osvijetljenost - 1)
    if osvijetljenost > 0.5:
        if smer > 0:
            draw.chord([cx-r, cy-r, cx+r, cy+r], 270, 90, fill=boja_mjeseca)
            draw.ellipse([cx - r*k, cy-r, cx + r*k, cy+r], fill=boja_mjeseca)
        else:
            draw.chord([cx-r, cy-r, cx+r, cy+r], 90, 270, fill=boja_mjeseca)
            draw.ellipse([cx - r*k, cy-r, cx + r*k, cy+r], fill=boja_mjeseca)
    else:
        if smer > 0:
            draw.chord([cx-r, cy-r, cx+r, cy+r], 270, 90, fill=boja_mjeseca)
            draw.ellipse([cx - r*k, cy-r, cx + r*k, cy+r], fill=boja_bg, outline=boja_mjeseca, width=1)
        else:
            draw.chord([cx-r, cy-r, cx+r, cy+r], 90, 270, fill=boja_mjeseca)
            draw.ellipse([cx - r*k, cy-r, cx + r*k, cy+r], fill=boja_bg, outline=boja_mjeseca, width=1)

def draw_text_spaced(draw, position, text, font, fill, spacing=0, anchor="mm"):
    if not text: return
    sirine_slova = [font.getbbox(char)[2] for char in text]
    ukupna_sirina = sum(sirine_slova) + spacing * (len(text) - 1)
    cx, cy = position
    if anchor == "mm":
        start_x = cx - ukupna_sirina / 2
        bbox = font.getbbox(text)
        th = bbox[3] - bbox[1]
        start_y = cy - th / 2
    else:
        start_x = cx
        start_y = cy
    trenutni_x = start_x
    for char in text:
        draw.text((trenutni_x, start_y), char, font=font, fill=fill)
        trenutni_x += font.getbbox(char)[2] + spacing

def transformisi_tekst(tekst, transform_tip):
    if transform_tip == 'uppercase': return tekst.upper()
    if transform_tip == 'lowercase': return tekst.lower()
    return tekst

def napravi_starmap_pro(podaci):
    # Provjeravamo licencu preko Render Environment okruženja
    STATUS_LICENCE = os.environ.get("VERZIJA_APLIKACIJE", "DEMO")

    # Pokupimo parametre koje je korisnik poslao iz forme
    raw_bg = podaci.get('boja_pozadine', '#05070d')
    raw_okvir = podaci.get('boja_okvira', '#ffffff')
    raw_zvijezda = podaci.get('boja_zvijezda', '#ffffff')
    raw_tekst = podaci.get('boja_teksta', '#ffffff')

    prikazi_grid = podaci.get('grid') == 'on'
    prikazi_lines = podaci.get('lines') == 'on'
    prikazi_okvir = podaci.get('okvir') == 'on'
    prikazi_mjesec = podaci.get('prikazi_mjesec') == 'on'
    
    oblik = podaci.get('oblik', 'krug')
    
    # Podrazumijevane dimenzije za Premium verziju
    SIRINA, VISINA = 2400, 3400 
    cx, cy, R = 1200, 1150, 950

    # --- LOKALNA / OPEN-SOURCE ZAŠTITA (ZAKLJUČAVANJE) ---
    if STATUS_LICENCE != "PREMIUM_PRODUKCIJA":
        # 1. Gasimo apsolutno sve opcije sa štrikiranjem (force-off)
        prikazi_grid = False
        prikazi_lines = False
        prikazi_okvir = False
        prikazi_mjesec = False
        oblik = 'krug'  # Forsiramo samo obični krug (srce je zaključano)

        # 2. Smanjujemo rezoluciju (tako da je nemoguće odštampati poster)
        SIRINA, VISINA = 1000, 1416  
        cx, cy, R = 500, 480, 390

        # 3. Zaključavamo boje na samo 2 šablona (color picker se ignoriše)
        # Ako detektujemo da su probali staviti bijelu pozadinu, damo im "White" šablon, inače "Classic Navy"
        is_white_bg = raw_bg.lower() in ['#ffffff', '#fff', 'rgb(255, 255, 255)', 'white']
        if is_white_bg:
            # Šablon 2: Minimalist White
            raw_bg = '#ffffff'
            raw_okvir = '#111111'
            raw_zvijezda = '#111111'
            raw_tekst = '#111111'
        else:
            # Šablon 1: Classic Navy
            raw_bg = '#05070d'
            raw_okvir = '#ffffff'
            raw_zvijezda = '#ffffff'
            raw_tekst = '#ffffff'

    # Pretvaranje u RGB formate nakon što su pravila licence primijenjena
    bg_boja = hex_to_rgb(raw_bg)
    okvir_boja = hex_to_rgb(raw_okvir)
    zvijezde_boja = hex_to_rgb(raw_zvijezda)
    tekst_boja = hex_to_rgb(raw_tekst)

    img = Image.new('RGB', (SIRINA, VISINA), color=bg_boja)
    maska_neba = Image.new('L', (SIRINA, VISINA), 0)
    draw_maska = ImageDraw.Draw(maska_neba)
    
    if oblik == 'srce':
        tacke_srca = generisi_tacke_srca(cx, cy, R)
        draw_maska.polygon(tacke_srca, fill=255)
    else:
        draw_maska.ellipse([cx-R, cy-R, cx+R, cy+R], fill=255)

    nebo_img = Image.new('RGBA', (SIRINA, VISINA), (0,0,0,0))
    draw_nebo = ImageDraw.Draw(nebo_img, 'RGBA')

    ts = load.timescale()
    try:
        y, m, d = map(int, (podaci.get('datum_raw') or '2000 01 01').split())
        h, mn = map(int, (podaci.get('vrijeme_raw') or '00 00').split())
        lon, lat = float(podaci.get('lon') or 0), float(podaci.get('lat') or 0)
    except: y, m, d, h, mn, lon, lat = 2000, 1, 1, 0, 0, 0, 0

    t = ts.utc(y, m, d, h, mn)
    lst = (18.697374558 + 24.06570982441908 * (t.ut1 - 2451545.0) + lon / 15.0) % 24

    # --- STEREOGRAFSKA REŠETKA (GRID) ---
    if prikazi_grid:
        grid_col = (*zvijezde_boja, 45)
        for lat_deg in range(-75, 76, 15):
            tacke_linije = []
            for lon_deg in range(-90, 91, 2):
                lon_rad = math.radians(lon_deg)
                lat_rad = math.radians(lat_deg)
                imenilac = 1 + math.cos(lat_rad) * math.cos(lon_rad)
                if imenilac > 0:
                    x = cx + R * (math.cos(lat_rad) * math.sin(lon_rad)) / imenilac
                    y = cy - R * (math.sin(lat_rad)) / imenilac
                    tacke_linije.append((x, y))
            if len(tacke_linije) > 1:
                draw_nebo.line(tacke_linije, fill=grid_col, width=3)
                
        for lon_deg in range(-75, 76, 15):
            tacke_linije = []
            for lat_deg in range(-90, 91, 2):
                lon_rad = math.radians(lon_deg)
                lat_rad = math.radians(lat_deg)
                imenilac = 1 + math.cos(lat_rad) * math.cos(lon_rad)
                if imenilac > 0:
                    x = cx + R * (math.cos(lat_rad) * math.sin(lon_rad)) / imenilac
                    y = cy - R * (math.sin(lat_rad)) / imenilac
                    tacke_linije.append((x, y))
            if len(tacke_linije) > 1:
                draw_nebo.line(tacke_linije, fill=grid_col, width=3)

    # --- CRTANJE ZVIJEZDA ---
    pos_map = {}
    for hid, s in stars_df.iterrows():
        ha = math.radians((lst - s['ra_hours']) * 15)
        dec, lt = math.radians(s['dec_degrees']), math.radians(lat)
        sin_alt = math.sin(lt)*math.sin(dec) + math.cos(lt)*math.cos(dec)*math.cos(ha)
        alt = math.asin(max(-1, min(1, sin_alt)))
        
        if alt > 0:
            r_px = R * (1 - math.degrees(alt)/90)
            cos_az = (math.sin(dec)-math.sin(alt)*math.sin(lt))/(math.cos(alt)*math.cos(lt))
            az = math.acos(max(-1, min(1, cos_az)))
            if math.sin(ha) > 0: az = 2*math.pi - az
            
            x, y = cx+r_px*math.sin(az), cy-r_px*math.cos(az)
            pos_map[hid] = (x, y)
            
            mag = s['magnitude']
            size = max(2, int((6.8-mag)*2.5))
            if mag < 1.5:
                draw_nebo.ellipse([x-size-5, y-size-5, x+size+5, y+size+5], fill=(*zvijezde_boja, 50))
            draw_nebo.ellipse([x-size, y-size, x+size, y+size], fill=zvijezde_boja)

    # --- LINIJE SAZVIJEŽĐA ---
    if prikazi_lines:
        for s, e in VEZE_SAZVIJEZDA:
            if s in pos_map and e in pos_map:
                draw_nebo.line([pos_map[s], pos_map[e]], fill=(*zvijezde_boja, 180), width=4)

    img.paste(nebo_img, (0,0), mask=maska_neba)
    draw_main = ImageDraw.Draw(img, 'RGBA')

    # Unutrašnji okvir oko mape (srce ili krug)
    if oblik == 'srce':
        tacke_srca = generisi_tacke_srca(cx, cy, R)
        draw_main.polygon(tacke_srca, outline=okvir_boja, width=18 if STATUS_LICENCE == "PREMIUM_PRODUKCIJA" else 8)
    else:
        draw_main.ellipse([cx-R, cy-R, cx+R, cy+R], outline=okvir_boja, width=18 if STATUS_LICENCE == "PREMIUM_PRODUKCIJA" else 8)

    # --- VANJSKI UKRASNI OKVIR ---
    if prikazi_okvir:
        draw_main.rectangle([70, 70, SIRINA-70, VISINA-70], outline=okvir_boja, width=12)
        draw_main.rectangle([100, 100, SIRINA-100, VISINA-100], outline=okvir_boja, width=4)

    odabrani_font = podaci.get('font_choice', 'arial.ttf')
    font_path = os.path.join(FONTS_DIR, odabrani_font) if odabrani_font != 'arial.ttf' else 'arial.ttf'

    try:
        # Dinamičko prilagođavanje veličine fonta i pozicije u zavisnosti od rezolucije (Premium vs Demo)
        if STATUS_LICENCE == "PREMIUM_PRODUKCIJA":
            f_main = ImageFont.truetype(font_path, 140)
            f_sub = ImageFont.truetype(font_path, 70)
            f_info = ImageFont.truetype(font_path, 52)
            
            y_main = int(podaci.get('y_main', 2450))
            y_sub = int(podaci.get('y_sub', 2650))
            y_info = int(podaci.get('y_info', 2950))
            y_razmak = 85
        else:
            # Smanjene veličine fontova za demo sliku niske rezolucije
            f_main = ImageFont.truetype(font_path, 60)
            f_sub = ImageFont.truetype(font_path, 30)
            f_info = ImageFont.truetype(font_path, 22)
            
            y_main = 1020
            y_sub = 1110
            y_info = 1230
            y_razmak = 35

        ls_main = int(podaci.get('ls_main', 0))
        ls_sub = int(podaci.get('ls_sub', 0))
        ls_info = int(podaci.get('ls_info', 0))
        
        trans_main = podaci.get('trans_main', 'uppercase')
        trans_sub = podaci.get('trans_sub', 'uppercase')
        trans_info = podaci.get('trans_info', 'uppercase')

        t_main = transformisi_tekst(podaci.get('ime_prezime', ''), trans_main)
        t_sub = transformisi_tekst(podaci.get('podnaslov', ''), trans_sub)
        t_lok = transformisi_tekst(podaci.get('lokacija', ''), trans_info)
        t_dat = transformisi_tekst(podaci.get('datum_txt', ''), trans_info)
        t_koor = transformisi_tekst(f"{lat}° N, {lon}° E", trans_info)

        draw_text_spaced(draw_main, (cx, y_main), t_main, f_main, tekst_boja, spacing=ls_main, anchor="mm")
        draw_text_spaced(draw_main, (cx, y_sub), t_sub, f_sub, tekst_boja, spacing=ls_sub, anchor="mm")
        
        draw_text_spaced(draw_main, (cx, y_info), t_lok, f_info, tekst_boja, spacing=ls_info, anchor="mm")
        draw_text_spaced(draw_main, (cx, y_info + y_razmak), t_dat, f_info, tekst_boja, spacing=ls_info, anchor="mm")
        draw_text_spaced(draw_main, (cx, y_info + (y_razmak * 2)), t_koor, f_info, tekst_boja, spacing=ls_info, anchor="mm")

        # --- CRTANJE MJESECA (Samo ako je dozvoljeno) ---
        if prikazi_mjesec:
            osvijetljenost, smer = izracunaj_fazu_mjeseca(t)
            # Na demo verziji je onemogućeno pa se ovaj dio neće izvršiti
            nacrtaj_mjesec(draw_main, cx + 500, y_info + y_razmak, 75, osvijetljenost, smer, okvir_boja, bg_boja)

    except Exception as e:
        print(f"Greška prilikom ispisa teksta: {e}")

    putanja = os.path.join('static', 'preview.png')
    img.save(putanja, quality=100)
    return putanja


# --- RUTE ZA AUTENTIFIKACIJU I ČUVANJE RADOVA ---

@app.route('/')
def index():
    fontovi = []
    for korijen, direktoriji, fajlovi in os.walk(FONTS_DIR):
        for f in fajlovi:
            if f.endswith(('.ttf', '.otf')):
                relativna_putanja = os.path.relpath(os.path.join(korijen, f), FONTS_DIR).replace('\\', '/')
                fontovi.append(relativna_putanja)
    fontovi.sort()
    return render_template('index.html', fontovi=fontovi)

@app.route('/update', methods=['POST'])
def update():
    path = napravi_starmap_pro(request.form.to_dict())
    return jsonify({"image_url": f"/{path}?v={time.time()}"})

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    if not username or not password:
        return jsonify({'error': 'Korisničko ime i lozinka su obavezni.'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Korisničko ime je zauzeto.'}), 400
    
    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, password_hash=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return jsonify({'message': 'Uspješna registracija!', 'username': new_user.username})

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'message': 'Uspješna prijava!', 'username': user.username})
    return jsonify({'error': 'Pogrešno korisničko ime ili lozinka.'}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/save_poster', methods=['POST'])
@login_required
def save_poster():
    data = request.form.to_dict()
    novi_poster = Poster(
        user_id=current_user.id,
        naslov_projekta=data.get('naslov_projekta', 'Moj Poster'),
        ime_prezime=data.get('ime_prezime'),
        y_main=data.get('y_main'),
        ls_main=data.get('ls_main'),
        trans_main=data.get('trans_main'),
        podnaslov=data.get('podnaslov'),
        y_sub=data.get('y_sub'),
        ls_sub=data.get('ls_sub'),
        trans_sub=data.get('trans_sub'),
        y_info=data.get('y_info'),
        ls_info=data.get('ls_info'),
        trans_info=data.get('trans_info'),
        datum_raw=data.get('datum_raw'),
        vrijeme_raw=data.get('vrijeme_raw'),
        lat=data.get('lat'),
        lon=data.get('lon'),
        boja_pozadine=data.get('boja_pozadine'),
        boja_okvira=data.get('boja_okvira'),
        boja_zvijezda=data.get('boja_zvijezda'),
        boja_teksta=data.get('boja_teksta'),
        font_choice=data.get('font_choice'),
        lokacija=data.get('lokacija'),
        datum_txt=data.get('datum_txt'),
        oblik=data.get('oblik'),
        okvir='on' if 'okvir' in data else 'off',
        grid='on' if 'grid' in data else 'off',
        lines='on' if 'lines' in data else 'off',
        prikazi_mjesec='on' if 'prikazi_mjesec' in data else 'off'
    )
    db.session.add(novi_poster)
    db.session.commit()
    return jsonify({'message': 'Rad je uspješno sačuvan na tvoj profil!'})

@app.route('/get_posters', methods=['GET'])
@login_required
def get_posters():
    radovi = [{
        'id': p.id,
        'naslov': p.naslov_projekta,
        'ime_prezime': p.ime_prezime,
        'lokacija': p.lokacija,
        'datum_txt': p.datum_txt
    } for p in current_user.posters]
    return jsonify({'posters': radovi})

@app.route('/load_poster/<int:poster_id>', methods=['GET'])
@login_required
def load_poster(poster_id):
    p = Poster.query.filter_by(id=poster_id, user_id=current_user.id).first_or_404()
    return jsonify({
        'ime_prezime': p.ime_prezime, 'y_main': p.y_main, 'ls_main': p.ls_main, 'trans_main': p.trans_main,
        'podnaslov': p.podnaslov, 'y_sub': p.y_sub, 'ls_sub': p.ls_sub, 'trans_sub': p.trans_sub,
        'y_info': p.y_info, 'ls_info': p.ls_info, 'trans_info': p.trans_info,
        'datum_raw': p.datum_raw, 'vrijeme_raw': p.vrijeme_raw, 'lat': p.lat, 'lon': p.lon,
        'boja_pozadine': p.boja_pozadine, 'boja_okvira': p.boja_okvira, 'boja_zvijezda': p.boja_zvijezda, 'boja_teksta': p.boja_teksta,
        'font_choice': p.font_choice, 'lokacija': p.lokacija, 'datum_txt': p.datum_txt, 'oblik': p.oblik,
        'okvir': p.okvir, 'grid': p.grid, 'lines': p.lines, 'prikazi_mjesec': p.prikazi_mjesec
    })

@app.route('/delete_poster/<int:poster_id>', methods=['POST'])
@login_required
def delete_poster(poster_id):
    p = Poster.query.filter_by(id=poster_id, user_id=current_user.id).first_or_404()
    db.session.delete(p)
    db.session.commit()
    return jsonify({'message': 'Rad obrisan.'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Automatska inicijalizacija baze na startu
     
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)     
