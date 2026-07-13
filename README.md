# ⭐ Starmap Generator

A web app that generates personalized astronomical posters — enter a date, time, and location, and it draws the exact star positions for that moment, packaged into a print-ready poster.

Built with Flask, Skyfield for the astronomical calculations, and Pillow for the actual drawing.

## Live Demo

No hosted demo right now — this project relies on a local SQLite database and downloads star catalog/ephemeris data on first run, so it's honestly a much smoother experience run locally rather than deployed somewhere. Follow the install steps below, it only takes a few minutes.

## Features

- Generates a sky map based on the date, time, and geographic coordinates (lat/lon) you enter
- Uses the Hipparcos star catalog (down to magnitude 6.5) for an accurate star field
- Draws constellation lines connecting recognizable star patterns
- Shows the Moon phase for the selected date (calculated astronomically, not looked up from a table)
- Optional celestial grid overlay
- Two poster shapes: circle or heart
- Customizable text (title, subtitle, location, date) — font, size, letter spacing, case transform (uppercase/lowercase)
- Custom colors for background, border, stars, and text
- Account system (register/login) so you can save your posters and come back to them later

## Requirements

- **Python 3.10+** (Skyfield and newer Pillow releases play nicer with a recent Python)
- **pip**
- A few hundred MB of free space — Skyfield will download ephemeris data (`de421.bsp`) and the Hipparcos star catalog from the internet on first run

## Local Installation

**1. Clone the repo**

```bash
git clone https://github.com/Alen1132011/Starmap-generator.git
cd Starmap-generator
```

**2. Create a virtual environment** (recommended, keeps things clean)

```bash
python -m venv venv
```

Activate it:

```bash
# Linux / macOS
source venv/bin/activate

# Windows (cmd)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the app**

```bash
python app.py
```

On first run, the app will:
- automatically create `starmap.db` (SQLite database for users and saved posters)
- create the `fonts/` and `static/` folders if they don't exist yet
- download the Hipparcos star catalog and `de421.bsp` ephemeris data from the internet (can take a couple of minutes depending on your connection — this only happens once, then it's cached locally)

**5. Open it in your browser**

```
http://127.0.0.1:5000
```

That's it — you're up and running, go make some posters.

## Fonts

Want to use your own fonts for the poster text? Just drop `.ttf` or `.otf` files into the `fonts/` folder — the app scans it automatically and lists them in the dropdown next time you start it up.

## Note

This is a development setup — it runs with `debug=True` and a local SQLite file, which is fine for local use and testing. If you ever wanted to deploy this publicly, you'd want to:
- turn off debug mode
- replace `SECRET_KEY` with something actually secret and unique
- consider a proper database (PostgreSQL, etc.) instead of SQLite

## Project Structure

```
Starmap-generator/
├── app.py              # all backend logic (Flask routes, astronomy, drawing)
├── requirements.txt    # Python dependencies
├── fonts/               # .ttf/.otf fonts for poster text
├── templates/           # HTML templates (frontend)
└── static/              # generated posters (preview.png)
```

---

Built with too much coffee and too many Skyfield docs tabs open. For stardance program ☕🌌
