# Starmap Generator

Starmap Generator is a Flask web application that creates printable star map posters based on a specific date, time, and location.

The application uses Skyfield to calculate the positions of stars and Pillow to render the final poster image. It started as a small learning project and gradually grew into a much larger application.

## Live Demo

**Hack Club Nest (recommended)**
https://starmap.alen.hackclub.app/

**Render (backup)**
https://starmap-generator.onrender.com/

The Render version may take around 30–50 seconds to start if it has been inactive.

## Features

* Generate a star map for any date and location
* Uses the Hipparcos star catalog (stars down to magnitude 6.5)
* High-resolution poster rendering (2400×3400)
* Custom title, subtitle, location, and date
* Multiple fonts and adjustable text spacing
* Circle and heart poster layouts
* User accounts for saving posters
* Moon phase, constellation lines, and celestial grid (online version)

## Local Version

The source code in this repository runs in a limited mode.

Some customization features are disabled in the public version, including:

* custom color picker
* moon phase
* constellation lines
* celestial grid
* decorative border
* heart layout

Instead, the local version includes three built-in color themes.

The live demo contains the complete version of the application.

## Requirements

* Python 3.10 or newer
* pip

During the first launch Skyfield downloads the required astronomy data automatically.

## Installation

Clone the repository:

```bash
git clone https://github.com/Alen1132011/Starmap-generator.git
cd Starmap-generator
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it.

Linux/macOS:

```bash
source venv/bin/activate
```

Windows (Command Prompt):

```cmd
venv\Scripts\activate.bat
```

Windows (PowerShell):

```powershell
venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

Open your browser and go to:

```
http://127.0.0.1:5000
```

On the first run the application will automatically:

* create the SQLite database
* create missing folders
* download the Hipparcos catalog
* download the `de421.bsp` ephemeris

This only happens once.

## Fonts

To add your own fonts, place `.ttf` or `.otf` files inside the `fonts` folder.
To add your own fonts, place .ttf or .otf` files inside the fonts folder.

They will appear in the font selector after restarting the application.

## Deployment

If you deploy the application yourself, you should:

* disable Flask debug mode
* use a secure `SECRET_KEY`
* use PostgreSQL (or another production database) instead of SQLite
* set

```text
VERZIJA_APLIKACIJE=PREMIUM_PRODUKCIJA
```

to enable the full feature set.

## Project Structure

```text
Starmap-generator/
├── app.py
├── requirements.txt
├── fonts/
├── templates/
└── static/
```

## Gallery

Example posters created with the generator.

<img width="2400" height="3400" alt="Poster example 1" src="https://github.com/user-attachments/assets/7533eec4-4779-452d-be1c-420e0ecefc58" />

<img width="2400" height="3400" alt="Poster example 2" src="https://github.com/user-attachments/assets/f149865d-2a05-4adb-8737-5c02a0002ed1" />

## About

I started this project because I wanted to learn more about astronomical calculations and image generation in Python.

At first I expected it to be a relatively small Flask project, but it quickly became much more complex than I had planned. While building it I learned how to work with Skyfield, generate high-resolution images with Pillow, and organize a larger Flask application.

There were plenty of bugs, rewrites, and things I had to learn along the way, but that's also what made the project enjoyable to build.

Thanks to Hack Club for providing Nest hosting for the live demo.
