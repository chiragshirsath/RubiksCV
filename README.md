# Rubik's Cube Solver (Hybrid AI + C++ Engine)

A high-performance Rubik's Cube solver utilizing a **Python/Flask Web Interface**, a **PyTorch Convolutional Neural Network (CNN)** for edge computer vision, and a dual-solver backend featuring a blazing fast **C++17 Engine** and an experimental **Deep Reinforcement Learning (RL) Agent**.

---

## Technical Architecture

This project implements state-of-the-art algorithms from both classical computer science and modern deep learning to solve the Rubik's cube efficiently.

### 1. Deep Learning Computer Vision (PyTorch CNN)
Traditional Rubik's cube solvers rely on hardcoded HSV (Hue, Saturation, Value) color thresholding, which frequently fails in real-world lighting conditions (e.g., confusing shadows on white stickers for grey or blue). 
- **The Solution:** This project replaces deterministic thresholding with a custom-trained **Convolutional Neural Network (CNN)** built in PyTorch. 
- **Pipeline:** The webcam feed is processed via OpenCV to dynamically crop the 3x3 grid into 9 individual sticker images. These patches are grouped into a tensor batch and passed through the CNN, which robustly maps the physical colors to a digital state matrix, regardless of dynamic lighting or shadows.

### 2. The Algorithmic Solver: Kociemba's Two-Phase Algorithm (C++)
The default solver is a custom, from-scratch **C++** implementation of **Herbert Kociemba’s Two-Phase Algorithm**.
- **Phase 1:** Restricts the cube to a mathematical subgroup where edge orientations and corner orientations are solved, and the middle slice edges are in their correct orbit.
- **Phase 2:** Solves the rest of the cube using only a restricted set of moves (`U, D, R2, L2, F2, B2`).
- **Performance:** By generating massive pruning tables via Breadth-First Search (BFS) in memory on startup (taking <0.3 seconds), the C++ engine uses Iterative Deepening A* (IDA*) to guarantee a mathematically optimal or near-optimal solution (≤20 moves) out of the 43 quintillion possible states almost instantly.

### 3. The AI Solver: Deep Reinforcement Learning (PyTorch)
As an experimental alternative to the algorithmic approach, this project features a **Deep Reinforcement Learning Agent** modeled after the breakthrough research paper *"Solving the Rubik's Cube Without Human Knowledge"* (McAleer et al., Autodidactic Iteration).
- **Autodidactic Iteration (ADI):** The neural network learns by generating its own training data. Starting from a solved cube, it randomly scrambles it, and then learns to predict the "distance to solved" (Value) and the "best next move" (Policy) for every state it encounters.
- **Value-Guided Beam Search:** During inference, the AI doesn't just guess one move; it uses the PyTorch model to evaluate and explore the top 512 most promising future paths simultaneously (Beam Width = 512) to find the shortest path to the solved state without any human-programmed heuristics.

---

## Interactive UI & Playback

- **Hybrid Integration:** A beautiful, framework-free web interface combining HTML/JS/SVG with a Python Flask backend.
- **Visualizer:** A step-by-step 2D visualizer dynamically generates precise SVG arrows showing exactly which slice to turn.
- **State History:** Interactive "Next" and "Prev" controls with a complete state history tree guide you through the optimal solution without confusion.

---

## Project Structure

```
RubiksCV/
├── app.py                  # Python Flask web server & OpenCV processor
├── requirements.txt        # Python dependencies
├── start.sh                # Helper script to run the server
├── Makefile                # C++ compilation configuration
├── static/                 # Web interface (HTML, JS, CSS)
├── train_cnn.py            # PyTorch script used to train the vision model
├── train_rl.py             # PyTorch script used to train the ADI Reinforcement Learning agent
├── rl_model.py             # Neural network architecture definitions
├── rl_solver.py            # Value-guided beam search inference
├── rl_utils.py             # Mathematical physics engine & cube state permutations
└── src/
    ├── cli_solver.cpp      # C++ CLI wrapper exposing the solver to Python
    ├── solver.cpp          # Kociemba algorithm & coordinate mapping implementation
    └── solver.h            # Header file exposing the solver interface
```

---

## Installation & Setup

### 1. Compile the C++ Solver (macOS/Linux)
Ensure you have Xcode Command Line Tools or GCC/Clang installed.

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

## Screenshots

### 1. Scan (Camera or Manual)
Capture all 6 faces of the Rubik's Cube using your webcam or click to input manually.
![Scan Phase](docs/scan_camera.png)

### 2. Review
Verify the captured colors against your physical cube, and choose your preferred solver engine (Kociemba or RL Agent).
![Review Phase](docs/review.png)

### 3. Solve
Follow the dynamically generated SVG arrows perfectly mapped to each face slice.
![Solve Phase](docs/solve_move1.png)

---

## How to Run & Use

Start the Flask web server:
```bash
python app.py
```

### Using the App
1. Open your browser to `http://localhost:5001`.
2. **Scan Phase**: Click **▶ Start Camera** to use your webcam, or switch to **Manual Mode** to click the grid and fill colors by hand.
3. Once all 6 faces are captured successfully, click **Solve Cube**.
4. **Review Phase**: Verify the colors. Select either the **Kociemba** or **RL Agent** solver from the dropdown. The backend will instantly calculate the path!
5. **Solve Phase**: Follow the beautiful dynamic SVG arrows to solve your cube step-by-step. Use the **Prev** and **Next Move** buttons to navigate through the history easily!
