CXX = g++
CXXFLAGS = -O3 -std=c++17 -Wall -Wno-narrowing -Wno-write-strings -fpermissive -Isrc/include
LDFLAGS = 

SRCS = $(wildcard src/*.cpp)
OBJS = $(SRCS:.cpp=.o)
TARGET = rubiks_solver_cli

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS) $(LDFLAGS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)
