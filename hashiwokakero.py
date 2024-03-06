import numpy

# This is an example of what the scan_print_map file returns after execution.
matrix = numpy.array([
    [".", "4", ".", "9", ".", ".", "8", ".", ".", "6"],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],   
    [".", "5", ".", "9", ".", ".", "9", ".", "4", "."],   
    [".", ".", ".", ".", ".", "2", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],   
    [".", "5", ".", "8", ".", "5", ".", ".", "1", "."],   
    [".", ".", "3", ".", ".", ".", "7", ".", ".", "7"],   
    [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],   
    [".", "1", ".", ".", ".", "1", ".", ".", ".", "4"],   
    [".", ".", ".", ".", ".", ".", ".", ".", ".", "."]
])

class Island:
    def __init__(self, size, top, down, left, right):
        self.size = size
        self.top = top
        self.down = down
        self.left = left
        self.right = right


def create_islands():
    for row in range(matrix.size):
        for col in range(matrix[row].size):

            if matrix[row][col] == ".":
                continue
            value = int(matrix[row][col], 16)
            if value > 0 and value < 13:
                matrix[row][col] = Island(matrix[row][col], 0, 0, 0, 0)

def get_adjacent_islands():
    # Four loops stop when you hit the first thing.
    return

def simplify():
    # 
    return

def DFS():
    # Brute-Force
    return


def main():
    create_islands()
    print(matrix)

if __name__ == "__main__":
    main()


