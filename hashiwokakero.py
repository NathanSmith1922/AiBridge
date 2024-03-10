import numpy

# CONSTANTS
MATRIX_CODE = '.123456789abc-|="E#'
EMPTY_CELL = 0
MINIMUM_DOMAIN = 1
MAXIMUM_DOMAIN = 12
MAP_START_INDEX = -1

TOP = 0
DOWN = 1
LEFT = 2
RIGHT = 3


# This is an temporary example of what the scan_print_map file returns after execution.
# These variables will be provided from said function as a return statement.
n_row = 10
n_col = 10
map = numpy.array(
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


class Cell:
    def __init__(self, row, col) -> None:
        self.row = row
        self.col = col


###########################################################################################


class Island:
    def __init__(self, n_row, n_col, cell, domain) -> None:
        self.n_row = n_row
        self.n_col = n_col
        self.cell = cell
        self.domain = domain

    # PRIVATE FUNCTIONS

    def is_vertical_bridge(value):
        return value > 12 and value % 2 == 1

    def __navigate_vertically(self, map, star_row, end_row, step) -> Cell:
        for row in range(star_row, end_row, step):
            cell = map[row][self.cell.col]
            # if cell > MAXIMUM_DOMAIN and not self.is_vertical_bridge(cell): return None
            if (
                row != self.cell.row
                and cell >= MINIMUM_DOMAIN
                and cell <= MAXIMUM_DOMAIN
            ):
                return Cell(row, self.cell.col)
        return None

    def __navigate_horizontally(self, map, start_col, end_col, step) -> Cell:
        for col in range(start_col, end_col, step):
            cell = map[self.cell.row][col]
            # if cell > MAXIMUM_DOMAIN and self.is_vertical_bridge(cell): return None
            if (
                col != self.cell.col
                and cell >= MINIMUM_DOMAIN
                and cell <= MAXIMUM_DOMAIN
            ):
                return Cell(self.cell.row, col)
        return None

    def __navigate_up(self, map) -> Cell:
        return self.__navigate_vertically(map, self.cell.row, MAP_START_INDEX, -1)

    def __navigate_down(self, map) -> Cell:
        return self.__navigate_vertically(map, self.cell.row, self.n_row, 1)

    def __navigate_left(self, map) -> Cell:
        return self.__navigate_horizontally(map, self.cell.col, MAP_START_INDEX, -1)

    def __navigate_right(self, map) -> Cell:
        return self.__navigate_horizontally(map, self.cell.col, self.n_col, 1)

    # PUBLIC FUNCTIONS

    def get_adjacent_paths(self, map) -> list[Cell]:
        return [
            self.__navigate_up(map),
            self.__navigate_down(map),
            self.__navigate_left(map),
            self.__navigate_right(map),
        ]

    def get_adjacent_count(self, map) -> int:
        return 4 - self.get_adjacent_paths(map).count(None)


###########################################################################################


def initialise_islands(n_row, n_col):
    islands = []
    for row in range(n_row):
        for col in range(n_col):
            if map[row][col] == 0:
                continue
            islands.append(Island(n_row, n_col, Cell(row, col), map[row][col]))
    return islands


###########################################################################################
# ANOTHER FUCKING DRAFT FUNCTION DO NOT JUDGE, THERE'S SO MANY DUPLICATED PIECES OF CODE
###########################################################################################


def simplify(map, n_row, n_col, islands):
    copy = map
    for island in islands:
        if island.domain < 3 and island.get_adjacent_count(copy) == 1:

            direction = 0
            for connections in island.get_adjacent_paths(copy):
                if connections != None:
                    copy = create_bridge(
                        island.cell, copy, n_row, n_col, direction, island.domain
                    )
                direction += 1

        elif (
            island.domain % 3 == 0
            and island.get_adjacent_count(copy) == island.domain / 3
        ):
            direction = 0
            for connections in island.get_adjacent_paths(copy):
                if connections != None:
                    copy = create_bridge(island.cell, copy, n_row, n_col, direction, 3)
                direction += 1

        elif island.get_adjacent_count(copy) == int(island.domain / 3 + 1):

            direction = 0
            for connections in island.get_adjacent_paths(copy):
                if connections != None:
                    copy = create_bridge(island.cell, copy, n_row, n_col, direction, 1)
                direction += 1
    return copy


###########################################################################################
# DRAFT FUNCTION PLEASE DON'T JUDGE THIS IS LITERALLY THE FUCKING WORST CODE
# I DIDN'T WANT TO DO FOUR FUCKING FOR LOOPS SO I MADE A REALLY LONG FUCKING CONDITION
###########################################################################################


def create_bridge(start, map, n_row, n_col, direction, length):

    copy = map

    start_row = start.row if (direction == TOP or direction == DOWN) else start.col
    end_row = (
        MAP_START_INDEX
        if (direction == TOP or direction == LEFT)
        else n_row
        if direction == DOWN
        else n_col
    )
    step = 1 if (direction == DOWN or direction == RIGHT) else -1

    for i in range(start_row, end_row, step):
        row = start.row if not (direction == TOP or direction == DOWN) else i
        col = start.col if (direction == TOP or direction == DOWN) else i

        if row == start.row and col == start.col:
            continue

        cell = copy[row][col]

        if cell > 0 and cell <= 12:
            break
        copy[row][col] = max(
            cell,
            MAXIMUM_DOMAIN + length * 2 - (0 if (direction == TOP or direction == DOWN) else 1),
        )

    return copy


def print_matrix(map):
    for row in range(n_row):
        for col in range(n_col):
            print(MATRIX_CODE[map[row][col]], end="")
        print()


def main():
    islands = initialise_islands(n_row, n_col)
    print_matrix(simplify(map, n_row, n_col, islands))


if __name__ == "__main__":
    main()
