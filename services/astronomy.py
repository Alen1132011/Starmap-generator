utf-8utf-8import math

from skyfield.api import load
from skyfield.data import hipparcos


with load.open(hipparcos.URL) as f:
    stars_df = hipparcos.load_dataframe(f)
    stars_df = stars_df[stars_df["magnitude"] <= 6.5]

eph = load("de421.bsp")

sun = eph["sun"]
moon = eph["moon"]
earth = eph["earth"]

ts = load.timescale()


def get_timescale():
    return ts


def izracunaj_fazu_mjeseca(t):
    pos = earth.at(t)

    sun_pos = pos.observe(sun).apparent()
    moon_pos = pos.observe(moon).apparent()

    angle = sun_pos.separation_from(moon_pos).radians
    illuminated = (1 + math.cos(math.pi - angle)) / 2

    t2 = ts.utc(
        t.utc.year,
        t.utc.month,
        t.utc.day,
        t.utc.hour,
        t.utc.minute + 1
    )

    pos2 = earth.at(t2)

    sun2 = pos2.observe(sun).apparent()
    moon2 = pos2.observe(moon).apparent()

    angle2 = sun2.separation_from(moon2).radians

    direction = 1 if angle2 > angle else -1

    return illuminated, direction