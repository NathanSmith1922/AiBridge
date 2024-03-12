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

####################################################################################################

# Matrix relevant constants
MATRIX_CODE = '.123456789abc-|="E#'

EMPTY_CELL = 0
MINIMUM_DOMAIN = 1
MAXIMUM_DOMAIN = 12

# Direction relevant constants.
TOP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

####################################################################################################

class Map:
    """Class representing the entire grid representing the Hashi game."""

    def __init__(self, n_row: int, n_col: int, matrix: list[list[int]]) -> None:
        self.n_row = n_row
        self.n_col = n_col
        self.matrix = matrix

####################################################################################################

class Cell:
    """Class representing the cell nodes of the Hashi grid."""

    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col

####################################################################################################
        
class Path:
    """Class representing the path between islands on the Hashi grid."""

    def __init__(self, path: list[Cell], direction, size) -> None:
        self.path = path
        self.direction = direction
        self.size = size

####################################################################################################

class Island(Cell):
    """Subclass of Cell, representing the island nodes of the Hashi grid."""

    def __init__(self, row: int, col: int, domain: int) -> None:
        super().__init__(row, col)
        self.domain = domain

    def __navigate_direction(self, map: Map, direction: int) -> list[Cell]:
        """
        Navigates through the grid in a particular direction
        starting from this node. Path is considered invalid,
        if it encounters a cardinally adjacent island, a
        perpendicular bridge, or an island with full connections.

        This function runs in O(n) time.

        Parameters:
            map (Map): Map class representing the grid
            direction (int): Direction to navigate.

        Returns:
            list[Cell]: A list of Cells representing the path towards its destination.
        """

        navigate_vertically = (direction == TOP or direction == DOWN)
        navigate_backwards = (direction == TOP or direction == LEFT)

        # Since this function is generalised into a single loop, the range and
        # step of the loop is determined by the directions parameter.

        step = -1 if navigate_backwards else 1
        start = (self.row if navigate_vertically else self.col) + step
        end = -1 if navigate_backwards else map.n_row if direction == DOWN else map.n_col

        path = []
        for i in range(start, end, step):
            row = self.row if not navigate_vertically else i
            col = self.col if navigate_vertically else i
            
            domain = map.matrix[row][col]
            is_bridge_vertical = domain % 2 == 0

            # Self-completed case
            if sum(self.get_adjacent_bridge_connections(map)) == self.domain:
                return None

            # If the path contains a parallel bridge or an empty cell. Add to potentential path.
            if domain == EMPTY_CELL or (domain > MAXIMUM_DOMAIN and is_bridge_vertical == navigate_vertically):
                #print("Valid path added at direction" + str(direction))
                path.append(Cell(row, col))

            # Hits a perpendicular bridge.
            if domain > MAXIMUM_DOMAIN and is_bridge_vertical != navigate_vertically:
                return None
            
            # Stops searching when it hits an island.
            if domain >= MINIMUM_DOMAIN and domain <= MAXIMUM_DOMAIN:
                # If no cell is found before hitting this island, then no path exists.
                if len(path) == 0:
                    return None
                # If the destination cell has full connections, then
                # this path shouldn't be considered in calculations.
                if sum(Island(row, col, domain).get_adjacent_bridge_connections(map)) == domain:
                    return None
                
                return path
        # Returns nothing once it's hit the edges of the grid.
        return None

    def get_adjacent_paths(self, map: Map) -> list[list[Cell]]:
        """
        This function runs in O(n) time.

        Parameters:
            map (Map): Map class representing the grid.

        Returns:
            list[list[Cell]]: List of Cell lists representing the paths in all directions.
        """
        return [
            self.__navigate_direction(map, TOP),
            self.__navigate_direction(map, DOWN),
            self.__navigate_direction(map, LEFT),
            self.__navigate_direction(map, RIGHT),
        ]

    def get_adjacent_bridge_connections(self, map: Map) -> list[int]:
        """
        This function runs in O(1) time.

        Parameters:
            map (Map): Map class representing the grid.

        Returns:
            list[int]: List of the connecting bridges to the island in all directions.
        """

        left = map.matrix[self.row][max(self.col - 1, 0)]
        right = map.matrix[self.row][min(self.col + 1, map.n_col - 1)]
        top = map.matrix[max(self.row - 1, 0)][self.col]
        down = map.matrix[min(self.row + 1, map.n_row - 1)][self.col]

        return [
                get_bridge_size(top) if top % 2 == 0 else 0, 
                get_bridge_size(down) if down % 2 == 0 else 0, 
                get_bridge_size(left) if left % 2 == 1 else 0, 
                get_bridge_size(right) if right % 2 == 1 else 0, 
            ]
    
    def get_restricted_domain(self, map: Map) -> int:
        paths = self.get_adjacent_paths(map)
        bridge_connections = self.get_adjacent_bridge_connections(map)
        restricted_domain = self.domain

        debug = ""

        for i in range(4):
            if paths[i] == None and bridge_connections[i] > 0: 
                restricted_domain -= bridge_connections[i]
                debug = debug + " - " + str(bridge_connections[i])
            else:
                debug = debug + " - 0"
        
        #print(str(self.domain) + debug + " = " + str(restricted_domain))
        return restricted_domain
    
####################################################################################################

def get_bridge_size(domain: int) -> int:
        """
        This function runs in O(1) time.

        Parameters:
            domain (int): Domain of the cell.

        Returns:
            int: Bridge size with the associated node.
        """
        if domain >= 0 and domain <= MAXIMUM_DOMAIN: return 0
        return int((domain - MAXIMUM_DOMAIN) / 2) + (1 if domain % 2 == 1 else 0)


def get_islands(map: Map) -> list[Island]:
    """
    Using the Map object, this method iterates
    through the grid and returns a list of all
    the nodes that are islands.

    This function runs in O(n^2) time.

    Parameters:
        map (Map): Map class representing the grid.

    Returns:
        list[Island]: List of all islands on the grid.
    """

    islands = []
    for row in range(map.n_row):
        for col in range(map.n_col):
            domain = map.matrix[row][col]
            if domain == EMPTY_CELL or domain > MAXIMUM_DOMAIN: continue
            islands.append(Island(row, col, domain))
    return islands
    
def simplify(map: Map) -> Map:
    """
    Given a provided Hashi map, create guaranteed bridges
    as according to the layout of the islands and existing
    bridges.

    This function runs in O(n^3) time.

    Parameters:
        map (Map): Map class representing the grid.

    Returns:
        Map: Simplified map class with guaranteed bridges applied.
    """

    # Iterate through all the islands, determine what build steps need to be
    # executed, and queue them into a list to be run after scanning.
    copy = map
    steps = []

    for island in get_islands(copy):
        domain = island.get_restricted_domain(copy)
        paths = island.get_adjacent_paths(copy)
        adjacency_count = 4 - paths.count(None)
        direction = 0

        #print("Node: (" + str(island.row) + ", " + str(island.col) + ")")
        #print("\tDomain: " + str(domain))
        #print("\tPaths: " + str(paths))
        #print("\tAdjacency Count: " + str(adjacency_count))
        # Single island connections case.
        if domain < 3 and adjacency_count == 1:
            for path in paths:
                if path != None:
                    #print("\tSingle")
                    steps.append(Path(path, direction, domain))
                direction += 1
        # Complete islands with maximum connections case.
        elif domain % 3 == 0 and adjacency_count == domain / 3:
            for path in paths:
                if path != None:
                    #print("\tComplete")
                    steps.append(Path(path, direction, 3))
                direction += 1
        # Guaranteed partial connections case.
        elif domain % 3 != 0 and adjacency_count == int(domain / 3 + 1):
            for path in paths:
                if path != None:
                    #print("\tPartial")
                    steps.append(Path(path, direction, 1))
                direction += 1
    
    # After scanning each island and their configurations apply the changes.
    for path in steps:
        copy = create_bridge(copy, path.path, path.direction, path.size)
    return copy

####################################################################################################
# LEGACY SHIT

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
    copy = map.matrix
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
            print(MATRIX_CODE[map.matrix[row][col]], end="")
        print()


def main():
    n_row, n_col, matrix = scan_map()
    map = Map(n_row, n_col, matrix)

    # Helper code to estimate runtime of solution.!
    start_time = time.time()

    before = simplify(map)
    after = simplify(before)
    result = (before.matrix == after.matrix).all()

    while not result:
        before = simplify(after)
        after = simplify(before)
        result = (before.matrix == after.matrix).all()
    
    print_map(after)
    
    print("\033[92mRUNTIME: %ss \033[0m" % (time.time() - start_time))

    # for island in completed_nodes:
        # print(str(island.cell.row) + ", " + str(island.cell.col))


if __name__ == "__main__":
    main()
