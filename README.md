# 🧊 Rubik's Cube Solver - Web & Desktop Versions

A real-time **Rubik's Cube Solver** that uses your webcam to:

1. Scan each face of a real cube  
2. Classify sticker colors with HSV thresholds  
3. Solve the cube using the [Kociemba two-phase algorithm](https://github.com/hkociemba/RubiksCube-TwophaseSolver)  
4. Guide you through each move with visual feedback  

---

## 🌐 Web Version (NEW!)

The project now includes a **web-based version** that can be deployed to any hosting platform!

### 🚀 Quick Start (Web Version)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the web server**
   ```bash
   python app.py
   ```

3. **Open your browser**
   - Navigate to `http://localhost:5001` (or the port shown in the terminal)
   - Allow camera access when prompted
   - Start scanning faces!
   
   **Note**: The default port is 5001 to avoid conflicts with macOS AirPlay Receiver on port 5000.

### 📦 Deployment Options

#### Option 1: Heroku
1. Install Heroku CLI and login
2. Create a new app: `heroku create your-app-name`
3. Deploy: `git push heroku main`
4. Your app will be live at `https://your-app-name.herokuapp.com`

#### Option 2: Render
1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`
5. Deploy!

#### Option 3: Railway
1. Connect your GitHub repository
2. Railway will auto-detect the Flask app
3. Deploy with one click!

#### Option 4: PythonAnywhere
1. Upload your files via the web interface
2. Create a new web app
3. Point it to `app.py`
4. Reload and access your app!

### 🎥 Web Features

- **Browser-based camera access** - No desktop app needed!
- **Real-time color classification** - Scan faces directly in your browser
- **Interactive cube visualization** - See your cube state in real-time
- **Step-by-step solution guide** - Follow moves one at a time
- **Responsive design** - Works on desktop, tablet, and mobile

---

## 💻 Desktop Version (Original)

The original desktop version using OpenCV windows is still available.

### 🎥 Desktop Features

- **Webcam scanning** of all 6 faces  
- **HSV-based color classification**  
- **Kociemba solver** via the `kociemba` Python package  
- **Arrow overlays** for visual move guidance  
- **Real-time state tracking** after every move  
- **Separate viewer window** rendering the cube state via sockets  

---

## 🧰 Tech Stack & Libraries

### Web Version
- **Flask** – Web framework
- **Flask-CORS** – Cross-origin resource sharing
- **OpenCV** – Image processing on server
- **NumPy** – Numerical operations
- **kociemba** – Cube solving algorithm
- **HTML/CSS/JavaScript** – Frontend interface

### Desktop Version
- **Python 3.10.8+**  
- **OpenCV** – Camera capture, image display, overlays  
- **NumPy** – Numerical operations  
- **kociemba** – Cube solving algorithm  
- **socket** – Real-time communication between solver and viewer  
- **pickle** – Serializing cube state data  

---

## 📁 Project Structure

```
rubiks-cube-solver/
│
├── app.py              # Flask web application (NEW!)
├── Main.py             # Desktop script: scanning, solving & overlay guidance  
├── State.py            # Desktop viewer script: renders current cube state  
├── Calibrator.py       # HSV calibration tool
├── static/             # Web frontend files (NEW!)
│   ├── index.html      # Main web page
│   ├── style.css       # Styling
│   └── app.js          # Frontend JavaScript
├── Resources/          # Static assets
│   ├── Colors/         # PNG tiles for each sticker color
│   └── *.png           # Arrow overlay images
├── requirements.txt    # Python dependencies
├── Procfile           # Heroku deployment config
├── runtime.txt        # Python version for deployment
└── README.md          # This file  
```
---

### 🛠️ HSV Calibration Notice

> ⚠️ **Important:** The default HSV thresholds used to detect sticker colors are tuned for **one specific cube under specific lighting**.  
> Since color perception varies between different Rubik’s Cubes, cameras, and lighting conditions, you **must calibrate the HSV ranges** for accurate detection on your setup.

---

### 🎯 How to Calibrate Sticker Colors

1. **Run the color calibrator tool** (a Python script with HSV trackbars and webcam feed).
2. Show a sticker (e.g., white face) in front of the webcam and adjust sliders until only that color is detected.
3. Note down the **Hue, Saturation, and Value** ranges that isolate each color clearly.
4. Repeat this process for all 6 colors: White, Red, Yellow, Green, Blue, and Orange.

---

### 📝 Where to Update HSV Values

Open `Main.py`, and locate this function:

```python
def classify_hue(h, s, v):
    if h >= 5 and h <= 36 and s >= 9 and s <= 60 and v >= 45 and v <= 179:
        return "W"
    elif h >= 0 and h <= 25 and s >= 156 and s <= 232 and v >= 82 and v <= 143:
        return "R"
    elif h >= 28 and h <= 39 and s >= 146 and s <= 255 and v >= 132 and v <= 194:
        return "Y"
    elif h >= 42 and h <= 160 and s >= 133 and s <= 255 and v >= 97 and v <= 190:
        return "G"
    elif h >= 55 and h <= 121 and s >= 129 and s <= 255 and v >= 26 and v <= 84:
        return "B"
    elif h >= 1 and h <= 85 and s >= 211 and s <= 248 and v >= 75 and v <= 148:
        return "O"
    else:
        return "O"
```
🔧 **Update the HSV ranges** for each color (`h`, `s`, `v`) based on your calibrated values from the color calibrator tool.

---

## 🚀 Getting Started

### Web Version

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the web server**
   ```bash
   python app.py
   ```

3. **Open in browser**
   - Go to `http://localhost:5001` (or the port shown in terminal)
   - **Note**: Port 5001 is used by default to avoid conflicts with macOS AirPlay Receiver on port 5000
   - Click "Start Camera" and allow access
   - Scan each face by clicking the face buttons (U, R, F, D, L, B)
   - Click "Solve Cube" when all 6 faces are scanned
   - Follow the step-by-step solution!

### Desktop Version

1. **Clone the repository**  
   ```bash
   git clone https://github.com/Goddbott/Rubiks-s-Cube-Solver.git
   cd Rubiks-s-Cube-Solver
   ```

2. **Install dependencies**  
   ```bash
   pip install opencv-python numpy kociemba
   ```

3. **Run the viewer** (in one terminal)  
   ```bash
   python State.py
   ```

4. **Run the solver** (in another terminal)  
   ```bash
   python Main.py
   ```

---

## 🎮 Controls

### Web Version
- **Camera**: Click "Start Camera" to begin
- **Scanning**: Click face buttons (U, R, F, D, L, B) to scan each face
- **Solving**: Click "Solve Cube" when all faces are scanned
- **Navigation**: Use "Next Move" and "Apply Move" buttons to follow the solution

### Desktop Version
- **During scanning (Main.py)**  
  - Press `U`, `R`, `F`, `D`, `L`, `B` to scan that face  
  - Press `ESC` once all six faces are scanned  

- **During solving**  
  - Press `SPACE` to confirm each move  
  - Press `ESC` to exit at any time  

---

## 📸 Resources

- `Resources/Colors/` – Sticker tiles for white, yellow, red, orange, green, blue  
- `Resources/*.png` – Overlay arrows for each face turn (e.g., `R.png`, `U'.png`, etc.)  

---

## 🔧 Configuration

### Adjusting HSV Color Detection

The color classification may need adjustment based on your lighting and cube colors. Edit the `classify_hue()` function in:
- **Web version**: `app.py` (line ~9)
- **Desktop version**: `Main.py` (line ~9)

Use `Calibrator.py` to find the right HSV ranges for your setup.

---

## 📝 Notes

- The web version uses your browser's camera API - no desktop app needed!
- HTTPS is required for camera access on most hosting platforms
- The desktop version requires OpenCV and works best on local machines
- Both versions use the same solving algorithm (Kociemba)

---

