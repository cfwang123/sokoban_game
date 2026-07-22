CXX = g++
CXXFLAGS = -O3 -std=c++17 -march=native -Wall
TARGET = sokosolve.exe

all: $(TARGET)

$(TARGET): solver.cpp
	$(CXX) $(CXXFLAGS) -o $(TARGET) solver.cpp

clean:
	rm -f $(TARGET) sokosolve

.PHONY: all clean
