# RubiksCV

A computer vision-powered Rubik's Cube solver that uses your webcam to scan, detect colors, and solve any standard 3x3 Rubik's Cube in real-time.

## Table of Contents

- [What is RubiksCV?](#what-is-rubikscv)
- [How It Works](#how-it-works)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
  - [Web Version](#web-version)
  - [Desktop Version](#desktop-version)
- [Understanding the Code](#understanding-the-code)
- [HSV Color Calibration](#hsv-color-calibration)
- [Cube Notation](#cube-notation)
- [Troubleshooting](#troubleshooting)
- [Technologies Used](#technologies-used)

---

## What is RubiksCV?

RubiksCV is an application that helps you solve a physical Rubik's Cube using computer vision. Instead of manually entering the cube's state, you simply show each face of your cube to a webcam. The application:

1. Detects the 9 colored stickers on each face
2. Builds a complete digital representation of your cube
3. Calculates the optimal solution using the Kociemba algorithm
4. Guides you through each move with visual arrows

The project includes two versions:
- **Web Version**: Runs in your browser, accessible from any device with a camera
- **Desktop Version**: Native OpenCV application with real-time visualization

---

## How It Works

### Step 1: Color Detection

When you point your webcam at a cube face, the application samples 9 points in a 3x3 grid pattern. Each point's color is analyzed using the HSV (Hue, Saturation, Value) color space, which is more reliable for color detection than RGB.

The `classify_hue()` function determines which of the 6 cube colors (White, Yellow, Red, Orange, Green, Blue) each sticker represents:

```
HSV Color Ranges:
- White:  Low saturation (S <= 80), high value (V >= 50)
- Red:    Hue 0-4 or 165-180, high saturation
- Orange: Hue 5-20, high saturation
- Yellow: Hue 21-45, high saturation
- Green:  Hue 46-90, high saturation
- Blue:   Hue 91-140, high saturation
```

### Step 2: Building the Cube State

After scanning all 6 faces (U, R, F, D, L, B), the application constructs a 54-character string representing every sticker. The center sticker of each face determines that face's identity.

Example cube string: `UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB` (solved cube)

### Step 3: Solving with Kociemba

The Kociemba two-phase algorithm finds a near-optimal solution (typically 20 moves or fewer). This algorithm:
- Phase 1: Reduces the cube to a subset of positions
- Phase 2: Solves from that subset to the solved state

### Step 4: Move Guidance

The solution is displayed as a sequence of moves. The application shows arrow overlays indicating:
- Which face to turn
- Which direction to turn (clockwise or counter-clockwise)
- Special instructions for back-face moves (rotate the cube first)

---

## Features

| Feature | Web Version | Desktop Version |
|---------|-------------|-----------------|
| Browser-based | Yes | No |
| Real-time preview | Yes | Yes |
| Color detection | Yes | Yes |
| Visual move guidance | Yes | Yes (with arrows) |
| Cube state viewer | In-browser | Separate window |
| Mobile support | Yes | No |
| Offline capable | No | Yes |

---

## Project Structure

```
RubiksCV/
|
|-- app.py                  # Flask web server with REST API
|-- Main.py                 # Desktop scanner and solver
|-- State.py                # Desktop cube state viewer (socket-based)
|-- Calibrator.py           # HSV threshold calibration tool
|
|-- static/                 # Web frontend
|   |-- index.html          # Main web page
|   |-- style.css           # Styling
|   |-- app.js              # Frontend JavaScript
|
|-- Resources/              # Visual assets
|   |-- Colors/             # Colored tiles for state viewer
|   |   |-- white.png
|   |   |-- yellow.png
|   |   |-- red.png
|   |   |-- orange.png
|   |   |-- green.png
|   |   |-- blue.png
|   |
|   |-- U.png, U'.png       # Arrow overlays for each move
|   |-- R.png, R'.png
|   |-- F.png, F'.png
|   |-- D.png, D'.png
|   |-- L.png, L'.png
|   |-- TURN_BACK.png
|
|-- requirements.txt        # Python dependencies
|-- Procfile               # Heroku deployment config
|-- runtime.txt            # Python version specification
```

### File Descriptions

| File | Purpose |
|------|---------|
| `app.py` | Flask web application. Handles image processing, color classification, and cube solving via REST endpoints. |
| `Main.py` | Desktop application entry point. Opens webcam, scans faces, calls solver, and displays move guidance with arrow overlays. |
| `State.py` | Desktop cube visualizer. Connects via socket to Main.py and renders a 2D unfolded view of the current cube state. |
| `Calibrator.py` | HSV calibration utility. Shows trackbars to adjust hue, saturation, and value ranges for color detection tuning. |

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Webcam
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/chiragshirsath/RubiksCV.git
   cd RubiksCV
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   This installs:
   - `Flask` - Web framework
   - `flask-cors` - Cross-origin resource sharing
   - `opencv-python` - Computer vision library
   - `numpy` - Numerical computing
   - `kociemba` - Rubik's Cube solving algorithm
   - `gunicorn` - Production WSGI server

---

## Usage

### Web Version

1. **Start the server**
   ```bash
   python app.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:5001`

3. **Allow camera access**
   Click "Start Camera" and grant permission when prompted

4. **Scan each face**
   - Hold your cube so one face fills the camera view
   - Align the 9 stickers with the detection grid
   - Click the corresponding face button (U, R, F, D, L, B)
   - Repeat for all 6 faces

5. **Solve**
   - Click "Solve Cube"
   - Follow the move sequence displayed on screen
   - Use "Next Move" to advance through the solution

### Desktop Version

The desktop version requires two terminal windows:

**Terminal 1 - Start the State Viewer:**
```bash
python State.py
```
This opens a window showing a 2D representation of your cube.

**Terminal 2 - Start the Scanner:**
```bash
python Main.py
```

**Scanning Process:**
1. Point your webcam at a cube face
2. Press the corresponding key (U, R, F, D, L, B) to scan
3. The terminal shows the detected colors for confirmation
4. Repeat for all 6 faces
5. Press ESC when done scanning

**Solving Process:**
1. The solution appears in the terminal
2. Arrow overlays show which move to make
3. Press SPACE to confirm each move
4. The State Viewer updates in real-time
5. Press ESC to exit at any time

### Keyboard Controls (Desktop)

| Key | Action |
|-----|--------|
| U | Scan Up face |
| R | Scan Right face |
| F | Scan Front face |
| D | Scan Down face |
| L | Scan Left face |
| B | Scan Back face |
| SPACE | Confirm move (during solve) |
| ESC | Exit / Finish scanning |

---

## Understanding the Code

### Color Classification Logic

The `classify_hue()` function in both `app.py` and `Main.py` converts HSV values to cube colors:

```python
def classify_hue(h, s, v):
    # White: Low saturation indicates lack of color
    if s <= 80 and v >= 50:
        return "W"
    
    # Red: Hue wraps around at 0/180
    elif ((h >= 0 and h <= 4) or (h >= 165 and h <= 180)) and s > 80:
        return "R"
    
    # Orange: Just above red in the hue spectrum
    elif h >= 5 and h <= 20 and s > 80:
        return "O"
    
    # Yellow: Bright and distinct
    elif h >= 21 and h <= 45 and s > 80:
        return "Y"
    
    # Green: Mid-range hue
    elif h >= 46 and h <= 90 and s > 80:
        return "G"
    
    # Blue: Upper hue range
    elif h >= 91 and h <= 140 and s > 80:
        return "B"
```

### Cube State Representation

The cube is stored as a dictionary with 6 keys (U, R, F, D, L, B), each containing a list of 9 color codes:

```python
cube_state = {
    'U': ['W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W'],  # Up face
    'R': ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],  # Right face
    'F': ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'],  # Front face
    'D': ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],  # Down face
    'L': ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'],  # Left face
    'B': ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B'],  # Back face
}
```

Sticker positions are indexed 0-8:
```
| 0 | 1 | 2 |
| 3 | 4 | 5 |   (4 is the center)
| 6 | 7 | 8 |
```

### Move Application

The `apply_move()` function simulates a physical move on the digital cube:

1. **Rotate the face** - The 9 stickers on the turned face rotate 90 degrees
2. **Cycle the edges** - Adjacent stickers on neighboring faces shift accordingly

---

## HSV Color Calibration

Different lighting conditions and cube brands may require adjusting the color detection thresholds.

### Using the Calibrator

1. Run the calibration tool:
   ```bash
   python Calibrator.py
   ```

2. A window with 6 trackbars appears:
   - LH/UH - Lower/Upper Hue (0-179)
   - LS/US - Lower/Upper Saturation (0-255)
   - LV/UV - Lower/Upper Value (0-255)

3. Show a sticker to the camera and adjust trackbars until only that color is highlighted in the mask view

4. Record the values for each of the 6 colors

5. Update the `classify_hue()` function in `Main.py` or `app.py` with your new ranges

### Tips for Better Detection

- Use consistent, diffused lighting (avoid harsh shadows)
- Position the cube face parallel to the camera
- Ensure the webcam is in focus
- Avoid reflective surfaces behind the cube
- Clean your cube stickers if worn or dirty

---

## Cube Notation

Standard Rubik's Cube notation used in solutions:

| Move | Description |
|------|-------------|
| U | Up face clockwise (90 degrees) |
| U' | Up face counter-clockwise |
| U2 | Up face 180 degrees |
| R | Right face clockwise |
| R' | Right face counter-clockwise |
| F | Front face clockwise |
| F' | Front face counter-clockwise |
| D | Down face clockwise |
| D' | Down face counter-clockwise |
| L | Left face clockwise |
| L' | Left face counter-clockwise |
| B | Back face clockwise |
| B' | Back face counter-clockwise |

**Face Orientation:**
- Hold the cube with one face toward you (Front)
- Up is the top face
- Right is to your right
- Clockwise means turning as if looking at that face directly

---

## Troubleshooting

### Colors are detected incorrectly

**Problem:** The scanner shows wrong colors for stickers.

**Solutions:**
1. Improve lighting - use bright, even light without shadows
2. Run `Calibrator.py` to tune HSV ranges for your environment
3. Ensure the cube fills most of the camera frame
4. Check that your webcam is producing a clear, focused image

### "Could not solve" error

**Problem:** The solver returns an error after scanning.

**Solutions:**
1. Verify each face was scanned correctly (check terminal output)
2. Ensure the center sticker of each face is a different color
3. Rescan any faces that show incorrect colors
4. Make sure your cube is actually solvable (not disassembled incorrectly)

### Webcam not detected

**Problem:** The application cannot access the camera.

**Solutions:**
1. Check that no other application is using the webcam
2. Verify webcam permissions in your OS settings
3. Try a different USB port (for external webcams)
4. For the web version, ensure you're using HTTPS or localhost

### State Viewer not updating (Desktop)

**Problem:** The State.py window doesn't show cube updates.

**Solutions:**
1. Start State.py before Main.py
2. Ensure port 9999 is not blocked by a firewall
3. Check the terminal for connection errors

### Web version camera not working

**Problem:** Browser doesn't show camera feed.

**Solutions:**
1. Allow camera permissions when prompted
2. Use Chrome, Firefox, or Edge (Safari may have issues)
3. For remote access, HTTPS is required for camera access
4. Check browser console for errors (F12 > Console)

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.10+** | Core programming language |
| **OpenCV** | Image capture, processing, and display |
| **NumPy** | Efficient array operations for image data |
| **Flask** | Web server and REST API |
| **Kociemba** | Two-phase Rubik's Cube solving algorithm |
| **Socket** | Inter-process communication (desktop version) |
| **HTML/CSS/JS** | Web frontend interface |

---

## API Reference (Web Version)

### POST /api/classify-colors

Analyzes an image and returns detected colors.

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
  "colors": ["W", "W", "R", "G", "W", "B", "O", "Y", "W"],
  "positions": [{"x": 100, "y": 100}, ...]
}
```

### POST /api/solve

Solves the cube and returns the solution.

**Request Body:**
```json
{
  "cube_faces": {
    "U": ["W", "W", "W", ...],
    "R": ["R", "R", "R", ...],
    ...
  }
}
```

**Response:**
```json
{
  "solution": "R U R' U'",
  "moves": ["R", "U", "R'", "U'"],
  "expanded_moves": ["R", "U", "R'", "U'"],
  "cube_string": "UUUUUUUUU..."
}
```

### POST /api/apply-move

Applies a move to a cube state.

**Request Body:**
```json
{
  "state": {"U": [...], "R": [...], ...},
  "move": "R"
}
```

**Response:**
```json
{
  "state": {"U": [...], "R": [...], ...}
}
```

---

## License

MIT License - feel free to use, modify, and distribute.

---

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
