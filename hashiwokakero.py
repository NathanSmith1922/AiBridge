import numpy

# This is an example of what the scan_print_map file returns after execution.

MATRIX_CODE = ".123456789abc-|=\"E#"

rowSize = 10
colSize = 10

matrix = numpy.array(
    [
        [0, 4, 0, 9, 0, 0, 8, 0, 0, 6],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 5, 0, 9, 0, 0, 9, 0, 4, 0],
        [0, 0, 0, 0, 0, 2, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 5, 0, 8, 0, 5, 0, 0, 1, 0],
        [0, 0, 3, 0, 0, 0, 7, 0, 0, 7],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 4],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
)


class Coordinate:
    def __init__(self, row, col):
        self.row = row
        self.col = col


class Island:
    def __init__(self, coordinate, size):
        self.coordinate = coordinate
        self.size = size

    # DRAFT FUNCTIONS FOR GETTING ADJACENCIES
    def top(self):
        for i in range(self.coordinate.row, 0, -1):
            node = matrix[i][self.coordinate.col]
            if i != self.coordinate.row and node != 0 and node <= 12:
                return Coordinate(i, self.coordinate.col)
        return Coordinate(None, None)

    def down(self):
        for i in range(self.coordinate.row, rowSize):
            node = matrix[i][self.coordinate.col]
            if i != self.coordinate.row and node != 0 and node <= 12:
                return Coordinate(i, self.coordinate.col)
        return Coordinate(None, None)

    def left(self):
        for i in range(self.coordinate.col, 0, -1):
            node = matrix[self.coordinate.row][i]
            if i != self.coordinate.col and node != 0 and node <= 12:
                return Coordinate(self.coordinate.row, i)
        return Coordinate(None, None)

    def right(self):
        for i in range(self.coordinate.col, colSize):
            node = matrix[self.coordinate.row][i]
            if i != self.coordinate.col and node != 0 and node <= 12:
                return Coordinate(self.coordinate.row, i)
        return Coordinate(None, None)


def getBridgeSize(domain):
    return int(max(0, ((domain - 10) / 2)))

# TESTING FUNCTIONS
# island = Island(Coordinate(row, col), matrix[row][col])

def print_matrix():
    for row in range(rowSize):
        for col in range(colSize):
            print(MATRIX_CODE[matrix[row][col]],end="")
        print()

def main():
    print_matrix()

    for i in range(18):
        print(getBridgeSize(i))

if __name__ == "__main__":
    main()