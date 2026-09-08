import numpy as np
from random import choice

# 12 quarter-turn moves
MOVES = ['F', 'B', 'U', 'D', 'L', 'R', "F'", "B'", "U'", "D'", "L'", "R'"]
N_ACTIONS = len(MOVES)

# Permutations derived from Pycuber
PERMS = {
    'U': [6, 3, 0, 7, 4, 1, 8, 5, 2, 45, 46, 47, 12, 13, 14, 15, 16, 17, 9, 10, 11, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 18, 19, 20, 39, 40, 41, 42, 43, 44, 36, 37, 38, 48, 49, 50, 51, 52, 53],
    'R': [0, 1, 20, 3, 4, 23, 6, 7, 26, 15, 12, 9, 16, 13, 10, 17, 14, 11, 18, 19, 29, 21, 22, 32, 24, 25, 35, 27, 28, 51, 30, 31, 48, 33, 34, 45, 36, 37, 38, 39, 40, 41, 42, 43, 44, 8, 46, 47, 5, 49, 50, 2, 52, 53],
    'F': [0, 1, 2, 3, 4, 5, 44, 41, 38, 6, 10, 11, 7, 13, 14, 8, 16, 17, 24, 21, 18, 25, 22, 19, 26, 23, 20, 15, 12, 9, 30, 31, 32, 33, 34, 35, 36, 37, 27, 39, 40, 28, 42, 43, 29, 45, 46, 47, 48, 49, 50, 51, 52, 53],
    'D': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 24, 25, 26, 18, 19, 20, 21, 22, 23, 42, 43, 44, 33, 30, 27, 34, 31, 28, 35, 32, 29, 36, 37, 38, 39, 40, 41, 51, 52, 53, 45, 46, 47, 48, 49, 50, 15, 16, 17],
    'L': [53, 1, 2, 50, 4, 5, 47, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 0, 19, 20, 3, 22, 23, 6, 25, 26, 18, 28, 29, 21, 31, 32, 24, 34, 35, 42, 39, 36, 43, 40, 37, 44, 41, 38, 45, 46, 33, 48, 49, 30, 51, 52, 27],
    'B': [11, 14, 17, 3, 4, 5, 6, 7, 8, 9, 10, 35, 12, 13, 34, 15, 16, 33, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 36, 39, 42, 2, 37, 38, 1, 40, 41, 0, 43, 44, 51, 48, 45, 52, 49, 46, 53, 50, 47]
}

# Create inverse permutations for prime moves
for move in ['U', 'R', 'F', 'D', 'L', 'B']:
    perm = PERMS[move]
    inv_perm = [0] * 54
    for i, p in enumerate(perm):
        inv_perm[p] = i
    PERMS[move + "'"] = inv_perm

def apply_move(state, move):
    """Apply move to a 54-element array or list."""
    perm = PERMS[move]
    return [state[i] for i in perm]

def state_to_kociemba_string(state):
    """Convert state list to string."""
    return "".join(state)

def kociemba_string_to_state(cube_string):
    """Convert Kociemba string to list of characters."""
    return list(cube_string)

def solved_state():
    """Return a solved state string based on center colors."""
    # Centers are at U:4, R:13, F:22, D:31, L:40, B:49
    # In standard Kociemba solved string, the faces are pure.
    return list("U"*9 + "R"*9 + "F"*9 + "D"*9 + "L"*9 + "B"*9)

def is_solved(state):
    """Check if the state is solved."""
    return state == solved_state()

def flatten_cube_to_vector(state):
    """Convert 54-char list to 324-dim RL vector."""
    char_to_color_idx = {
        state[22]: 0, # F center -> green
        state[49]: 1, # B center -> blue
        state[4]: 2,  # U center -> yellow
        state[40]: 3, # L center -> red
        state[13]: 4, # R center -> orange
        state[31]: 5  # D center -> white
    }
    
    kociemba_face_offsets = {
        'U': 0, 'R': 9, 'F': 18, 'D': 27, 'L': 36, 'B': 45
    }
    
    # RL paper extracts in this order
    rl_face_order = ['F', 'B', 'U', 'D', 'L', 'R']
    
    vector = np.zeros(324, dtype=np.float32)
    idx = 0
    for face in rl_face_order:
        offset = kociemba_face_offsets[face]
        for i in range(9):
            char = state[offset + i]
            color_idx = char_to_color_idx[char]
            vector[idx + color_idx] = 1.0
            idx += 6
            
    return vector

def get_neighbors(state):
    """Return list of (action_idx, neighbor_state, neighbor_vector) for all 12 moves."""
    neighbors = []
    for idx, move in enumerate(MOVES):
        new_state = apply_move(state, move)
        neighbors.append((idx, new_state, flatten_cube_to_vector(new_state)))
    return neighbors

def generate_episode(k):
    """Generate a training episode (reversed path from solved)."""
    state = solved_state()
    transformation = [choice(MOVES) for _ in range(k)]
    
    # apply forward
    for move in transformation:
        state = apply_move(state, move)
        
    # generate backward path
    path_states = []
    for move in reversed(transformation):
        path_states.append(state)
        # apply inverse move
        inv_move = move[0] if len(move) == 2 else move + "'"
        state = apply_move(state, inv_move)
        
    path_states.append(state) # include solved state
    return path_states

def scramble(n_moves):
    """Used for testing: returns a state and moves applied."""
    state = solved_state()
    moves_applied = []
    for _ in range(n_moves):
        idx = np.random.randint(N_ACTIONS)
        move = MOVES[idx]
        state = apply_move(state, move)
        moves_applied.append(idx)
    return state, moves_applied

