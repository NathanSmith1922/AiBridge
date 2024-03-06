import numpy

# This is an example of what the scan_print_map file returns after execution.

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

    def top(self):
        for i in range(self.coordinate.row, 0, -1):
            if i != self.coordinate.row and matrix[i][self.coordinate.col] > 0:
                return Coordinate(i, self.coordinate.col)
        return Coordinate(None, None)

    def down(self):
        for i in range(self.coordinate.row, rowSize):
            if i != self.coordinate.row and matrix[i][self.coordinate.col] > 0:
                return Coordinate(i, self.coordinate.col)
        return Coordinate(None, None)

    def left(self):
        for i in range(self.coordinate.col, 0, -1):
            if i != self.coordinate.col and matrix[self.coordinate.row][i] > 0:
                return Coordinate(self.coordinate.row, i)
        return Coordinate(None, None)

    def right(self):
        for i in range(self.coordinate.col, colSize):
            if i != self.coordinate.col and matrix[self.coordinate.row][i] > 0:
                return Coordinate(self.coordinate.row, i)
        return Coordinate(None, None)


def test_check_adjacencies():
    for row in range(rowSize):
        for col in range(colSize):
            if matrix[row][col] == 0:
                continue
            island = Island(Coordinate(row, col), matrix[row][col])

            print(
                "CHECKING NODE: "
                + str(island.coordinate.row)
                + ", "
                + str(island.coordinate.col)
            )
            print("\tTOP: " + str(island.top().row) + ", " + str(island.top().col))
            print("\tDOWN: " + str(island.down().row) + ", " + str(island.down().col))
            print("\tLEFT: " + str(island.left().row) + ", " + str(island.left().col))
            print("\tRIGHT: " + str(island.right().row) + ", " + str(island.right().col))
            print()


def main():
    test_check_adjacencies()
    print(matrix)


if __name__ == "__main__":
    main()
