#ifndef HUFFMAN_HPP
#define HUFFMAN_HPP

#include <string>
#include <queue>
#include <unordered_map>
#include <memory>

struct HuffmanNode {
    char data;
    unsigned frequency;
    std::shared_ptr<HuffmanNode> left, right;
    
    HuffmanNode(char data, unsigned freq) : 
        data(data), frequency(freq), left(nullptr), right(nullptr) {}
};

class HuffmanCoding {
public:
    void compress(const std::string& input_file, const std::string& output_file);
    void decompress(const std::string& input_file, const std::string& output_file);

private:
    std::unordered_map<char, std::string> huffman_codes;
    
    struct CompareNodes {
        bool operator()(const std::shared_ptr<HuffmanNode>& a, 
                       const std::shared_ptr<HuffmanNode>& b) {
            return a->frequency > b->frequency;
        }
    };

    std::shared_ptr<HuffmanNode> buildHuffmanTree(const std::string& text);
    void generateHuffmanCodes(std::shared_ptr<HuffmanNode> root, 
                            const std::string& code);
    std::string readFile(const std::string& filename);
    void writeFile(const std::string& filename, const std::string& content);
};

#endif 