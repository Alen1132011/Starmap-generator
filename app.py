from flask import Flask, render_template, request, jsonify
import math, os, time
from skyfield.api import load
from skyfield.data import hipparcos
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

FONTS_DIR = 'fonts'
if not os.path.exists(FONTS_DIR): os.makedirs(FONTS_DIR)
if not os.path.exists('static'): os.makedirs('static')

# Baza podataka sazviježđa (veze između Hipparcos ID-jeva zvijezda)
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

# Učitavanje zvijezda (do magnitude 6.5)
with load.open(hipparcos.URL) as f:
    stars_df = hipparcos.load_dataframe(f)
    stars_df = stars_df[stars_df['magnitude'] <= 6.5]

# Učitavanje efemerida za računanje pozicija nebeskih tijela
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
    """ Vraća procenat osvijetljenosti (0.0 - 1.0) i znak da li raste (+1) ili opada (-1) """
    e = zemlja_tijelo.at(t)
    s = e.observe(sunce_tijelo).apparent()
    m = e.observe(mjesec_tijelo).apparent()
    
    # Elongacija (ugao između Sunca i Mjeseca gledano sa Zemlje)
    ugao = s.separation_from(m).radians
    osvijetljenost = (1.0 + math.cos(math.pi - ugao)) / 2.0
    
    # Računamo elongaciju 1 minut kasnije da vidimo da li raste ili opada
    ts = load.timescale()
    t2 = ts.utc(t.utc.year, t.utc.month, t.utc.day, t.utc.hour, t.utc.minute + 1)
    e2 = zemlja_tijelo.at(t2)
    s2 = e2.observe(sunce_tijelo).apparent()
    m2 = e2.observe(mjesec_tijelo).apparent()
    ugao2 = s2.separation_from(m2).radians
    
    smer = 1 if ugao2 > ugao else -1
    return osvijetljenost, smer

def nacrtaj_mjesec(draw, cx, cy, r, osvijetljenost, smer, boja_mjeseca, boja_bg):
    """ Crta minimalističku fazu Mjeseca pomoću PIL elipsi i isječaka """
    # Osnovni krug (tamna pozadina/kontura Mjeseca)
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=boja_bg, outline=boja_mjeseca, width=2)
    
    # Ako je mladak (manje od 3% osvijetljeno)
    if osvijetljenost < 0.03:
        return 
        
    # Ako je pun Mjesec (više od 97% osvijetljeno)
    if osvijetljenost > 0.97:
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=boja_mjeseca)
        return

    # Faktor širine unutrašnje sjene/elipse
    k = abs(2 * osvijetljenost - 1)
    
    if osvijetljenost > 0.5:
        # Gibbous faza (više od pola osvijetljeno)
        if smer > 0: # Raste (Desna strana osvijetljena)
            draw.chord([cx-r, cy-r, cx+r, cy+r], 270, 90, fill=boja_mjeseca)
            draw.ellipse([cx - r*k, cy-r, cx + r*k, cy+r], fill=boja_mjeseca)
        else: # Opada (Lijeva strana osvijetljena)
            draw.chord([cx-r, cy-r, cx+r, cy+r], 90, 270, fill=boja_mjeseca)
            draw.ellipse([cx - r*k, cy-r, cx + r*k, cy+r], fill=boja_mjeseca)
    else:
        # Crescent faza (manje od pola osvijetljeno)
        if smer > 0: # Raste
            draw.chord([cx-r, cy-r, cx+r, cy+r], 270, 90, fill=boja_mjeseca)
            draw.ellipse([cx - r*k, cy-r, cx + r*k, cy+r], fill=boja_bg, outline=boja_mjeseca, width=1)
        else: # Opada
            draw.chord([cx-r, cy-r, cx+r, cy+r], 90, 270, fill=boja_mjeseca)
            draw.ellipse([cx - r*k, cy-r, cx + r*k, cy+r], fill=boja_bg, outline=boja_mjeseca, width=1)

def draw_text_spaced(draw, position, text, font, fill, spacing=0, anchor="mm"):
    """ Crta tekst karakter po karakter kako bi se simulirao 'letter-spacing' """
    if not text: return
    
    # Izračunavanje ukupne širine teksta sa uračunatim razmacima
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
    bg_boja = hex_to_rgb(podaci.get('boja_pozadine', '#05070d'))
    okvir_boja = hex_to_rgb(podaci.get('boja_okvira', '#ffffff'))
    zvijezde_boja = hex_to_rgb(podaci.get('boja_zvijezda', '#ffffff'))
    tekst_boja = hex_to_rgb(podaci.get('boja_teksta', '#ffffff'))

    SIRINA, VISINA = 2400, 3400 
    cx, cy, R = 1200, 1150, 950
    oblik = podaci.get('oblik', 'krug')

    img = Image.new('RGB', (SIRINA, VISINA), color=bg_boja)
    
    # Kreiranje maske za isijecanje neba
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
        y, m, d = map(int, podaci.get('datum_raw', '2026 05 11').split())
        h, mn = map(int, podaci.get('vrijeme_raw', '22 30').split())
        lon, lat = float(podaci.get('lon', 18.66)), float(podaci.get('lat', 44.53))
    except: y, m, d, h, mn, lon, lat = 2026, 5, 11, 22, 30, 18.66, 44.53

    t = ts.utc(y, m, d, h, mn)
    lst = (18.697374558 + 24.06570982441908 * (t.ut1 - 2451545.0) + lon / 15.0) % 24

    # Crtanje koordinatne mreže (Grid)
    if podaci.get('grid') == 'on':
        grid_col = (*zvijezde_boja, 45)
        for alt_deg in [30, 60]:
            r_g = R * (1 - alt_deg/90)
            draw_nebo.ellipse([cx-r_g, cy-r_g, cx+r_g, cy+r_g], outline=grid_col, width=3)
        for az in range(0, 360, 30):
            ang = math.radians(az)
            draw_nebo.line([(cx, cy), (cx+R*math.sin(ang), cy-R*math.cos(ang))], fill=grid_col, width=2)

    # Izračunavanje i crtanje pozicija zvijezda
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

    # Crtanje linija sazviježđa
    if podaci.get('lines') == 'on':
        for s, e in VEZE_SAZVIJEZDA:
            if s in pos_map and e in pos_map:
                draw_nebo.line([pos_map[s], pos_map[e]], fill=(*zvijezde_boja, 180), width=4)

    img.paste(nebo_img, (0,0), mask=maska_neba)
    draw_main = ImageDraw.Draw(img, 'RGBA')

    # Crtanje okvira oko neba
    if oblik == 'srce':
        tacke_srca = generisi_tacke_srca(cx, cy, R)
        draw_main.polygon(tacke_srca, outline=okvir_boja, width=18)
    else:
        draw_main.ellipse([cx-R, cy-R, cx+R, cy+R], outline=okvir_boja, width=18)

    # Eksterni ukrasni poster okvir
    if podaci.get('okvir') == 'on':
        draw_main.rectangle([70, 70, SIRINA-70, VISINA-70], outline=okvir_boja, width=12)
        draw_main.rectangle([100, 100, SIRINA-100, VISINA-100], outline=okvir_boja, width=4)

    odabrani_font = podaci.get('font_choice', 'arial.ttf')
    font_path = os.path.join(FONTS_DIR, odabrani_font) if odabrani_font != 'arial.ttf' else 'arial.ttf'

    try:
        f_main = ImageFont.truetype(font_path, 140)
        f_sub = ImageFont.truetype(font_path, 70)
        f_info = ImageFont.truetype(font_path, 52)
        
        y_main = int(podaci.get('y_main', 2450))
        y_sub = int(podaci.get('y_sub', 2650))
        y_info = int(podaci.get('y_info', 2950))

        # Letter spacing (razmak) parametri iz HTML formi
        ls_main = int(podaci.get('ls_main', 0))
        ls_sub = int(podaci.get('ls_sub', 0))
        ls_info = int(podaci.get('ls_info', 0))
        
        # Tipovi transformacije teksta
        trans_main = podaci.get('trans_main', 'uppercase')
        trans_sub = podaci.get('trans_sub', 'uppercase')
        trans_info = podaci.get('trans_info', 'uppercase')

        t_main = transformisi_tekst(podaci.get('ime_prezime', ''), trans_main)
        t_sub = transformisi_tekst(podaci.get('podnaslov', ''), trans_sub)
        t_lok = transformisi_tekst(podaci.get('lokacija', ''), trans_info)
        t_dat = transformisi_tekst(podaci.get('datum_txt', ''), trans_info)
        t_koor = transformisi_tekst(f"{lat}° N, {lon}° E", trans_info)

        # Rendering tekstova preko prilagođene funkcije za razmake
        draw_text_spaced(draw_main, (cx, y_main), t_main, f_main, tekst_boja, spacing=ls_main, anchor="mm")
        draw_text_spaced(draw_main, (cx, y_sub), t_sub, f_sub, tekst_boja, spacing=ls_sub, anchor="mm")
        
        draw_text_spaced(draw_main, (cx, y_info), t_lok, f_info, tekst_boja, spacing=ls_info, anchor="mm")
        draw_text_spaced(draw_main, (cx, y_info + 85), t_dat, f_info, tekst_boja, spacing=ls_info, anchor="mm")
        draw_text_spaced(draw_main, (cx, y_info + 170), t_koor, f_info, tekst_boja, spacing=ls_info, anchor="mm")

        # Ako je kvačica za Mjesec aktivna, proračunaj i nacrtaj ga desno od info bloka
        if podaci.get('prikazi_mjesec') == 'on':
            osvijetljenost, smer = izracunaj_fazu_mjeseca(t)
            nacrtaj_mjesec(draw_main, cx + 500, y_info + 85, 75, osvijetljenost, smer, okvir_boja, bg_boja)

    except Exception as e:
        print(f"Greška prilikom ispisa teksta ili Mjeseca: {e}")

    putanja = os.path.join('static', 'preview.png')
    img.save(putanja, quality=100)
    return putanja

@app.route('/')
def index():
    fontovi = []
    for korijen, direktoriji, fajlovi in os.walk(FONTS_DIR):
        for f in fajlovi:
            if f.endswith(('.ttf', '.otf')):
                relativna_putanja = os.path.relpath(os.path.join(korijen, f), FONTS_DIR)
                relativna_putanja = relativna_putanja.replace('\\', '/')
                fontovi.append(relativna_putanja)
                
    fontovi.sort()
    return render_template('index.html', fontovi=fontovi)

@app.route('/update', methods=['POST'])
def update():
    path = napravi_starmap_pro(request.form.to_dict())
    return jsonify({"image_url": f"/{path}?v={time.time()}"})

if __name__ == '__main__':
    app.run(debug=True)