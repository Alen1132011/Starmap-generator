# Starmap Generator

A web app that generates personalized astronomical posters — enter a date, time, and location, and it draws the exact star positions for that moment, packaged into a print-ready poster.

Built with Flask, Skyfield for the astronomical calculations, and Pillow for the actual drawing.

> **Before you start**
>
> - If the text doesn't appear on the poster immediately, **that's completely normal**. Fill in **all required fields** (date, time, location, coordinates, etc.). The poster is generated only after enough information is provided.
> - If the text is still missing after filling everything in, **try selecting a different font**. Some fonts may not support every character or may fail to load depending on your system.

---

## Live Demos

The application is currently available on two live web hosting services:

1. **[alen.hackclub.app](https://alen.hackclub.app/)** *(Official Hack Club Nest — Recommended)*
   - Powered by a persistent Linux container on Hack Club Nest.
   - **Instant access (0s cold start)** with permanent storage and unlimited execution time for high-resolution renderings.

2. **[starmap-generator.onrender.com](https://starmap-generator.onrender.com/)** *(Secondary Demo)*
   - Hosted on Render's free tier.
   - *May take 30–50 seconds to wake up if inactive.*

---

## Local Version vs. Online Version (Important Note)

The main focus of this project was on developing a high-quality, stable, and secure web application ready for production. Because of this, certain differences exist between running the app locally and using the online versions:

- **Local Version (Lite / Demo Mode):**
  To protect the unique design and optimize the code for evaluation, the local version runs in a secure mode. In this mode, advanced toggle options (grid, constellation lines, moon phase, decorative border) are disabled, and custom color selection via the color picker is restricted.

  Instead, the application automatically applies **3 predefined official templates (Classic Navy, Midnight Black, and Minimalist White)** in full print-ready resolution (2400×3400).

- **Online Versions (Full Premium):**
  If you want to try absolutely all features without any restrictions—including custom color picking, heart shape, moon phases, celestial grid, constellation lines, and decorative borders—visit one of the live versions:

  - **https://alen.hackclub.app/**
  - **https://starmap-generator.onrender.com/**

---

## Features

- Generates a sky map based on the date, time, and geographic coordinates (latitude/longitude)
- Uses the Hipparcos star catalog (down to magnitude 6.5) for an accurate star field
- Draws constellation lines connecting recognizable star patterns *(Online/Premium only)*
- Shows the Moon phase for the selected date, calculated astronomically *(Online/Premium only)*
- Optional celestial grid overlay *(Online/Premium only)*
- Two poster shapes: **Circle** or **Heart** *(Heart is Online/Premium only)*
- Customizable text (title, subtitle, location, date):
  - Font
  - Size
  - Letter spacing
  - Uppercase / lowercase
- Three official color presets for local use
- Fully customizable colors online (background, border, stars, text)
- Account system (register/login) so users can save and manage posters

---

## Requirements

- Python **3.10+**
- pip
- A few hundred MB of free disk space

On the first run Skyfield automatically downloads:

- `de421.bsp`
- Hipparcos star catalog

---

# Local Installation

## 1. Clone the repository

```bash
git clone https://github.com/Alen1132011/Starmap-generator.git
cd Starmap-generator
```

## 2. Create a virtual environment (recommended)

```bash
python -m venv venv
```

Activate it:

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows (Command Prompt)

```cmd
venv\Scripts\activate.bat
```

### Windows (PowerShell)

```powershell
venv\Scripts\Activate.ps1
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Run the application

```bash
python app.py
```

On first startup the application automatically:

- Creates `starmap.db`
- Creates the `fonts/` folder (if missing)
- Creates the `static/` folder (if missing)
- Downloads:
  - Hipparcos catalog
  - `de421.bsp`

*(Only happens once.)*

---

## 5. Open your browser

```
http://127.0.0.1:5000
```

---

# Fonts

Want to use your own fonts?

Simply place any `.ttf` or `.otf` file into the `fonts/` folder.

The application automatically scans the folder and adds new fonts to the font selector on the next startup.

---

# Notes

If you deploy this yourself, consider:

- Disabling Flask debug mode
- Using a secure `SECRET_KEY`
- Replacing SQLite with PostgreSQL (or another production database)
- Setting the environment variable:

```text
VERZIJA_APLIKACIJE=PREMIUM_PRODUKCIJA
```

to unlock the full feature set.

---

# Project Structure

```text
Starmap-generator/
├── app.py              # Flask backend, astronomy calculations and rendering
├── requirements.txt    # Python dependencies
├── fonts/              # Custom fonts (.ttf/.otf)
├── templates/          # HTML templates
└── static/             # Generated poster previews
```

---

# Gallery

Here are a few example posters created with the generator.

<img width="2400" height="3400" alt="preview (1)" src="https://github.com/user-attachments/assets/7533eec4-4779-452d-be1c-420e0ecefc58" />
<img width="2400" height="3400" alt="preview" src="https://github.com/user-attachments/assets/f149865d-2a05-4adb-8737-5c02a0002ed1" />

---

# A Small Personal Note

This project ended up being much bigger than I originally expected.

I spent a lot of time learning **Skyfield**, astronomical coordinate systems, poster rendering with **Pillow**, and putting everything together into a complete web application.

If the **Hack Club** team is reading this: thank you for taking the time to check it out—and for providing the **Hack Club Nest** infrastructure that keeps the application running 24/7.

Building this project taught me a tremendous amount. I encountered many challenges, rewrote large parts of the code several times, and learned a lot throughout the process.

I'm proud of the final result, and I hope you enjoy using it as much as I enjoyed building it.
