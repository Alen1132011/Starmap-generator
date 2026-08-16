import math


def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")

    return tuple(
        int(hex_str[i:i+2], 16)
        for i in (0, 2, 4)
    )


def generisi_tacke_srca(cx, cy, R):
    tacke = []

    for stepen in range(360):
        ang = math.radians(stepen)

        x = 16 * math.sin(ang) ** 3

        y = (
            13 * math.cos(ang)
            - 5 * math.cos(2 * ang)
            - 2 * math.cos(3 * ang)
            - math.cos(4 * ang)
        )

        fx = cx + x * (R * 0.059)
        fy = cy - y * (R * 0.055) - (R * 0.22)

        tacke.append((int(fx), int(fy)))

    return tacke


def draw_text_spaced(draw, position, text, font, fill, spacing=0, anchor="mm"):
    if not text:
        return

    sirine = []

    for char in text:
        sirine.append(font.getbbox(char)[2])

    ukupno = sum(sirine) + spacing * (len(text) - 1)

    cx, cy = position

    if anchor == "mm":
        start_x = cx - ukupno / 2

        bbox = font.getbbox(text)
        visina = bbox[3] - bbox[1]

        start_y = cy - visina / 2

    else:
        start_x = cx
        start_y = cy


    x = start_x

    for char in text:
        draw.text(
            (x, start_y),
            char,
            font=font,
            fill=fill
        )

        x += font.getbbox(char)[2] + spacing


def transformisi_tekst(tekst, transform_tip):
    if transform_tip == "uppercase":
        return tekst.upper()

    if transform_tip == "lowercase":
        return tekst.lower()

    return tekst


def nacrtaj_mjesec(draw, cx, cy, r, osvijetljenost, smjer, boja_mjeseca, boja_bg):

    draw.ellipse(
        [
            cx-r,
            cy-r,
            cx+r,
            cy+r
        ],
        fill=boja_bg,
        outline=boja_mjeseca,
        width=2
    )


    if osvijetljenost < 0.03:
        return


    if osvijetljenost > 0.97:
        draw.ellipse(
            [
                cx-r,
                cy-r,
                cx+r,
                cy+r
            ],
            fill=boja_mjeseca
        )

        return


    k = abs(2 * osvijetljenost - 1)


    if osvijetljenost > 0.5:

        if smjer > 0:
            draw.chord(
                [cx-r, cy-r, cx+r, cy+r],
                270,
                90,
                fill=boja_mjeseca
            )

        else:
            draw.chord(
                [cx-r, cy-r, cx+r, cy+r],
                90,
                270,
                fill=boja_mjeseca
            )


        draw.ellipse(
            [
                cx-r*k,
                cy-r,
                cx+r*k,
                cy+r
            ],
            fill=boja_mjeseca
        )


    else:

        if smjer > 0:

            draw.chord(
                [cx-r, cy-r, cx+r, cy+r],
                270,
                90,
                fill=boja_mjeseca
            )

        else:

            draw.chord(
                [cx-r, cy-r, cx+r, cy+r],
                90,
                270,
                fill=boja_mjeseca
            )


        draw.ellipse(
            [
                cx-r*k,
                cy-r,
                cx+r*k,
                cy+r
            ],
            fill=boja_bg,
            outline=boja_mjeseca,
            width=1
        )