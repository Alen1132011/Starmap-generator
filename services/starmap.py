import os
import math
from skyfield.api import load

from PIL import Image, ImageDraw, ImageFont

from services.astronomy import stars_df, izracunaj_fazu_mjeseca
from services.drawing import (
    hex_to_rgb,
    generisi_tacke_srca,
    draw_text_spaced,
    transformisi_tekst,
    nacrtaj_mjesec
)

from services.constellations import VEZE_SAZVIJEZDA


FONTS_DIR = "fonts"


def napravi_starmap_pro(podaci, width=None, height=None, output_path=None):

                                            
    if width is None:
        width = 2400
    if height is None:
        height = 3400

    STATUS_LICENCE = os.environ.get(
        "VERZIJA_APLIKACIJE",
        "DEMO"
    )

    raw_bg = podaci.get(
        "boja_pozadine",
        "#05070d"
    )

    raw_okvir = podaci.get(
        "boja_okvira",
        "#ffffff"
    )

    raw_zvijezda = podaci.get(
        "boja_zvijezda",
        "#ffffff"
    )

    raw_tekst = podaci.get(
        "boja_teksta",
        "#ffffff"
    )


    prikazi_grid = podaci.get("grid") == "on"
    prikazi_lines = podaci.get("lines") == "on"
    prikazi_okvir = podaci.get("okvir") == "on"
    prikazi_mjesec = podaci.get("prikazi_mjesec") == "on"

    oblik = podaci.get(
        "oblik",
        "krug"
    )


    if STATUS_LICENCE != "PREMIUM_PRODUKCIJA":

        prikazi_grid = False
        prikazi_lines = False
        prikazi_okvir = False
        prikazi_mjesec = False

        oblik = "krug"


        bg_lower = raw_bg.lower()

        if bg_lower in [
            "#ffffff",
            "#fff",
            "white"
        ]:

            raw_bg = "#ffffff"
            raw_okvir = "#000000"
            raw_zvijezda = "#000000"
            raw_tekst = "#000000"


        elif bg_lower in [
            "#000000",
            "#000",
            "black"
        ]:

            raw_bg = "#000000"
            raw_okvir = "#ffffff"
            raw_zvijezda = "#ffffff"
            raw_tekst = "#ffffff"


        else:

            raw_bg = "#05070d"
            raw_okvir = "#ffffff"
            raw_zvijezda = "#ffffff"
            raw_tekst = "#ffffff"



    bg_boja = hex_to_rgb(raw_bg)
    okvir_boja = hex_to_rgb(raw_okvir)
    zvijezde_boja = hex_to_rgb(raw_zvijezda)
    tekst_boja = hex_to_rgb(raw_tekst)


    SIRINA = width
    VISINA = height

    cx = width // 2
    cy = height // 3                                                     
    R = min(width, height) * 0.35                                     


    img = Image.new(
        "RGB",
        (SIRINA, VISINA),
        color=bg_boja
    )


    maska_neba = Image.new(
        "L",
        (SIRINA, VISINA),
        0
    )

    draw_maska = ImageDraw.Draw(
        maska_neba
    )


    if oblik == "srce":

        tacke_srca = generisi_tacke_srca(
            cx,
            cy,
            R
        )

        draw_maska.polygon(
            tacke_srca,
            fill=255
        )

    else:

        draw_maska.ellipse(
            [
                cx-R,
                cy-R,
                cx+R,
                cy+R
            ],
            fill=255
        )


    nebo_img = Image.new(
        "RGBA",
        (SIRINA, VISINA),
        (0,0,0,0)
    )


    draw_nebo = ImageDraw.Draw(
        nebo_img,
        "RGBA"
    )


    try:

        y, m, d = map(
            int,
            (
                podaci.get(
                    "datum_raw",
                    "2000 01 01"
                )
                .split()
            )
        )


        h, mn = map(
            int,
            (
                podaci.get(
                    "vrijeme_raw",
                    "00 00"
                )
                .split()
            )
        )


        lon = float(
            podaci.get(
                "lon",
                0
            )
        )

        lat = float(
            podaci.get(
                "lat",
                0
            )
        )


    except:

        y = 2000
        m = 1
        d = 1
        h = 0
        mn = 0
        lon = 0
        lat = 0

    ts = load.timescale()

    t = ts.utc(
        y,
        m,
        d,
        h,
        mn
    )


    lst = (
        18.697374558
        + 24.06570982441908 * (t.ut1 - 2451545.0)
        + lon / 15.0
    ) % 24



    if prikazi_grid:

        grid_col = (
            *zvijezde_boja,
            45
        )


        for lat_deg in range(-75, 76, 15):

            tacke = []

            for lon_deg in range(-90, 91, 2):

                lon_rad = math.radians(lon_deg)
                lat_rad = math.radians(lat_deg)

                imenilac = (
                    1
                    + math.cos(lat_rad)
                    * math.cos(lon_rad)
                )


                if imenilac > 0:

                    x = cx + R * (
                        math.cos(lat_rad)
                        * math.sin(lon_rad)
                    ) / imenilac


                    y_pos = cy - R * (
                        math.sin(lat_rad)
                    ) / imenilac


                    tacke.append(
                        (
                            x,
                            y_pos
                        )
                    )


            if len(tacke) > 1:

                draw_nebo.line(
                    tacke,
                    fill=grid_col,
                    width=3
                )



        for lon_deg in range(-75, 76, 15):

            tacke = []

            for lat_deg in range(-90, 91, 2):

                lon_rad = math.radians(lon_deg)
                lat_rad = math.radians(lat_deg)


                imenilac = (
                    1
                    + math.cos(lat_rad)
                    * math.cos(lon_rad)
                )


                if imenilac > 0:

                    x = cx + R * (
                        math.cos(lat_rad)
                        * math.sin(lon_rad)
                    ) / imenilac


                    y_pos = cy - R * (
                        math.sin(lat_rad)
                    ) / imenilac


                    tacke.append(
                        (
                            x,
                            y_pos
                        )
                    )


            if len(tacke) > 1:

                draw_nebo.line(
                    tacke,
                    fill=grid_col,
                    width=3
                )



    pos_map = {}


    for hid, star in stars_df.iterrows():

        ha = math.radians(
            (
                lst - star["ra_hours"]
            ) * 15
        )


        dec = math.radians(
            star["dec_degrees"]
        )

        lt = math.radians(
            lat
        )


        sin_alt = (
            math.sin(lt)
            * math.sin(dec)
            +
            math.cos(lt)
            * math.cos(dec)
            * math.cos(ha)
        )


        alt = math.asin(
            max(
                -1,
                min(
                    1,
                    sin_alt
                )
            )
        )


        if alt > 0:

            r_px = R * (
                1 - math.degrees(alt) / 90
            )


            cos_az = (
                math.sin(dec)
                -
                math.sin(alt)
                *
                math.sin(lt)
            ) / (
                math.cos(alt)
                *
                math.cos(lt)
            )


            az = math.acos(
                max(
                    -1,
                    min(
                        1,
                        cos_az
                    )
                )
            )


            if math.sin(ha) > 0:

                az = (
                    2 * math.pi
                    -
                    az
                )


            x = cx + r_px * math.sin(az)
            y_star = cy - r_px * math.cos(az)


            pos_map[hid] = (
                x,
                y_star
            )


            mag = star["magnitude"]

            size = max(
                2,
                int(
                    (6.8 - mag)
                    * 2.5
                )
            )


            if mag < 1.5:

                draw_nebo.ellipse(
                    [
                        x-size-5,
                        y_star-size-5,
                        x+size+5,
                        y_star+size+5
                    ],
                    fill=(
                        *zvijezde_boja,
                        50
                    )
                )


            draw_nebo.ellipse(
                [
                    x-size,
                    y_star-size,
                    x+size,
                    y_star+size
                ],
                fill=zvijezde_boja
            )



    if prikazi_lines:

        for start, end in VEZE_SAZVIJEZDA:

            if (
                start in pos_map
                and end in pos_map
            ):

                draw_nebo.line(
                    [
                        pos_map[start],
                        pos_map[end]
                    ],
                    fill=(
                        *zvijezde_boja,
                        180
                    ),
                    width=4
                )



    img.paste(
        nebo_img,
        (0,0),
        mask=maska_neba
    )


    draw_main = ImageDraw.Draw(
        img,
        "RGBA"
    )



    if oblik == "srce":

        draw_main.polygon(
            generisi_tacke_srca(
                cx,
                cy,
                R
            ),
            outline=okvir_boja,
            width=18
        )

    else:

        draw_main.ellipse(
            [
                cx-R,
                cy-R,
                cx+R,
                cy+R
            ],
            outline=okvir_boja,
            width=18
        )



    if prikazi_okvir:

        draw_main.rectangle(
            [
                70,
                70,
                SIRINA-70,
                VISINA-70
            ],
            outline=okvir_boja,
            width=12
        )


        draw_main.rectangle(
            [
                100,
                100,
                SIRINA-100,
                VISINA-100
            ],
            outline=okvir_boja,
            width=4
        )



    font_name = podaci.get(
        "font_choice",
        "arial.ttf"
    )


    font_path = os.path.join(
        FONTS_DIR,
        font_name
    )


    try:

        f_main = ImageFont.truetype(
            font_path,
            140
        )

        f_sub = ImageFont.truetype(
            font_path,
            70
        )

        f_info = ImageFont.truetype(
            font_path,
            52
        )



        y_main = int(
            podaci.get(
                "y_main",
                2450
            )
        )

        y_sub = int(
            podaci.get(
                "y_sub",
                2650
            )
        )

        y_info = int(
            podaci.get(
                "y_info",
                2950
            )
        )



        t_main = transformisi_tekst(
            podaci.get("ime_prezime", ""),
            podaci.get("trans_main", "uppercase")
        )


        t_sub = transformisi_tekst(
            podaci.get("podnaslov", ""),
            podaci.get("trans_sub", "uppercase")
        )


        t_lok = transformisi_tekst(
            podaci.get("lokacija", ""),
            podaci.get("trans_info", "uppercase")
        )


        t_dat = transformisi_tekst(
            podaci.get("datum_txt", ""),
            podaci.get("trans_info", "uppercase")
        )


        t_koor = f"{lat}° N, {lon}° E"



        draw_text_spaced(
            draw_main,
            (cx, y_main),
            t_main,
            f_main,
            tekst_boja,
            int(podaci.get("ls_main", 0))
        )


        draw_text_spaced(
            draw_main,
            (cx, y_sub),
            t_sub,
            f_sub,
            tekst_boja,
            int(podaci.get("ls_sub", 0))
        )


        draw_text_spaced(
            draw_main,
            (cx, y_info),
            t_lok,
            f_info,
            tekst_boja,
            int(podaci.get("ls_info", 0))
        )


        draw_text_spaced(
            draw_main,
            (cx, y_info+85),
            t_dat,
            f_info,
            tekst_boja,
            int(podaci.get("ls_info", 0))
        )


        draw_text_spaced(
            draw_main,
            (cx, y_info+170),
            t_koor,
            f_info,
            tekst_boja,
            int(podaci.get("ls_info", 0))
        )


        if prikazi_mjesec:

            osvijetljenost, smjer = izracunaj_fazu_mjeseca(t)

            nacrtaj_mjesec(
                draw_main,
                cx+500,
                y_info+85,
                75,
                osvijetljenost,
                smjer,
                okvir_boja,
                bg_boja
            )


    except Exception:
        pass



    if output_path is None:
        putanja = os.path.join(
            "static",
            "preview.png"
        )
    else:
        putanja = output_path

    img.save(
        putanja,
        quality=100
    )

    return putanja