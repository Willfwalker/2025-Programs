#include "huffman.hpp"
#include <fstream>
#include <iostream>
#include <bitset>

void HuffmanCoding::compress(const std::string& input_file, 
                           const std::string& output_file) {
    std::string text = readFile(input_file);
    if (text.empty()) return;

    // Build Huffman tree
    auto root = buildHuffmanTree(text);
    
    // Generate Huffman codes
    huffman_codes.clear();
    generateHuffmanCodes(root, "");

    // Create compressed binary string
    std::string compressed;
    for (char c : text) {
        compressed += huffman_codes[c];
    }

    // Convert binary string to bytes and write to file
    std::ofstream out(output_file, std::ios::binary);
    
    // First write the Huffman table
    size_t table_size = huffman_codes.size();
    out.write(reinterpret_cast<const char*>(&table_size), sizeof(table_size));
    
    for (const auto& pair : huffman_codes) {
        out.write(&pair.first, sizeof(char));
        size_t code_length = pair.second.length();
        out.write(reinterpret_cast<const char*>(&code_length), sizeof(code_length));
        out.write(pair.second.c_str(), code_length);
    }

    // Write compressed data
    size_t padding = 8 - (compressed.length() % 8);
    if (padding == 8) padding = 0;
    
    out.write(reinterpret_cast<const char*>(&padding), sizeof(padding));
    
    // Convert binary string to bytes
    for (size_t i = 0; i < compressed.length(); i += 8) {
        std::bitset<8> bits(compressed.substr(i, 8));
        char byte = static_cast<char>(bits.to_ulong());
        out.write(&byte, 1);
    }
    
    out.close();
}

void HuffmanCoding::decompress(const std::string& input_file, 
                             const std::string& output_file) {
    std::ifstream in(input_file, std::ios::binary);
    if (!in) return;

    // Read Huffman table
    size_t table_size;
    in.read(reinterpret_cast<char*>(&table_size), sizeof(table_size));

    std::unordered_map<std::string, char> reverse_codes;
    for (size_t i = 0; i < table_size; i++) {
        char c;
        size_t code_length;
        in.read(&c, sizeof(char));
        in.read(reinterpret_cast<char*>(&code_length), sizeof(code_length));
        
        char* code = new char[code_length + 1];
        in.read(code, code_length);
        code[code_length] = '\0';
        
        reverse_codes[std::string(code)] = c;
        delete[] code;
    }

    // Read padding information
    size_t padding;
    in.read(reinterpret_cast<char*>(&padding), sizeof(padding));

    // Read compressed data
    std::string binary;
    char byte;
    while (in.read(&byte, 1)) {
        binary += std::bitset<8>(byte).to_string();
    }

    // Remove padding
    if (padding > 0) {
        binary = binary.substr(0, binary.length() - padding);
    }

    // Decompress
    std::string decompressed;
    std::string current_code;
    for (char bit : binary) {
        current_code += bit;
        if (reverse_codes.find(current_code) != reverse_codes.end()) {
            decompressed += reverse_codes[current_code];
            current_code.clear();
        }
    }

    writeFile(output_file, decompressed);
    in.close();
}

std::shared_ptr<HuffmanNode> HuffmanCoding::buildHuffmanTree(const std::string& text) {
    std::unordered_map<char, unsigned> freq;
    for (char c : text) freq[c]++;

    std::priority_queue<std::shared_ptr<HuffmanNode>, 
                       std::vector<std::shared_ptr<HuffmanNode>>, 
                       CompareNodes> pq;

    for (const auto& pair : freq) {
        pq.push(std::make_shared<HuffmanNode>(pair.first, pair.second));
    }

    while (pq.size() > 1) {
        auto left = pq.top(); pq.pop();
        auto right = pq.top(); pq.pop();

        auto parent = std::make_shared<HuffmanNode>('\0', 
                                                  left->frequency + right->frequency);
        parent->left = left;
        parent->right = right;
        pq.push(parent);
    }

    return pq.top();
}

void HuffmanCoding::generateHuffmanCodes(std::shared_ptr<HuffmanNode> root, 
                                       const std::string& code) {
    if (!root) return;

    if (!root->left && !root->right) {
        huffman_codes[root->data] = code;
    }

    generateHuffmanCodes(root->left, code + "0");
    generateHuffmanCodes(root->right, code + "1");
}

std::string HuffmanCoding::readFile(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (!file) {
        std::cerr << "Error opening file: " << filename << std::endl;
        return "";
    }
    return std::string((std::istreambuf_iterator<char>(file)),
                       std::istreambuf_iterator<char>());
}

void HuffmanCoding::writeFile(const std::string& filename, const std::string& content) {
    std::ofstream file(filename, std::ios::binary);
    if (!file) {
        std::cerr << "Error opening file: " << filename << std::endl;
        return;
    }
    file.write(content.c_str(), content.length());
} 