from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import base64
import copy
import kociemba
import os

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

def classify_hue(h, s, v):
    """Classify color based on HSV values - optimized for bright colors"""
    # White: Low saturation, high value
    if s <= 80 and v >= 50:
        return "W"
    
    # Check colors in order of specificity to avoid misclassification
    # Priority: Yellow > Orange > Red > Green > Blue
    
    # Yellow: Hue 18-32, MUST have very high value to distinguish from green
    # Yellow is the brightest color - use strict value check
    if h >= 18 and h <= 32:
        if v > 180:  # Very bright - definitely yellow
            return "Y"
        elif v > 140 and s > 100:  # Bright with high saturation
            return "Y"
        elif v > 120 and s > 120:  # Still bright enough
            return "Y"
    
    # Orange: Check BEFORE red to catch bright orange
    # Very bright orange can have hue 0-7, use value to distinguish from red
    if h >= 3 and h <= 19:
        # If very bright (v > 180) and high saturation, it's bright orange
        if v > 180 and s > 100:
            return "O"
        # Standard orange range
        elif s > 80:
            return "O"
    
    # Red: Very narrow range, and typically not as bright as orange
    if (h >= 0 and h <= 2) or (h >= 170 and h <= 180):
        if s > 80:
            return "R"
    # Edge case: hue 3-7 but not bright enough for orange
    elif h >= 3 and h <= 7:
        if v <= 180 and s > 80:  # Not bright enough, likely red
            return "R"
    
    # Green: Hue 35-85, MUST have lower value than yellow
    # If value is too high, it might be yellow misclassified
    if h >= 35 and h <= 85:
        if s > 80:
            # If very bright, might be yellow - check value threshold
            if v > 180:
                # Too bright for green, might be yellow - but hue is wrong
                # Check if it's in yellow-green boundary (33-34)
                if h <= 34:
                    return "Y"  # Yellow-green boundary
                else:
                    return "G"  # Probably green but very bright
            else:
                return "G"  # Normal green
    
    # Blue: Hue 86-130, high saturation
    if h >= 86 and h <= 130 and s > 80:
        return "B"
    
    # Fallback for edge cases
    if s > 60:
        if h >= 18 and h <= 34:
            return "Y" if v > 100 else "G"
        elif h >= 3 and h <= 24:
            return "O"
        elif (h >= 0 and h <= 2) or (h >= 170 and h <= 180):
            return "R"
        elif h >= 35 and h <= 85:
            return "G"
        elif h >= 86 and h <= 130:
            return "B"
    
    # Default to white for low saturation colors
    return "W"

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
    face = move[0]
    modifier = move[1:] if len(move) > 1 else ''
    turns = {'': 1, "'": 3, '2': 2}[modifier]
    state = copy.deepcopy(state)
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
    """Classify colors from an image"""
    try:
        data = request.json
        image_data = data.get('image')
        debug = data.get('debug', False)  # Optional debug mode
        
        # Remove data URL prefix
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        height, width = hsv.shape[:2]
        center_x, center_y = width // 2, height // 2
        
        GRID_SIZE = 3
        SPACING = min(width, height) // 4
        colors = []
        positions = []
        hsv_values = [] if debug else None
        
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x = center_x + (j - 1) * SPACING
                y = center_y + (i - 1) * SPACING
                x = max(0, min(width - 1, x))
                y = max(0, min(height - 1, y))
                
                hsv_pixel = hsv[y, x]
                h, s, v = hsv_pixel
                h_int, s_int, v_int = int(h), int(s), int(v)
                color = classify_hue(h_int, s_int, v_int)
                colors.append(color)
                positions.append({'x': int(x), 'y': int(y)})
                
                if debug:
                    hsv_values.append({'h': h_int, 's': s_int, 'v': v_int, 'color': color})
        
        result = {
            'colors': colors,
            'positions': positions
        }
        if debug:
            result['hsv_values'] = hsv_values
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/solve', methods=['POST'])
def solve():
    """Solve the cube"""
    try:
        data = request.json
        cube_faces = data.get('cube_faces')
        
        if not cube_faces or len(cube_faces) != 6:
            return jsonify({'error': 'All 6 faces must be scanned'}), 400
        
        face_order = ['U', 'R', 'F', 'D', 'L', 'B']
        
        # Build cube string
        color_to_face = {cube_faces[face][4]: face for face in face_order}
        cube_string = ''.join(color_to_face.get(color, '?') for face in face_order for color in cube_faces[face])
        
        # Solve using kociemba
        solution = kociemba.solve(cube_string)
        moves = solution.strip().split()
        
        # Expand moves (handle B moves and double moves)
        expanded_moves = []
        for move in moves:
            if move == "B":
                expanded_moves.extend(["TURN_BACK", "F", "TURN_BACK"])
            elif move == "B'":
                expanded_moves.extend(["TURN_BACK", "F'", "TURN_BACK"])
            elif move == "B2":
                expanded_moves.extend(["TURN_BACK", "F", "F", "TURN_BACK"])
            elif move.endswith("2"):
                expanded_moves.extend([move[0], move[0]])
            else:
                expanded_moves.append(move)
        
        return jsonify({
            'solution': solution,
            'moves': moves,
            'expanded_moves': expanded_moves,
            'cube_string': cube_string
        })
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
