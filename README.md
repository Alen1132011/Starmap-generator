# Starmap Generator

A web app that generates personalized astronomical posters — enter a date, time, and location, and it draws the exact star positions for that moment, packaged into a print-ready poster.

Built with Flask, Skyfield for the astronomical calculations, and Pillow for the actual drawing.

> **Before you start**
>
> - If the text doesn't appear on the poster immediately, **that's completely normal**. Fill in **all required fields** (date, time, location, coordinates, etc.). The poster is generated only after enough information is provided.
> - If the text is still missing after filling everything in, **try selecting a different font**. Some fonts may not support every character or may fail to load depending on your system.
> - If you're using the online demo, the first load may take **up to 50 seconds** because it's hosted on Render's free tier. Just wait for the app to wake up.
> - The online demo is intended for testing. If several people generate posters at the same time, or if the server reaches Render's free resource limits, it may restart or temporarily become unavailable.

---

## Live Demo

**Online version (Full Experience):**

**[starmap-generator.onrender.com](https://starmap-generator.onrender.com/)**

> **Note:** Since the app is hosted on Render's free plan, the server goes to sleep after inactivity. The first visit may take around **30–50 seconds** while it starts up. After that, everything works normally.

---

## Local Version vs. Online Version (Important Note)

The main focus of this project was on developing a high-quality, stable, and secure web application (website) ready for production. Because of this, certain differences have been introduced between running the app locally and using the online version:

- **Local Version (Lite / Demo Mode):** To protect the unique design and optimize the code for evaluation, the local version runs in a secure mode. In this mode, advanced toggle options (grid, constellation lines, moon phase, decorative border) are disabled, and custom color selection via the color picker is restricted. Instead, the application automatically applies **3 predefined official templates (Classic Navy, Midnight Black, and Minimalist White)** in full, print-ready resolution (2400x3400). If you want the fastest local experience without waiting for server spin-ups and are satisfied with our 3 beautiful default templates, running it locally is ideal for you!
- **Online Version on Render (Full Premium):** If you want to try absolutely all features without any restrictions — including custom color picking, heart shape, moon phases, celestial grid, constellation lines, and decorative borders — visit our **[Live Demo Page](https://starmap-generator.onrender.com/)** where everything is 100% unlocked!

---

## Features

- Generates a sky map based on the date, time, and geographic coordinates (lat/lon) you enter
- Uses the Hipparcos star catalog (down to magnitude 6.5) for an accurate star field
- Draws constellation lines connecting recognizable star patterns (Online/Premium only)
- Shows the Moon phase for the selected date, calculated astronomically (Online/Premium only)
- Optional celestial grid overlay (Online/Premium only)
- Two poster shapes: circle or heart (Heart is Online/Premium only)
- Customizable text (title, subtitle, location, date) — font, size, letter spacing, case transform (uppercase/lowercase)
- 3 Beautiful color presets for local use, and fully customizable colors for background, border, stars, and text online
- Account system (register/login) so you can save your posters and come back to them later

---

## Requirements

- **Python 3.10+**
- **pip**
- A few hundred MB of free space — Skyfield will download ephemeris data (`de421.bsp`) and the Hipparcos star catalog on first run

---

## Local Installation

### 1. Clone the repository

```bash
git clone [https://github.com/Alen1132011/Starmap-generator.git](https://github.com/Alen1132011/Starmap-generator.git)
cd Starmap-generator
```

### 2. Create a virtual environment (recommended)

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

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

On first run, the app will:

- automatically create `starmap.db`
- create the `fonts/` and `static/` folders if they don't exist
- download the Hipparcos catalog and the `de421.bsp` ephemeris (this only happens once)

### 5. Open your browser

```
[http://127.0.0.1:5000](http://127.0.0.1:5000)
```

---

## Fonts

Want to use your own fonts?

Just drop any `.ttf` or `.otf` files into the `fonts/` folder. The application automatically scans the folder and adds them to the font selector the next time it starts.

---

## Notes

This project is mainly intended for local use or structured web deployment.

The online demo is provided so you can quickly try it out with full features, but running it locally is recommended if:

- you want instant generation with 0s latency
- you want to avoid Render cold starts
- you are satisfied with our 3 pre-designed high-quality color templates

If you deploy this yourself, consider:

- disabling debug mode
- using a secure `SECRET_KEY`
- replacing SQLite with PostgreSQL (or another production database)
- setting the environment variable `VERZIJA_APLIKACIJE` to `PREMIUM_PRODUKCIJA` in your hosting panel to unlock all premium features.

---

## Project Structure

```text
Starmap-generator/
├── app.py              # Flask backend, astronomy calculations and drawing
├── requirements.txt    # Python dependencies
├── fonts/              # Custom fonts (.ttf/.otf)
├── templates/          # HTML templates
└── static/             # Generated poster previews
```

---

## Gallery

Here are a few example posters created with the generator.

<img width="2400" height="3400" alt="preview (1)" src="https://github.com/user-attachments/assets/7533eec4-4779-452d-be1c-420e0ecefc58" />
<img width="2400" height="3400" alt="preview" src="https://github.com/user-attachments/assets/f149865d-2a05-4adb-8737-5c02a0002ed1" />

---

## A Small Personal Note

This project ended up being much bigger than I originally expected. I spent a lot of time learning Skyfield, astronomical coordinate systems, poster rendering with Pillow, and putting everything together into a working web application.

If the **Hack Club** team is reading this: thank you for taking the time to check it out. I genuinely learned a lot while building it, ran into plenty of problems, rewrote large parts of the project more than once, and I'm proud of how it turned out.

I hope you enjoy trying it as much as I enjoyed building it.
```
