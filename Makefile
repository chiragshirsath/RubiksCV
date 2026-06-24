CXX = g++
CXXFLAGS = -O3 -std=c++17 -Wall

TARGET_CLI = rubiks_solver_cli
OBJS_CLI = src/cli_solver.o src/solver.o

all: $(TARGET_CLI)

$(TARGET_CLI): $(OBJS_CLI)
	$(CXX) $(OBJS_CLI) -o $(TARGET_CLI)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f src/*.o $(TARGET_CLI)
