#include <iostream>
#include <string>
#include <vector>
#include "solver.h"

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <54_char_cube_string>\n";
        return 1;
    }

    std::string cube_string = argv[1];
    if (cube_string.length() != 54) {
        std::cerr << "Error: Cube string must be exactly 54 characters long.\n";
        return 1;
    }

    try {
        std::vector<std::string> solution = solve_rubiks_cube(cube_string);
        
        // Output space-separated moves
        for (size_t i = 0; i < solution.size(); ++i) {
            std::cout << solution[i];
            if (i < solution.size() - 1) {
                std::cout << " ";
            }
        }
        std::cout << "\n";
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
