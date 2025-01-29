#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MEMORY_SIZE 64
#define MAX_BLOCKS 16

// Structure to represent a memory block
typedef struct {
    int start;      // Starting position
    int size;       // Size of block
    int allocated;  // 1 if allocated, 0 if free
    char id;        // Identifier for visualization
} MemoryBlock;

// Global variables
char memory[MEMORY_SIZE];
MemoryBlock blocks[MAX_BLOCKS];
int block_count = 0;
char next_id = 'A';

// Function prototypes
void initialize_memory(void);
void visualize_memory(void);
int allocate_memory(int size);
void free_memory(char id);
void print_block_info(void);

// Initialize memory system
void initialize_memory(void) {
    memset(memory, '.', MEMORY_SIZE);
    blocks[0].start = 0;
    blocks[0].size = MEMORY_SIZE;
    blocks[0].allocated = 0;
    blocks[0].id = '.';
    block_count = 1;
}

// Visualize memory layout
void visualize_memory(void) {
    printf("\nMemory Layout (%d units):\n", MEMORY_SIZE);
    
    // Print top border
    printf("+");
    for (int i = 0; i < MEMORY_SIZE; i++) printf("-");
    printf("+\n|");

    // Print memory contents
    for (int i = 0; i < MEMORY_SIZE; i++) {
        printf("%c", memory[i]);
    }
    printf("|\n+");

    // Print bottom border
    for (int i = 0; i < MEMORY_SIZE; i++) printf("-");
    printf("+\n");
}

// Allocate memory block
int allocate_memory(int size) {
    for (int i = 0; i < block_count; i++) {
        if (!blocks[i].allocated && blocks[i].size >= size) {
            // Found a suitable block
            if (blocks[i].size > size && block_count < MAX_BLOCKS) {
                // Split block if there's remaining space
                MemoryBlock new_block;
                new_block.start = blocks[i].start + size;
                new_block.size = blocks[i].size - size;
                new_block.allocated = 0;
                new_block.id = '.';
                
                blocks[i].size = size;
                
                // Insert new block
                for (int j = block_count; j > i + 1; j--) {
                    blocks[j] = blocks[j-1];
                }
                blocks[i + 1] = new_block;
                block_count++;
            }
            
            // Mark block as allocated
            blocks[i].allocated = 1;
            blocks[i].id = next_id;
            
            // Update memory visualization
            for (int j = blocks[i].start; j < blocks[i].start + blocks[i].size; j++) {
                memory[j] = next_id;
            }
            
            next_id++;
            return 1;
        }
    }
    return 0;
}

// Free memory block
void free_memory(char id) {
    for (int i = 0; i < block_count; i++) {
        if (blocks[i].allocated && blocks[i].id == id) {
            blocks[i].allocated = 0;
            blocks[i].id = '.';
            
            // Update memory visualization
            for (int j = blocks[i].start; j < blocks[i].start + blocks[i].size; j++) {
                memory[j] = '.';
            }
            
            // Merge with adjacent free blocks (check previous block first)
            if (i > 0 && !blocks[i - 1].allocated) {
                blocks[i - 1].size += blocks[i].size;
                for (int j = i; j < block_count - 1; j++) {
                    blocks[j] = blocks[j + 1];
                }
                block_count--;
                i--; // Adjust index after merging with previous block
            }
            
            // Then check next block
            if (i < block_count - 1 && !blocks[i + 1].allocated) {
                blocks[i].size += blocks[i + 1].size;
                for (int j = i + 1; j < block_count - 1; j++) {
                    blocks[j] = blocks[j + 1];
                }
                block_count--;
            }
            return;
        }
    }
}

// Print information about memory blocks
void print_block_info(void) {
    printf("\nBlock Information:\n");
    for (int i = 0; i < block_count; i++) {
        printf("Block %d: Start=%d, Size=%d, %s, ID=%c\n",
               i,
               blocks[i].start,
               blocks[i].size,
               blocks[i].allocated ? "Allocated" : "Free",
               blocks[i].id);
    }
}

int main() {
    initialize_memory();
    printf("Memory Allocation Visualizer\n");
    printf("----------------------------\n");
    
    while (1) {
        visualize_memory();
        print_block_info();
        
        printf("\nCommands:\n");
        printf("1. Allocate memory (a <size>)\n");
        printf("2. Free memory (f <id>)\n");
        printf("3. Quit (q)\n");
        printf("Enter command: ");
        
        char cmd;
        scanf(" %c", &cmd);
        
        if (cmd == 'q') {
            break;
        } else if (cmd == 'a') {
            int size;
            scanf("%d", &size);
            if (size > 0 && size <= MEMORY_SIZE) {
                if (allocate_memory(size)) {
                    printf("Successfully allocated %d units\n", size);
                } else {
                    printf("Failed to allocate memory\n");
                }
            } else {
                printf("Invalid size\n");
            }
        } else if (cmd == 'f') {
            char id;
            scanf(" %c", &id);
            free_memory(id);
        }
    }
    
    return 0;
} 