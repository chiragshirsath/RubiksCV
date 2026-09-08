# Rubik's Cube Solver (Hybrid AI + C++ Engine)

A high-performance Rubik's Cube solver utilizing a **Python/Flask Web Interface**, a **PyTorch Convolutional Neural Network (CNN)** for edge computer vision, and a dual-solver backend featuring a blazing fast **C++17 Engine** and an experimental **Deep Reinforcement Learning (RL) Agent**.

---

## Key Features

- **Deep Learning Computer Vision**: 
  - Overcomes standard lighting limitations by replacing deterministic HSV thresholding with a custom-trained **PyTorch CNN**. 
  - Dynamically crops webcam feeds, batches tensor inference, and robustly maps physical colors to digital states.
- **Dual-Solver Architecture**: Choose between two completely different backend brains to solve your cube:
  - **⚡ Kociemba (Fast)**: A custom, from-scratch C++ implementation of Kociemba's Two-Phase algorithm that instantly calculates mathematically optimal 20-move solutions via Iterative Deepening A* (IDA*).
  - **🧠 RL Agent (Experimental)**: A custom PyTorch Deep Reinforcement Learning solver built using Autodidactic Iteration (ADI) that evaluates moves via value-guided beam search on correct physical geometry.
- **Interactive Playback**:
  - Step-by-step 2D visualizer that dynamically generates precise SVG arrows showing exactly which slice to turn.
  - Interactive "Next" and "Prev" controls with complete state history to guide you through the optimal solution without confusion.

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
