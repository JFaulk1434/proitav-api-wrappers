# C++ Image Drawing Performance Test

This is a C++ implementation of the image drawing functions for performance comparison with the Python version.

## Requirements

- C++ compiler with C++11 support (g++, clang++)
- OpenCV 4.x or OpenCV 3.x

## Installation

### macOS
```bash
brew install opencv
```

### Ubuntu/Debian
```bash
sudo apt-get install libopencv-dev
```

## Compilation

From the `Tools` directory, run:

```bash
make
```

Or manually:
```bash
g++ -std=c++11 -O3 -Wall -o special_functions_cpp special_functions.cpp $(pkg-config --cflags --libs opencv4)
```

If you have OpenCV 3.x instead of 4.x, the Makefile will automatically try both.

## Running

```bash
./special_functions_cpp
```

This will test drawing 60 frames at 1080p, 4K, and 8K resolutions and display performance metrics.

## Cleanup

```bash
make clean
```





