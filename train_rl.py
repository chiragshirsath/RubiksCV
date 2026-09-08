import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import time

from rl_model import CubeNet
from rl_utils import (
    is_solved, get_neighbors, flatten_cube_to_vector,
    generate_episode, MOVES, N_ACTIONS
)

# Training Hyperparameters matching ADI paper closely
N_ITERATIONS = 200
N_EPISODES = 100       # Generate 100 scrambles
BATCH_SIZE = 128
LR = 0.0001
REWARD_SOLVED = 1.0
REWARD_UNSOLVED = -1.0
INNER_EPOCHS = 10      # Reduced from 20 for speed

def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Training on: {device}")

    model = CubeNet().to(device)
    optimizer = optim.Adam(model.parameters(), lr=LR)
    
    best_loss = float('inf')
    start_time = time.time()

    for iteration in range(1, N_ITERATIONS + 1):
        scramble_depth = min(30, (iteration // 5) + 1)

        # Generate episodes
        all_states = []
        all_target_values = []
        for _ in range(N_EPISODES):
            episode = generate_episode(scramble_depth)
            for i, state in enumerate(episode[:-1]):
                all_states.append(state)
                all_target_values.append(len(episode) - 1 - i)

        if len(all_states) == 0:
            continue

        # Prepare neighbor batch for ADI
        all_neighbor_encodings = []
        all_rewards = []
        for state in all_states:
            neighbors = get_neighbors(state)
            for _, neighbor_state, neighbor_vector in neighbors:
                all_neighbor_encodings.append(neighbor_vector)
                all_rewards.append(REWARD_SOLVED if is_solved(neighbor_state) else REWARD_UNSOLVED)

        neighbor_tensor = torch.tensor(np.array(all_neighbor_encodings), dtype=torch.float32).to(device)
        state_encodings = np.array([flatten_cube_to_vector(s) for s in all_states], dtype=np.float32)

        avg_v = 0
        avg_p = 0
        n_batches = 0

        # The ADI paper does internal epochs over the same generated data
        for _ in range(INNER_EPOCHS):
            with torch.no_grad():
                model.eval()
                neighbor_values, _ = model(neighbor_tensor)
                model.train()
            
            predicted_values = neighbor_values.cpu().numpy().flatten()
            
            target_values = []
            target_policies = []
            sample_weights = []

            for i, s in enumerate(all_states):
                v = predicted_values[i * N_ACTIONS : (i + 1) * N_ACTIONS]
                r = np.array(all_rewards[i * N_ACTIONS : (i + 1) * N_ACTIONS])

                # ADI paper uses: 0.4 * R + V
                r_plus_v = 0.4 * r + v
                
                best_val = np.max(r_plus_v)
                target_values.append(best_val)
                
                # Policy target is argmax
                target_p = np.argmax(r_plus_v)
                target_policies.append(target_p)
                
                # ADI paper uses sample weights: 1 / distance_to_solved
                dist = max(1, all_target_values[i])
                sample_weights.append(1.0 / dist)

            # Normalize values
            target_values = np.array(target_values)
            v_mean = np.mean(target_values)
            v_std = np.std(target_values) + 0.01
            target_values = (target_values - v_mean) / v_std
            
            # Normalize sample weights
            sample_weights = np.array(sample_weights)
            sample_weights = sample_weights * len(sample_weights) / np.sum(sample_weights)

            dataset = TensorDataset(
                torch.tensor(state_encodings, dtype=torch.float32),
                torch.tensor(target_values, dtype=torch.float32),
                torch.tensor(target_policies, dtype=torch.long),
                torch.tensor(sample_weights, dtype=torch.float32)
            )
            dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

            model.train()
            total_v_loss = 0
            total_p_loss = 0

            for batch_states, batch_v_targets, batch_p_targets, batch_weights in dataloader:
                batch_states = batch_states.to(device)
                batch_v_targets = batch_v_targets.to(device)
                batch_p_targets = batch_p_targets.to(device)
                batch_weights = batch_weights.to(device)

                optimizer.zero_grad()
                pred_v, pred_p = model(batch_states)

                # MSE for value, weighted
                v_loss = torch.mean(batch_weights * (pred_v.squeeze() - batch_v_targets)**2)
                
                # CrossEntropy for policy, weighted
                p_loss = torch.mean(batch_weights * nn.CrossEntropyLoss(reduction='none')(pred_p, batch_p_targets))

                loss = v_loss + p_loss
                loss.backward()
                optimizer.step()

                total_v_loss += v_loss.item()
                total_p_loss += p_loss.item()
                n_batches += 1

            avg_v = total_v_loss / len(dataloader)
            avg_p = total_p_loss / len(dataloader)
            
        elapsed = time.time() - start_time

        print(f"[{iteration:3d}/{N_ITERATIONS}] depth={scramble_depth:2d} | "
              f"states={len(all_states):5d} | v_loss={avg_v:.4f} | p_loss={avg_p:.4f} | time={int(elapsed)}s")

        if avg_v + avg_p < best_loss:
            best_loss = avg_v + avg_p
            torch.save(model.state_dict(), "rl_model.pth")
            print("  -> Saved rl_model.pth")

    print("\n✅ Training complete! Model saved to rl_model.pth")
    print(f"Total time: {int(elapsed)}s")

if __name__ == "__main__":
    train()
