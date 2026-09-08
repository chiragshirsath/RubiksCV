"""
rl_solver.py — Beam search solver using trained RL value-policy network.

Uses the trained CubeNet to guide a beam search towards the solved state.
No pycuber dependency — uses pure numpy cube manipulation from rl_utils.

Usage:
    from rl_solver import RLSolver
    solver = RLSolver("rl_model.pth")
    moves = solver.solve("LUULUUBLDRRFDRRUFDRBBFFRUUBFLLBDRRUFDDUFLLFDLRBBBBDLFD")
"""

import torch
import numpy as np
import time
from rl_model import CubeNet
from rl_utils import (
    is_solved, flatten_cube_to_vector, kociemba_string_to_state, apply_move, get_neighbors,
    MOVES, N_ACTIONS
)


class RLSolver:
    def __init__(self, model_path="rl_model.pth"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
        self.model = CubeNet().to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
        self.model.eval()

    def solve(self, cube_string, max_steps=25, beam_width=512, timeout=None):
        """
        Solve a cube using value-guided beam search with policy pruning.

        Args:
            cube_string: 54-char Kociemba format string
            max_steps: Maximum search depth
            beam_width: Number of paths to maintain in beam
            timeout: Max time in seconds before giving up

        Returns:
            List of move strings if solved, None otherwise.
        """
        start_time = time.time()

        try:
            init_state = kociemba_string_to_state(cube_string)
        except ValueError:
            return None

        if is_solved(init_state):
            return []

        # Each beam entry: (state, move_history)
        beam = [(init_state, [])]
        visited = set()
        visited.add(tuple(init_state))

        for step in range(max_steps):
            if timeout and (time.time() - start_time > timeout):
                return None

            # Collect all leaf states for batch prediction
            leaf_encodings = []
            for state, _ in beam:
                leaf_encodings.append(flatten_cube_to_vector(state))

            leaf_tensor = torch.tensor(np.array(leaf_encodings), dtype=torch.float32).to(self.device)

            with torch.no_grad():
                _, policies = self.model(leaf_tensor)
                policies = policies.cpu().numpy()

            # Expand beam: for each state, try top-K policy moves
            candidates = []
            top_k = min(4, N_ACTIONS)  # Try top 4 moves per state

            for i, (state, history) in enumerate(beam):
                policy = policies[i]
                top_actions = np.argsort(policy)[-top_k:][::-1]

                for action_idx in top_actions:
                    new_state = apply_move(state, MOVES[action_idx])
                    state_key = tuple(new_state)

                    if state_key in visited:
                        continue
                    visited.add(state_key)

                    new_history = history + [MOVES[action_idx]]

                    if is_solved(new_state):
                        return new_history

                    candidates.append((new_state, new_history))

            if not candidates:
                return None

            # Score all candidates by value
            cand_encodings = np.array([flatten_cube_to_vector(s) for s, _ in candidates], dtype=np.float32)
            cand_tensor = torch.tensor(cand_encodings).to(self.device)

            with torch.no_grad():
                values, _ = self.model(cand_tensor)
                scores = values.cpu().numpy().flatten()

            # Keep top beam_width candidates
            top_indices = np.argsort(scores)[-beam_width:][::-1]
            beam = [candidates[i] for i in top_indices]

        return None  # Failed to solve within max_steps


def test_solver():
    """Quick test on cubes of increasing scramble depth."""
    import sys
    from rl_utils import scramble, state_to_kociemba_string

    model_path = sys.argv[1] if len(sys.argv) > 1 else "rl_model.pth"

    try:
        solver = RLSolver(model_path)
    except FileNotFoundError:
        print("Model not found. Train first with: python train_rl.py")
        return

    print("Testing RL solver on scrambled cubes...")
    for depth in range(1, 15):
        solved_count = 0
        total = 20

        for _ in range(total):
            state, _ = scramble(depth)
            cube_str = state_to_kociemba_string(state)
            result = solver.solve(cube_str, timeout=3.0)
            if result is not None:
                solved_count += 1

        pct = solved_count / total * 100
        print(f"  Depth {depth:2d}: {solved_count}/{total} solved ({pct:.0f}%)")

        if solved_count == 0:
            print("  → Stopping (0% solve rate)")
            break


if __name__ == "__main__":
    test_solver()
