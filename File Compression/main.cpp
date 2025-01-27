#include "huffman.hpp"
#include <iostream>

void printUsage() {
    std::cout << "Usage:\n"
              << "  compress:   program -c input_file output_file\n"
              << "  decompress: program -d input_file output_file\n";
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        printUsage();
        return 1;
    }

    std::string mode = argv[1];
    std::string input_file = argv[2];
    std::string output_file = argv[3];

    HuffmanCoding huffman;

    if (mode == "-c") {
        std::cout << "Compressing " << input_file << " to " << output_file << "...\n";
        huffman.compress(input_file, output_file);
        std::cout << "Compression complete!\n";
    }
    else if (mode == "-d") {
        std::cout << "Decompressing " << input_file << " to " << output_file << "...\n";
        huffman.decompress(input_file, output_file);
        std::cout << "Decompression complete!\n";
    }
    else {
        printUsage();
        return 1;
    }

    return 0;
} 