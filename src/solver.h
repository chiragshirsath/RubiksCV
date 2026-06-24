#pragma once
#include <vector>
#include <string>

// Initialize solver tables (safe to call multiple times, will only build once)
void init_kociemba_solver();

// Solve a Rubik's cube from a 54-char string. Returns a vector of space-separated move strings or empty on error.
std::vector<std::string> solve_rubiks_cube(const std::string& face_string);
