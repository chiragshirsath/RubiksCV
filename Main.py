import cv2
import numpy as np
import os
import copy
import socket
import pickle


def classify_hue(h, s, v):
    # WHITE: S <= 80
    # Allows "yellowish" white to pass as White.
    if s <= 80 and v >= 50:
        return "W"

    # RED: STOPPED AT 4.
    # Your Orange is 8. If Red went to 10, it would eat your Orange.
    # Stopping at 4 forces your Orange to be recognized correctly.
    elif ((h >= 0 and h <= 4) or (h >= 165 and h <= 180)) and s > 80:
        return "R"

    # ORANGE: STARTS AT 5.
    # Your Orange is 8. This range (5 to 20) captures it perfectly.
    elif h >= 5 and h <= 20 and s > 80:
        return "O"

    # YELLOW: 21 to 45.
    # Your Yellow is 33. This places it right in the middle.
    # We expanded the top end to 45 to stop it from looking Green.
    elif h >= 21 and h <= 45 and s > 80:
        return "Y"

    # GREEN: STARTS AT 46.
    # Standard Green is ~60. By starting at 46, we keep it far away 
    # from your Yellow (33).
    elif h >= 46 and h <= 90 and s > 80:
        return "G"

    # BLUE: STARTS AT 91.
    # Catches your Sky Blue (which is usually around 95-100).
    elif h >= 91 and h <= 140 and s > 80:
        return "B"

    else:
        # Fallback
        return "O"

def get_position_for_move(move, frame_size, image_size):
    frame_h, frame_w = frame_size
    if move in ["R", "R'"]:
        return (520, 195)
    elif move in ["L", "L'"]:
        return (200, 195)
    elif move in ["U", "U'"]:
        return (260, 145)
    elif move in ["D", "D'"]:
        return (260, 465)
    else:
        return (250, 240)

def overlay_image(bg, overlay, position):
    h, w = overlay.shape[:2]
    x, y = position
    if x < 0 or y < 0 or x + w > bg.shape[1] or y + h > bg.shape[0]:
        return bg
    if overlay.shape[2] == 4:
        alpha = overlay[:, :, 3] / 255.0
        for c in range(3):
            bg[y:y+h, x:x+w, c] = (1 - alpha) * bg[y:y+h, x:x+w, c] + alpha * overlay[:, :, c]
    else:
        bg[y:y+h, x:x+w] = overlay
    return bg

def draw_arrow_for_move(frame, move):
    image_path = f"Resources/{move}.png"
    h, w = frame.shape[:2]
    size = (150, 150)
    if os.path.exists(image_path):
        overlay = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if overlay is not None:
            position = get_position_for_move(move, (h, w), size)
            frame[:] = overlay_image(frame, overlay, position)
    cv2.putText(frame, f"Move: {move}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)


def expand_moves(solution_str):
    expanded = []
    for move in solution_str.split():
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

def get_required_presses(move):
    if move.endswith("2"):
        return 2 if move[0] != 'B' else 4
    elif move[0] == 'B':
        return 3
    else:
        return 1

def rotate_face(face, turns=1):
    for _ in range(turns % 4):
        face[:] = [
            face[6], face[3], face[0],
            face[7], face[4], face[1],
            face[8], face[5], face[2]
        ]
    return face

def cycle_edges(state, faces, indices, turns=1):
    for _ in range(turns % 4):
        tmp = [state[faces[-1]][i] for i in indices[-1]]
        for i in reversed(range(1, 4)):
            for j in range(3):
                state[faces[i]][indices[i][j]] = state[faces[i - 1]][indices[i - 1][j]]
        for j in range(3):
            state[faces[0]][indices[0][j]] = tmp[j]

def apply_move(state, move):
    face = move[0]
    modifier = move[1:] if len(move) > 1 else ''
    turns = {'': 1, "'": 3, '2': 2}[modifier]
    state = copy.deepcopy(state)
    rotate_face(state[face], turns)
    if face == 'U':
        cycle_edges(state, ['B', 'R', 'F', 'L'], [[0,1,2]]*4, turns)
    elif face == 'D':
        cycle_edges(state, ['F', 'R', 'B', 'L'], [[6,7,8]]*4, turns)
    elif face == 'F':
        cycle_edges(state, ['U', 'R', 'D', 'L'], [[6,7,8], [0,3,6], [2,1,0], [8,5,2]], turns)
    elif face == 'B':
        cycle_edges(state, ['U', 'L', 'D', 'R'], [[2,1,0], [0,3,6], [6,7,8], [8,5,2]], turns)
    elif face == 'L':
        cycle_edges(state, ['U', 'F', 'D', 'B'], [[0,3,6]]*3 + [[8,5,2]], turns)
    elif face == 'R':
        cycle_edges(state, ['U', 'B', 'D', 'F'], [[8,5,2], [0,3,6], [8,5,2], [8,5,2]], turns)
    return state

def print_cube(state):
    for face in ['U', 'R', 'F', 'D', 'L', 'B']:
        print(f"{face}: {state[face]}")

cap = cv2.VideoCapture(0)

GRID_SIZE = 3
SPACING = 160
DOT_RADIUS = 5
face_order = ['U', 'R', 'F', 'D', 'L', 'B']
cube_faces = {}

print("▶️ Press keys: u r f d l b to scan that face")
print("▶️ Press ESC when done")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    if ret:
        frame = cv2.resize(frame, (750, 640))
    height, width = 640, 750
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    center_x, center_y = width // 2, height // 2

    current_face = []
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = center_x + (j - 1) * SPACING
            y = center_y + (i - 1) * SPACING + 50
            hsv_pixel = hsv[y, x]
            h, s, v = hsv_pixel
            color = classify_hue(h, s, v)
            current_face.append(color)
            cv2.circle(frame, (x, y), DOT_RADIUS, (0, 255, 0), -1)
            cv2.putText(frame, color, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("Cube Scanner", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break
    elif chr(key).upper() in face_order:
        face_key = chr(key).upper()
        cube_faces[face_key] = current_face.copy()
        print(f"✅ Scanned {face_key}:")
        for i in range(0, 9, 3):
            print(current_face[i], current_face[i + 1], current_face[i + 2])

cap.release()
cv2.destroyAllWindows()

if len(cube_faces) == 6:
    print("\n🧠 Building cube string for solver...")
    color_to_face = {cube_faces[face][4]: face for face in face_order}
    cube_string = ''.join(color_to_face.get(color, '?') for face in face_order for color in cube_faces[face])
    print("\n🧩 Final cube string:")
    print(cube_string)

    try:
        import kociemba
        solution = kociemba.solve(cube_string)
        print("\n🧩 Solution:")
        print(solution)

        kociemba_moves = solution.strip().split()
        overlay_moves = expand_moves(solution)
        cube_state = {face: cube_faces[face][:] for face in face_order}
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(('localhost', 9999))
            viewer_connected = True
            sock.send(pickle.dumps(cube_state))
        except ConnectionRefusedError:
            print("⚠️ Viewer not running. Continuing without visual updates.")
            viewer_connected = False

        if viewer_connected:
            try:
                sock.send(pickle.dumps(cube_state))
            except Exception as e:
                print("⚠️ Failed to send cube state to viewer:", e)

        cap = cv2.VideoCapture(0)

        current_overlay_step = 0
        logical_step = 0
        presses_remaining = get_required_presses(kociemba_moves[logical_step]) if kociemba_moves else 0

        while current_overlay_step < len(overlay_moves):
            is_ok, frame = cap.read()
            if not is_ok:
                break
            if is_ok:
                frame = cv2.resize(frame, (750, 640))
            overlay_move = overlay_moves[current_overlay_step]
            if overlay_move != "TURN_BACK":
                draw_arrow_for_move(frame, overlay_move)
            else:
                if overlay_move != "TURN_BACK":
                    draw_arrow_for_move(frame, overlay_move)
                else:
                    cv2.putText(frame, "Rotate cube to back", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                    image_path = "Resources/TURN_BACK.png"
                    turn_back_img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
                    if turn_back_img is not None:
                        h, w = frame.shape[:2]
                        x = (w - turn_back_img.shape[1]) // 2
                        y = (h - turn_back_img.shape[0]) // 2
                        frame = overlay_image(frame, turn_back_img, (x, y))

            cv2.imshow("Cube Solver", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord(' '):
                move = kociemba_moves[logical_step]
                print(f"🔁 Step {logical_step+1}: Move {move} - Presses left: {presses_remaining - 1}")
                presses_remaining -= 1
                current_overlay_step += 1

                if presses_remaining == 0:
                    cube_state = apply_move(cube_state, move)
                    print(f"✅ Move {move} completed and applied.")
                    sock.send(pickle.dumps(cube_state))
                    print_cube(cube_state)
                    logical_step += 1
                    if logical_step < len(kociemba_moves):
                        presses_remaining = get_required_presses(kociemba_moves[logical_step])

            if key == 27:
                break

        print("🎉 Cube solved! Showing final state. Press ESC to exit.")
        while True:
            is_ok, frame = cap.read()
            if not is_ok:
                break
            frame = cv2.resize(frame, (750, 640))
            cv2.putText(frame, "Cube Solved!", (220, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            cv2.imshow("Cube Solver", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break

        cap.release()
        cv2.destroyAllWindows()


    except Exception as e:
        print("⚠️ Could not solve:", e)
else:
    print("⚠️ Scan all 6 faces! Scanned faces:", list(cube_faces.keys()))
