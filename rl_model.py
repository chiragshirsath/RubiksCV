"""
rl_model.py — Dual-head Value-Policy network for Rubik's Cube RL solver.

Architecture (based on McAleer et al. "Solving the Rubik's Cube Without Human Knowledge"):
  Input:  324-dim one-hot vector (54 stickers × 6 colors)
  Shared: Linear(324→1024) + BN + ELU → Linear(1024→512) + BN + ELU
  Value:  Linear(512→1)   → scalar state value
  Policy: Linear(512→12)  → action probabilities (12 quarter-turn moves)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class CubeNet(nn.Module):
    """Dual-head neural network for Rubik's Cube solving via ADI."""

    def __init__(self, input_dim=324, hidden1=1024, hidden2=512, n_actions=12):
        super(CubeNet, self).__init__()
        # Shared backbone
        self.fc1 = nn.Linear(input_dim, hidden1)
        self.bn1 = nn.BatchNorm1d(hidden1)
        self.fc2 = nn.Linear(hidden1, hidden2)
        self.bn2 = nn.BatchNorm1d(hidden2)

        # Value head
        self.value_head = nn.Linear(hidden2, 1)

        # Policy head
        self.policy_head = nn.Linear(hidden2, n_actions)

    def forward(self, x):
        x = F.elu(self.bn1(self.fc1(x)))
        x = F.elu(self.bn2(self.fc2(x)))

        value = self.value_head(x)
        policy = F.softmax(self.policy_head(x), dim=-1)

        return value, policy
