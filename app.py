from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import base64
import copy
import subprocess
import os
import torch
import torchvision.transforms as transforms
from PIL import Image

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

class StickerNet(torch.nn.Module):
    def __init__(self):
        super(StickerNet, self).__init__()
        self.conv1 = torch.nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.bn1 = torch.nn.BatchNorm2d(16)
        self.conv2 = torch.nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.bn2 = torch.nn.BatchNorm2d(32)
        self.pool = torch.nn.MaxPool2d(2, 2)
        self.fc1 = torch.nn.Linear(32 * 8 * 8, 128)
        self.dropout = torch.nn.Dropout(0.5)
        self.fc2 = torch.nn.Linear(128, 6)

    def forward(self, x):
        x = self.pool(torch.nn.functional.relu(self.bn1(self.conv1(x))))
        x = self.pool(torch.nn.functional.relu(self.bn2(self.conv2(x))))
        x = x.view(x.size(0), -1)
        x = torch.nn.functional.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

device = torch.device("cpu")
model = StickerNet()
if os.path.exists("sticker_net.pth"):
    model.load_state_dict(torch.load("sticker_net.pth", map_location=device))
model.eval()

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

COLOR_MAP = {0: "W", 1: "Y", 2: "R", 3: "O", 4: "G", 5: "B"}

def rotate_face(face, turns=1):
    """Rotate a face 90 degrees clockwise (turns times)"""
    face = face[:]
    for _ in range(turns % 4):
        face = [
            face[6], face[3], face[0],
            face[7], face[4], face[1],
            face[8], face[5], face[2]
        ]
    return face

def cycle_edges(state, faces, indices, turns=1):
    """Cycle edges between faces"""
    # Note: state is already a deep copy from apply_move, so we can modify it directly
    for _ in range(turns % 4):
        tmp = [state[faces[-1]][i] for i in indices[-1]]
        for i in reversed(range(1, 4)):
            for j in range(3):
                state[faces[i]][indices[i][j]] = state[faces[i - 1]][indices[i - 1][j]]
        for j in range(3):
            state[faces[0]][indices[0][j]] = tmp[j]
    return state

def apply_move(state, move):
    """Apply a move to the cube state"""
    state = copy.deepcopy(state)
    if move == 'TURN_BACK':
        # Apply y2 rotation
        state['F'], state['B'] = state['B'], state['F']
        state['R'], state['L'] = state['L'], state['R']
        state['U'] = rotate_face(state['U'], 2)
        state['D'] = rotate_face(state['D'], 2)
        return state

    face = move[0]
    modifier = move[1:] if len(move) > 1 else ''
    turns = {'': 1, "'": 3, '2': 2}[modifier]
    state[face] = rotate_face(state[face], turns)
    if face == 'U':
        state = cycle_edges(state, ['B', 'R', 'F', 'L'], [[0,1,2]]*4, turns)
    elif face == 'D':
        state = cycle_edges(state, ['F', 'R', 'B', 'L'], [[6,7,8]]*4, turns)
    elif face == 'F':
        state = cycle_edges(state, ['U', 'R', 'D', 'L'], [[6,7,8], [0,3,6], [2,1,0], [8,5,2]], turns)
    elif face == 'B':
        state = cycle_edges(state, ['U', 'L', 'D', 'R'], [[2,1,0], [0,3,6], [6,7,8], [8,5,2]], turns)
    elif face == 'L':
        state = cycle_edges(state, ['U', 'F', 'D', 'B'], [[0,3,6]]*3 + [[8,5,2]], turns)
    elif face == 'R':
        state = cycle_edges(state, ['U', 'B', 'D', 'F'], [[8,5,2], [0,3,6], [8,5,2], [8,5,2]], turns)
    return state

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/Resources/<path:filename>')
def resources(filename):
    """Serve resources (move images)"""
    return send_from_directory('Resources', filename)

@app.route('/api/classify-colors', methods=['POST'])
def classify_colors():
    """Classify colors from an image using PyTorch CNN"""
    try:
        data = request.json
        image_data = data.get('image')
        
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        height, width = img_rgb.shape[:2]
        center_x, center_y = width // 2, height // 2
        
        GRID_SIZE = 3
        SPACING = min(width, height) // 4
        colors = []
        positions = []
        
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x = center_x + (j - 1) * SPACING
                y = center_y + (i - 1) * SPACING
                x = max(0, min(width - 1, x))
                y = max(0, min(height - 1, y))
                
                # Crop a 32x32 square around the center point (x, y)
                half_size = 16
                y1 = max(0, y - half_size)
                y2 = min(height, y + half_size)
                x1 = max(0, x - half_size)
                x2 = min(width, x + half_size)
                
                crop = img_rgb[y1:y2, x1:x2]
                if crop.shape[0] != 32 or crop.shape[1] != 32:
                    crop = cv2.resize(crop, (32, 32))
                
                pil_img = Image.fromarray(crop)
                tensor = transform(pil_img).unsqueeze(0).to(device)
                
                with torch.no_grad():
                    outputs = model(tensor)
                    _, predicted = torch.max(outputs, 1)
                    pred_idx = predicted.item()
                    color = COLOR_MAP.get(pred_idx, "W")
                
                colors.append(color)
                positions.append({'x': int(x), 'y': int(y)})
        
        result = {
            'colors': colors,
            'positions': positions
        }
        
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------------------------
# RL Solver (lazy-loaded)
# ---------------------------------------------------------------------------
_rl_solver = None

def get_rl_solver():
    """Lazy-load the RL solver to avoid slowing down startup if model is missing."""
    global _rl_solver
    if _rl_solver is None:
        try:
            from rl_solver import RLSolver
            if os.path.exists("rl_model.pth"):
                _rl_solver = RLSolver("rl_model.pth")
                print("✅ RL solver loaded successfully", flush=True)
            else:
                print("⚠️  rl_model.pth not found, RL solver disabled", flush=True)
        except Exception as e:
            print(f"⚠️  Failed to load RL solver: {e}", flush=True)
    return _rl_solver


def expand_moves(moves):
    """Expand solution moves (handle B moves and double moves) for the UI."""
    expanded = []
    for move in moves:
        if move == "B":
            expanded.extend(["TURN_BACK", "F", "TURN_BACK"])
        elif move == "B'":
            expanded.extend(["TURN_BACK", "F'", "TURN_BACK"])
        elif move == "B2":
            expanded.extend(["TURN_BACK", "F", "F", "TURN_BACK"])
        elif move.endswith("2"):
            expanded.extend([move[0], move[0]])
        else:
            expanded.append(move)
    return expanded


def solve_with_kociemba(cube_string):
    """Solve using the C++ Kociemba binary. Returns (solution_str, moves_list) or raises."""
    result = subprocess.check_output(['./rubiks_solver_cli', cube_string], stderr=subprocess.STDOUT)
    solution = result.decode('utf-8').strip()
    moves = solution.strip().split()
    return solution, moves


@app.route('/api/solve', methods=['POST'])
def solve():
    """Solve the cube — tries RL agent first (2s timeout), falls back to Kociemba C++."""
    try:
        data = request.json
        cube_faces = data.get('cube_faces')
        
        if not cube_faces or len(cube_faces) != 6:
            return jsonify({'error': 'All 6 faces must be scanned'}), 400
        
        face_order = ['U', 'R', 'F', 'D', 'L', 'B']
        
        # Build cube string
        color_to_face = {cube_faces[face][4]: face for face in face_order}
        cube_string = ''.join(color_to_face.get(color, '?') for face in face_order for color in cube_faces[face])
        
        requested_solver = data.get('solver', 'kociemba')
        
        if requested_solver == 'rl':
            rl = get_rl_solver()
            if rl is None:
                return jsonify({'error': 'RL model not loaded or missing.'}), 500
                
            import time
            t0 = time.time()
            # Since RL is explicitly requested, we can give it more time (e.g. 5s)
            rl_moves = rl.solve(cube_string, timeout=5.0)
            rl_time = time.time() - t0
            
            if rl_moves is not None:
                solution = ' '.join(rl_moves)
                moves = rl_moves
                expanded_moves = expand_moves(moves)
                print(f"🤖 RL solved in {len(moves)} moves ({rl_time:.2f}s)", flush=True)

                return jsonify({
                    'solution': solution,
                    'moves': moves,
                    'expanded_moves': expanded_moves,
                    'cube_string': cube_string,
                    'solver_used': 'rl',
                    'rl_time_ms': int(rl_time * 1000)
                })
            else:
                print(f"🤖 RL failed ({rl_time:.2f}s)", flush=True)
                return jsonify({'error': 'RL Agent could not solve this scramble (likely too complex, try Kociemba).'}), 400
                
        # --- Default: C++ Kociemba solver ---
        try:
            solution, moves = solve_with_kociemba(cube_string)
            expanded_moves = expand_moves(moves)
            
            return jsonify({
                'solution': solution,
                'moves': moves,
                'expanded_moves': expanded_moves,
                'cube_string': cube_string,
                'solver_used': 'kociemba'
            })
        except subprocess.CalledProcessError as e:
            err_output = e.output.decode('utf-8').strip()
            print(f"DEBUG: Solver error: {err_output}", flush=True)
            if "Cannot identify" in err_output or "Invalid" in err_output or "Unsolvable" in err_output:
                friendly_err = (
                    "Invalid cube state! The camera likely misread a color due to lighting "
                    "(e.g., confusing Orange and Red). Please look at the 2D Cube State map "
                    "carefully, and use the 'Manual Mode' tab to fix any incorrect colors "
                    "before hitting Solve."
                )
                return jsonify({'error': friendly_err}), 400
            return jsonify({'error': f"C++ Solver Error: {err_output}"}), 500
        except FileNotFoundError:
            return jsonify({'error': 'Solver executable not found. Did you compile it using make?'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/apply-move', methods=['POST'])
def apply_move_endpoint():
    """Apply a move and return updated state"""
    try:
        data = request.json
        state = data.get('state')
        move = data.get('move')
        
        if not state or not move:
            return jsonify({'error': 'State and move required'}), 400
        
        new_state = apply_move(state, move)
        return jsonify({'state': new_state})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # Changed default to 5001 to avoid AirPlay conflict
    print(f"🚀 Starting server on http://localhost:{port}")
    print(f"📱 Open this URL in your browser to use the app")
    app.run(host='0.0.0.0', port=port, debug=True)
