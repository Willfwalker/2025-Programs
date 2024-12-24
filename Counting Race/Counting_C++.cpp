#include <iostream>
#include <chrono>

int main() {
    // Start timing
    auto start = std::chrono::high_resolution_clock::now();

    for (long long i = 1; i <= 1000000000; i++) {
        // Just count, no printing
    }

    // End timing
    auto end = std::chrono::high_resolution_clock::now();
    
    // Calculate duration in seconds
    std::chrono::duration<double> duration = end - start;
    
    std::cout << "Time taken: " << duration.count() << " seconds" << std::endl;
    
    return 0;
}
