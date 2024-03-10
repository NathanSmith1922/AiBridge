import numpy
import sys
import time

###############################################################################

def scan_map():
    text = []
    for line in sys.stdin:
        row = []
        for ch in line:
            n = ord(ch)
            if n >= 48 and n <= 57:    # between '0' and '9'
                row.append(n - 48)
            elif n >= 97 and n <= 122: # between 'a' and 'z'
                row.append(n - 87)
            elif ch == '.':
                row.append(0)
        text.append(row)

    nrow = len(text)
    ncol = len(text[0])

    map = numpy.zeros((nrow,ncol),dtype=numpy.int32)
    for r in range(nrow):
        for c in range(ncol):
            map[r,c] = text[r][c]
    
    return nrow, ncol, map


###############################################################################

# This is an temporary example of what the scan_print_map file returns after
# execution. These variables will be provided from said function as a return
# statement.

n_row_test = 10
n_col_test = 10
matrix_test = numpy.array(
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

MATRIX_CODE = '.123456789abc-|="E#'

MAP_START_INDEX = -1
EMPTY_CELL = 0
MINIMUM_DOMAIN = 1
MAXIMUM_DOMAIN = 12

DIRECTION_COUNT = 4
TOP = 0
DOWN = 1
LEFT = 2
RIGHT = 3


class Map:
    """Class representing the entire grid representing the Hashi game."""

    def __init__(self, n_row: int, n_col: int, map: list[list[int]]) -> None:
        self.n_row = n_row
        self.n_col = n_col
        self.map = map


class Cell:
    """Class representing the cell nodes of the Hashi grid."""

    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col


class Island:
    """Class representing the island nodes of Hashi."""

    def __init__(self, cell: Cell, domain: int) -> None:
        self.cell = cell
        self.domain = domain

    def __navigate_direction(self, map: Map, direction: int) -> list[Cell]:
        """
        Navigates through the grid in a particular
        direction starting from this node. Stops when
        encountering a blocked path whether it's a
        non-adjacent bridge or another island node.

        This function runs in O(n) time.

        Args:
            map: Map class representing the grid.
            direction: Direction to navigate.

        Returns:
            A list of Cell objects representing a valid path
            in a particular direction to another island node.
        """

        is_vertical_direction = direction == TOP or direction == DOWN
        is_backwards_navigation = direction == TOP or direction == LEFT

        # Since this function is generalised into a single loop, the range and
        # step of the loop is determined by the parameters of this function.

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

            # When it encounters an empty cell or any bridge,
            # append potential path to array to avoid conflicts.
            if cell > MAXIMUM_DOMAIN or cell == EMPTY_CELL:
                path.append(Cell(row, col))

            # Stops when another island has been encounterd.
            # If no empty cell is between this island and the
            # other island, then no valid path can be created.

            if cell >= MINIMUM_DOMAIN and cell <= MAXIMUM_DOMAIN:
                if len(path) == 0:
                    return None
                return path
        return None

    def get_adjacent_paths(self, map: Map) -> list[list[Cell]]:
        """
        This function runs in O(n) time.

        Args:
            map: Map class representing the grid.

        Returns:
            Returns a list of all the valid paths
            adjacent to this island node.
        """
        return [
            self.__navigate_direction(map, TOP),
            self.__navigate_direction(map, DOWN),
            self.__navigate_direction(map, LEFT),
            self.__navigate_direction(map, RIGHT),
        ]

    def get_adjacent_count(self, map: Map) -> int:
        """
        This function runs in O(n) time.

        Args:
            map: Map class representing the grid.

        Returns:
            Returns the number of valid paths that
            can be potentially connected to this
            island node.
        """

        return DIRECTION_COUNT - self.get_adjacent_paths(map).count(None)

    def __get_bridge_size(self, domain: int) -> int:
        """
        This function runs in O(1) time.

        Args:
            domain: Size of the node value.

        Returns:
            Returns the bridge size with the associated node.
        """
        if domain >= 0 and domain <= MAXIMUM_DOMAIN:
            return 0
        return int((domain - MAXIMUM_DOMAIN) / 2) + (1 if domain % 2 == 1 else 0)

    def get_active_connections_count(self, map: Map) -> int:
        """
        This function runs in O(1) time.

        Args:
            map: Map class representing the grid.

        Returns:
            Returns the number of connecting bridges
            in the current node.
        """

        top = map.map[self.cell.row][max(self.cell.col - 1, 0)]
        bottom = map.map[self.cell.row][min(self.cell.col + 1, map.n_col - 1)]
        left = map.map[max(self.cell.row - 1, 0)][self.cell.col]
        right = map.map[min(self.cell.row + 1, map.n_row - 1)][self.cell.col]

        return (
            self.__get_bridge_size(top)
            + self.__get_bridge_size(bottom)
            + self.__get_bridge_size(left)
            + self.__get_bridge_size(right)
        )


def get_islands(map: Map) -> list[Island]:
    """
    Using the Map object, this method iterates
    through the grid and returns a list of all
    the nodes that are islands.

    This function runs in O(n^2) time.

    Args:
        map: Map class representing the grid.

    Returns:
        Returns the a list of islands in the provided grid.
    """

    islands = []
    for row in range(map.n_row):
        for col in range(map.n_col):
            if map.map[row][col] == EMPTY_CELL or map.map[row][col] > MAXIMUM_DOMAIN:
                continue
            islands.append(Island(Cell(row, col), map.map[row][col]))
    return islands


def simplify(map: Map) -> tuple[Map, list[Island]]:
    """
    Given a provided Hashi map, this function simplifies
    the problem by creating guaranteed bridges for islands
    that have the conditions to create them. This should
    hopefuly simplify the problem by pruning pathways in
    the latter DFS search.

    This function runs in O(n^3) time.

    Args:
        map: Map class representing the grid.

    Returns:
        A simplified version of the inputted Map object.
    """

    copy = map

    for island in get_islands(copy):
        adjacency_count = island.get_adjacent_count(copy)
        paths = island.get_adjacent_paths(copy)
        direction = 0

        # Single island connections case.
        if island.domain < 3 and adjacency_count == 1:
            for path in paths:
                if path != None:
                    copy = create_bridge(copy, path, direction, island.domain)
                direction += 1
        # Complete islands with maximum connections case.
        elif island.domain % 3 == 0 and adjacency_count == island.domain / 3:
            for path in paths:
                if path != None:
                    copy = create_bridge(copy, path, direction, 3)
                direction += 1
        # Guaranteed partial connections case.
        elif adjacency_count == int(island.domain / 3 + 1):
            for path in paths:
                if path != None:
                    copy = create_bridge(copy, path, direction, 1)
                direction += 1

    completed_nodes = []
    # Checks which islands have been completed from simplify function.
    for island in get_islands(copy):
        if island.get_active_connections_count(copy) == island.domain:
            completed_nodes.append(island)

    return copy, completed_nodes


def create_bridge(map: Map, path: list[Cell], direction: int, length: int) -> Map:
    """
    Given a provided Map object and a list of cells to
    navigate through, this method iterates through and
    sets the value of the node to the specified bridge
    value and direction.

    This function runs in O(n) time.

    Args:
        map: Map class representing the grid.

    Returns:
        A new map with the bridge created.
    """

    copy = map.map
    for cell in path:
        domain = copy[cell.row][cell.col]
        copy[cell.row][cell.col] = max(domain, get_bridge(direction, length))
    return Map(map.n_col, map.n_row, copy)


def get_bridge(direction: int, length: int) -> int:
    """
    Given a specific direction and bridge length, return the
    number code associated with representing it on the number grid.

    This function runs in O(1) time.

    Args:
        direction: Direction to navigate.
        length: Length of the bridge.

    Returns:
        The number representing the bridge.
    """

    return (
        MAXIMUM_DOMAIN
        + length * 2
        - (0 if (direction == TOP or direction == DOWN) else 1)
    )


def print_map(map: Map) -> None:
    """
    Prints the entire Map object.

    This function runs in O(n^2) time.

    Args:
        map: Map class representing the grid.
    """

    for row in range(map.n_row):
        for col in range(map.n_row):
            print(MATRIX_CODE[map.map[row][col]], end="")
        print()


def main():
    n_row, n_col, matrix = scan_map()
    map = Map(n_row, n_col, matrix)

    # Helper code to estimate runtime of solution.!
    start_time = time.time()

    simplified, completed_nodes = simplify(map)  # O(n^3)
    print_map(simplified)  # O(n^2)
    
    print("\033[92mRUNTIME: %ss \033[0m" % (time.time() - start_time))

    # for island in completed_nodes:
        # print(str(island.cell.row) + ", " + str(island.cell.col))


if __name__ == "__main__":
    main()
