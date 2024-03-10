import numpy
import time

###############################################################################

# This is an temporary example of what the scan_print_map file returns after
# execution. These variables will be provided from said function as a return
# statement.

n_row = 10
n_col = 10
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

###############################################################################

EMPTY_CELL = 0
DIRECTION_COUNT = 4

MATRIX_CODE = '.123456789abc-|="E#'
MINIMUM_DOMAIN = 1
MAXIMUM_DOMAIN = 12
MAP_START_INDEX = -1

TOP = 0
DOWN = 1
LEFT = 2
RIGHT = 3


class Map:
    def __init__(self, n_row: int, n_col: int, map: list[list[int]]) -> None:
        self.n_row = n_row
        self.n_col = n_col
        self.map = map


class Cell:
    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col


class Island:
    def __init__(self, cell: Cell, domain: int) -> None:
        self.cell = cell
        self.domain = domain

    # O(n)
    def __navigate_direction(self, map: Map, direction: int) -> list[Cell]:
        is_vertical_direction = direction == TOP or direction == DOWN
        is_backwards_navigation = direction == TOP or direction == LEFT

        step = -1 if is_backwards_navigation else 1
        start = (self.cell.row if is_vertical_direction else self.cell.col) + step
        end = (
            MAP_START_INDEX
            if is_backwards_navigation
            else map.n_row
            if direction == DOWN
            else map.n_col
        )

        path = []
        for i in range(start, end, step):
            row = self.cell.row if not is_vertical_direction else i
            col = self.cell.col if is_vertical_direction else i
            cell = map.map[row][col]

            if (
                cell > MAXIMUM_DOMAIN
                and cell % 2 == (0 if is_vertical_direction else 1)
            ) or cell == EMPTY_CELL:
                path.append(Cell(row, col))

            if cell >= MINIMUM_DOMAIN and cell <= MAXIMUM_DOMAIN:
                if len(path) == 0:
                    return None
                return path
        return None

    # O(n)
    def get_adjacent_paths(self, map: Map) -> list[list[Cell]]:
        return [
            self.__navigate_direction(map, TOP),
            self.__navigate_direction(map, DOWN),
            self.__navigate_direction(map, LEFT),
            self.__navigate_direction(map, RIGHT),
        ]

    # O(n)
    def get_adjacent_count(self, map: Map) -> int:
        return DIRECTION_COUNT - self.get_adjacent_paths(map).count(None)


# O(n^2)
def get_islands(map: Map) -> list[Island]:
    islands = []
    for row in range(map.n_row):
        for col in range(map.n_col):
            if map.map[row][col] == EMPTY_CELL:
                continue
            islands.append(Island(Cell(row, col), map.map[row][col]))
    return islands


# O(n^3)
def simplify(map: Map, islands: list[Island]) -> Map:

    copy = map

    for island in islands:  # O(n^3)
        adjacency_count = island.get_adjacent_count(copy)

        paths = island.get_adjacent_paths(copy)
        direction = 0

        if island.domain < 3 and adjacency_count == 1:
            for path in paths:  # O(4)
                if path != None:
                    copy = create_bridge(copy, path, direction, island.domain)  # O(n)
                direction += 1
        elif island.domain % 3 == 0 and adjacency_count == island.domain / 3:
            for path in paths:  # O(4)
                if path != None:
                    copy = create_bridge(copy, path, direction, 3)  # O(n)
                direction += 1
        elif adjacency_count == int(island.domain / 3 + 1):
            for path in paths:  # O(4)
                if path != None:
                    copy = create_bridge(copy, path, direction, 1)  # O(n)
                direction += 1
    return copy


# O(n)
def create_bridge(map: Map, path: list[Cell], direction: int, length: int) -> Map:
    copy = map.map
    for cell in path:
        domain = copy[cell.row][cell.col]
        copy[cell.row][cell.col] = max(domain, get_bridge(direction, length))
    return Map(map.n_col, map.n_row, copy)


# O(1)
def get_bridge(direction: int, length: int) -> int:
    return (
        MAXIMUM_DOMAIN
        + length * 2
        - (0 if (direction == TOP or direction == DOWN) else 1)
    )


# O(n^2)
def print_matrix(map: Map) -> None:
    for row in range(map.n_row):
        for col in range(map.n_row):
            print(MATRIX_CODE[map.map[row][col]], end="")
        print()


def main():
    map = Map(n_row, n_col, matrix)
    islands = get_islands(map)  # O(n^2)
    simplified = simplify(map, islands)  # O(n^3)
    print_matrix(simplified)  # O(n^2)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("\033[92mRUNTIME: %ss \033[0m" % (time.time() - start_time))
