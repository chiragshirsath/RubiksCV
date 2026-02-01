# RubiksCV

A computer vision-powered Rubik's Cube solver that uses your webcam to scan, analyze, and solve any 3x3 cube in real-time. Available as both a web application and a desktop application.

---

## Table of Contents

1. [What is RubiksCV?](#what-is-rubikscv)
2. [How It Works](#how-it-works)
3. [Features](#features)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Usage](#usage)
   - [Web Version](#web-version)
   - [Desktop Version](#desktop-version)
7. [Understanding Cube Notation](#understanding-cube-notation)
8. [HSV Color Calibration](#hsv-color-calibration)
9. [Project Architecture](#project-architecture)
10. [API Reference (Web Version)](#api-reference-web-version)
11. [Troubleshooting](#troubleshooting)
12. [Tech Stack](#tech-stack)
13. [License](#license)

---

## What is RubiksCV?

RubiksCV is a real-time Rubik's Cube solving assistant. Instead of manually entering your cube's colors, you simply point your webcam at each face of your physical cube. The application:

1. Captures a video frame from your webcam
2. Samples 9 points (one for each sticker) on the visible face
3. Converts each pixel from BGR to HSV color space
4. Classifies each sticker as White, Yellow, Red, Orange, Green, or Blue
5. After all 6 faces are scanned, generates an optimal solution using the Kociemba two-phase algorithm
6. Guides you through each move with visual overlays until your cube is solved

---

## How It Works

### Color Detection Pipeline

```
Webcam Frame → BGR Image → HSV Conversion → 9-Point Sampling → Color Classification
```

The application captures frames from your webcam and converts them from BGR (Blue-Green-Red) to HSV (Hue-Saturation-Value) color space. HSV is more robust for color detection because it separates color information (Hue) from lighting conditions (Value).

For each of the 9 sticker positions on a face, the system samples the HSV values and classifies the color:

| Color  | Hue Range | Saturation | Value |
|--------|-----------|------------|-------|
| White  | Any       | Low (<=80) | High (>=50) |
| Red    | 0-4 or 165-180 | High (>80) | Any |
| Orange | 5-20      | High (>80) | Any |
| Yellow | 21-45     | High (>80) | Any |
| Green  | 46-90     | High (>80) | Any |
| Blue   | 91-140    | High (>80) | Any |

### Solving Algorithm

Once all 6 faces are scanned, the cube state is converted to a 54-character string (9 stickers x 6 faces). This string is passed to the Kociemba two-phase algorithm, which finds a near-optimal solution typically in 20 moves or fewer.

The Kociemba algorithm works in two phases:
1. Phase 1: Reduces the cube to a subset that can be solved with specific moves only
2. Phase 2: Solves the reduced cube optimally

---

## Features

### Core Features
- Real-time webcam color detection using HSV classification
- Kociemba two-phase algorithm for optimal solutions (typically under 20 moves)
- Step-by-step visual guidance with arrow overlays
- Live cube state visualization

### Web Version
- Browser-based camera access (no installation required)
- Works on desktop, tablet, and mobile devices
- RESTful API for color classification and solving
- Deployable to any Python-compatible hosting platform

### Desktop Version
- Native OpenCV windows for low-latency display
- Dual-window setup: scanner + state viewer
- Socket-based real-time state synchronization
- Arrow overlay images for move guidance

---

## Prerequisites

- Python 3.8 or higher
- A webcam
- A physical 3x3 Rubik's Cube
- Good lighting conditions (important for accurate color detection)

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/chiragshirsath/RubiksCV.git
cd RubiksCV
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `Flask==3.0.0` - Web framework
- `flask-cors==4.0.0` - Cross-origin resource sharing
- `opencv-python==4.8.1.78` - Computer vision library
- `numpy>=1.24.0,<2.0.0` - Numerical computing
- `kociemba==1.2.1` - Rubik's Cube solving algorithm
- `gunicorn==21.2.0` - Production WSGI server

---

## Usage

### Web Version

1. Start the Flask server:

```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5001`

3. Click "Start Camera" and allow camera access when prompted

4. Position your cube so one face fills the scanning area

5. Click the face button (U, R, F, D, L, B) to scan that face

6. Repeat for all 6 faces

7. Click "Solve Cube" to generate the solution

8. Follow the step-by-step moves displayed on screen

**Note:** Port 5001 is used by default to avoid conflicts with macOS AirPlay Receiver on port 5000.

### Desktop Version

The desktop version uses two separate windows that communicate via sockets.

**Terminal 1 - Start the State Viewer:**
```bash
python State.py
```
This opens a window showing the unfolded cube state. It listens on port 9999 for state updates.

**Terminal 2 - Start the Scanner:**
```bash
python Main.py
```
This opens the webcam feed with scanning grid overlay.

**Scanning Process:**
1. Position your cube in front of the webcam
2. Press the key corresponding to the face you're scanning:
   - `U` - Up (top face)
   - `D` - Down (bottom face)
   - `F` - Front
   - `B` - Back
   - `L` - Left
   - `R` - Right
3. After scanning all 6 faces, press `ESC`
4. The solution appears as arrow overlays
5. Press `SPACE` to confirm each move and advance
6. Press `ESC` to exit at any time

---

## Understanding Cube Notation

Standard Rubik's Cube notation is used throughout this application:

### Face Names
| Letter | Face | Position |
|--------|------|----------|
| U | Up | Top face |
| D | Down | Bottom face |
| F | Front | Face facing you |
| B | Back | Face away from you |
| L | Left | Left face |
| R | Right | Right face |

### Move Types
| Notation | Meaning |
|----------|---------|
| R | Rotate Right face 90° clockwise |
| R' | Rotate Right face 90° counter-clockwise |
| R2 | Rotate Right face 180° |

The same pattern applies to all faces (U, D, F, B, L, R).

### How to Hold Your Cube
When scanning and solving:
- White face on top (U)
- Green face facing you (F)
- Keep this orientation consistent throughout the solving process

---

## HSV Color Calibration

Color detection accuracy heavily depends on your specific cube colors, camera, and lighting conditions. The default HSV thresholds may not work perfectly for your setup.

### Running the Calibrator

```bash
python Calibrator.py
```

This opens two windows:
1. **Webcam Feed** - Live camera view
2. **Masked Output** - Shows only pixels matching current HSV range

Use the trackbars to adjust:
- **LH/UH** - Lower/Upper Hue (0-179)
- **LS/US** - Lower/Upper Saturation (0-255)
- **LV/UV** - Lower/Upper Value (0-255)

### Calibration Process

For each of the 6 colors:
1. Hold a sticker of that color in front of the camera
2. Adjust the trackbars until only that color appears in the mask
3. Note down the HSV ranges that isolate the color
4. Repeat for all colors

### Updating HSV Values

Edit the `classify_hue()` function in:
- `app.py` (for web version)
- `Main.py` (for desktop version)

Example structure:
```python
def classify_hue(h, s, v):
    # White: Low saturation
    if s <= 80 and v >= 50:
        return "W"
    
    # Red: Hue wraps around 0/180
    elif ((h >= 0 and h <= 4) or (h >= 165 and h <= 180)) and s > 80:
        return "R"
    
    # Orange
    elif h >= 5 and h <= 20 and s > 80:
        return "O"
    
    # Yellow
    elif h >= 21 and h <= 45 and s > 80:
        return "Y"
    
    # Green
    elif h >= 46 and h <= 90 and s > 80:
        return "G"
    
    # Blue
    elif h >= 91 and h <= 140 and s > 80:
        return "B"
    
    else:
        return "O"  # Fallback
```

---

## Project Architecture

```
RubiksCV/
├── app.py              # Flask web server with REST API
├── Main.py             # Desktop scanner and solver
├── State.py            # Desktop cube state visualizer
├── Calibrator.py       # HSV calibration utility
├── requirements.txt    # Python dependencies
├── Procfile            # Heroku deployment configuration
├── runtime.txt         # Python version specification
├── static/             # Web frontend assets
│   ├── index.html      # Main HTML page
│   ├── style.css       # Stylesheet
│   └── app.js          # Frontend JavaScript
└── Resources/          # Desktop version assets
    ├── Colors/         # Sticker tile images (PNG)
    │   ├── white.png
    │   ├── yellow.png
    │   ├── red.png
    │   ├── orange.png
    │   ├── green.png
    │   └── blue.png
    └── *.png           # Move arrow overlays (R.png, U'.png, etc.)
```

### File Descriptions

| File | Purpose |
|------|---------|
| `app.py` | Flask application with endpoints for color classification (`/api/classify-colors`), solving (`/api/solve`), and applying moves (`/api/apply-move`) |
| `Main.py` | Desktop application that handles webcam capture, face scanning, solution generation, and move guidance with arrow overlays |
| `State.py` | Socket server that receives cube state updates and renders a 2D unfolded view of the cube |
| `Calibrator.py` | Utility with trackbars to find optimal HSV ranges for your cube and lighting |

---

## API Reference (Web Version)

### POST /api/classify-colors

Classifies colors from a captured image.

**Request Body:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQ...",
  "debug": false
}
```

**Response:**
```json
{
  "colors": ["W", "W", "W", "W", "W", "W", "W", "W", "W"],
  "positions": [{"x": 160, "y": 120}, ...]
}
```

### POST /api/solve

Generates solution for scanned cube.

**Request Body:**
```json
{
  "cube_faces": {
    "U": ["W","W","W","W","W","W","W","W","W"],
    "R": ["R","R","R","R","R","R","R","R","R"],
    "F": ["G","G","G","G","G","G","G","G","G"],
    "D": ["Y","Y","Y","Y","Y","Y","Y","Y","Y"],
    "L": ["O","O","O","O","O","O","O","O","O"],
    "B": ["B","B","B","B","B","B","B","B","B"]
  }
}
```

**Response:**
```json
{
  "solution": "R U R' U'",
  "moves": ["R", "U", "R'", "U'"],
  "expanded_moves": ["R", "U", "R'", "U'"],
  "cube_string": "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
}
```

### POST /api/apply-move

Applies a move and returns updated state.

**Request Body:**
```json
{
  "state": { "U": [...], "R": [...], ... },
  "move": "R"
}
```

**Response:**
```json
{
  "state": { "U": [...], "R": [...], ... }
}
```

---

## Troubleshooting

### Colors are being misclassified

1. Ensure good, consistent lighting (avoid shadows)
2. Run `Calibrator.py` to find correct HSV ranges
3. Update the `classify_hue()` function with your values
4. Avoid reflective cube surfaces or use a matte cube

### Webcam not working (Web Version)

1. Ensure browser has camera permissions
2. Try a different browser (Chrome recommended)
3. Check if another application is using the camera
4. For HTTPS deployment, ensure valid SSL certificate

### Socket connection refused (Desktop Version)

1. Start `State.py` before `Main.py`
2. Ensure port 9999 is not blocked by firewall
3. If port is in use, modify PORT in both files

### "Could not solve" error

This typically means the scanned cube state is invalid:
1. Re-scan all faces carefully
2. Ensure consistent cube orientation
3. Check that each color appears exactly 9 times
4. Verify center stickers match the face assignments

### Solution doesn't work on physical cube

1. Ensure you're holding the cube with correct orientation (White up, Green front)
2. Follow moves exactly as shown
3. Press SPACE only after completing each physical move
4. Double-check your scanned colors match the actual cube

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.8+ | Core programming language |
| OpenCV | Image capture and processing |
| NumPy | Numerical operations for image data |
| Flask | Web server framework |
| Flask-CORS | Cross-origin resource sharing |
| kociemba | Rubik's Cube solving algorithm |
| Gunicorn | Production WSGI server |
| HTML/CSS/JS | Web frontend |
| Socket | Desktop inter-process communication |
| Pickle | State serialization |

---

## License

MIT License - Feel free to use, modify, and distribute this project.
