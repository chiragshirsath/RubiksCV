# Rubik's Cube Solver (Hybrid Web + C++)

A high-performance Rubik's Cube solver utilizing a **Python/Flask Web Interface** for OpenCV camera scanning and a blazing fast **C++17 Engine** for calculating the solution from scratch.

---

## Key Features

- **Hybrid Architecture**: Beautiful web interface combining HTML/JS with a Python Flask backend, while delegating heavy algorithmic lifting to a custom C++ subprocess.
- **From-Scratch Kociemba Solver (C++)**:
  - Custom implementation of Kociemba's Two-Phase algorithm in C++.
  - In-memory Phase 1 & Phase 2 pruning table generation via BFS on startup in under **0.3 seconds**.
  - Iterative Deepening A* (IDA*) search for optimal moves.
- **Web-based OpenCV Vision**:
  - Python OpenCV processes webcam feeds in the browser.
  - Live grid rendering and HSV color classification (White, Yellow, Red, Orange, Green, Blue).
- **Interactive Playback**:
  - Overlays movement arrows onto the camera feed in the browser.
  - Advance step-by-step using on-screen buttons to solve the cube.

---

## Project Structure

```
RubiksCV/
├── app.py                  # Python Flask web server & OpenCV processor
├── requirements.txt        # Python dependencies
├── start.sh                # Helper script to create venv and run the server
├── Makefile                # C++ compilation configuration
├── static/                 # Web interface (HTML, JS, CSS)
├── Resources/              # Visual assets for arrow overlays
└── src/
    ├── cli_solver.cpp      # C++ CLI wrapper exposing the solver to Python
    ├── solver.cpp          # Kociemba algorithm & coordinate mapping implementation
    └── solver.h            # Header file exposing the solver interface
```

---

## Installation & Setup

### 1. Compile the C++ Solver (macOS)
Ensure you have Xcode Command Line Tools installed (`xcode-select --install`).

Compile the C++ CLI executable:
```bash
make clean && make
```
This generates the `rubiks_solver_cli` binary that the web server will call.

### 2. Setup Python Environment
Ensure Python 3 is installed.

```bash
# Create a virtual environment and activate it
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## How to Run & Use

Start the Flask web server:
```bash
./start.sh
```
*(Or manually via `python app.py`)*

### Using the App
1. Open your browser to `http://localhost:5001`.
2. Allow camera permissions.
3. Hold the Rubik's Cube in front of the camera, aligning the face with the 3x3 grid dots.
4. Click the on-screen buttons (`U`, `R`, `F`, `D`, `L`, `B`) to capture each face.
5. Once all 6 faces are scanned successfully, click **Solve Cube**.
6. The Python backend will invoke the C++ engine to generate the solution instantly.
7. Follow the visual arrow overlays on the web interface to solve the cube!
