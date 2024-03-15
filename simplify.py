import numpy as np
import sys
import time

###############################################################################


def scan_map():
	text = []
	for line in sys.stdin:
		row = []
		for ch in line:
			n = ord(ch)
			if n >= 48 and n <= 57:  # between '0' and '9'
				row.append(n - 48)
			elif n >= 97 and n <= 122:  # between 'a' and 'z'
				row.append(n - 87)
			elif ch == ".":
				row.append(0)
		text.append(row)

	nrow = len(text)
	ncol = len(text[0])

	map = np.zeros((nrow, ncol), dtype = np.int32)
	for r in range(nrow):
		for c in range(ncol):
			map[r, c] = text[r][c]


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

		navigate_vertically = direction == TOP or direction == DOWN
		navigate_backwards = direction == TOP or direction == LEFT

		# Since this function is generalised into a single loop, the range and
		# step of the loop is determined by the directions parameter.

		step = -1 if navigate_backwards else 1
		start = (self.row if navigate_vertically else self.col) + step
		end = (
			-1 if navigate_backwards else map.n_row if direction == DOWN else map.n_col
		)

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
			if domain == EMPTY_CELL or (
				domain > MAXIMUM_DOMAIN and is_bridge_vertical == navigate_vertically
			):
				# print("Valid path added at direction" + str(direction))
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
				if (
					sum(Island(row, col, domain).get_adjacent_bridge_connections(map))
					== domain
				):
					return None
				# Adds the destination cell to the path.
				path.append(Cell(row, col))
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

		"""
		This function runs in O(1) time.

		Parameters:
			map (Map): Map class representing the grid.

		Returns:
			int: The domain of the island after accounting for adjacent environment.
		"""

		paths = self.get_adjacent_paths(map)
		bridge_connections = self.get_adjacent_bridge_connections(map)
		restricted_domain = self.domain

		for i in range(4):
			if paths[i] == None and bridge_connections[i] > 0:
				restricted_domain -= bridge_connections[i]

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
	if domain >= 0 and domain <= MAXIMUM_DOMAIN:
		return 0
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
			if domain == EMPTY_CELL or domain > MAXIMUM_DOMAIN:
				continue
			islands.append(Island(row, col, domain))
	return islands


def simplify(map: Map) -> Map:
	"""
	Given a provided Hashi map, create guaranteed bridges
	as according to the layout of the islands and existing
	bridges.

	This function runs in O(n^4)? time. Included while loop.

	Parameters:
		map (Map): Map class representing the grid.

	Returns:
		Map: Simplified map class with guaranteed bridges applied.
	"""
	requires_restart = True
	while requires_restart:
		original = Map(map.n_row, map.n_col, np.copy(map.matrix))
		# Iterate through all the islands, determine what build steps need to be
		# executed, and queue them into a list to be run after scanning.
		steps = []

		for island in get_islands(map):  # O(n^2)
			domain = island.get_restricted_domain(map)
			paths = island.get_adjacent_paths(map)
			adjacency_count = 4 - paths.count(None)
			direction = 0

			# Single island connections case.
			if domain < 3 and adjacency_count == 1:
				for path in paths:
					if path != None:
						steps.append(Path(path, direction, domain))
					direction += 1

			# Complete islands with maximum connections case.
			elif domain % 3 == 0 and adjacency_count == domain / 3:
				for path in paths:
					if path != None:
						steps.append(Path(path, direction, 3))
					direction += 1

			# Guaranteed partial connections case.
			elif domain % 3 != 0 and adjacency_count == int(domain / 3 + 1):
				for path in paths:
					if path != None:
						steps.append(Path(path, direction, 1))
					direction += 1

		
		# After scanning each island and their configurations apply the changes.
		for path in steps:  # O(n^3)
			map = create_bridge(map, path.path, path.direction, path.size)
		requires_restart = not np.array_equal(original.matrix, map.matrix)
	return map


def create_bridge(map: Map, path: list[Cell], direction: int, length: int) -> Map:
	"""
	Given a provided Map object and a list of cells to
	navigate through, this method iterates through and
	sets the value of the node to the specified bridge
	value and direction.

	This function runs in O(n) time.

	Parameters:
		map (Map): Map class representing the grid.

	Returns:
		Map: A new map with the bridge created.
	"""
	copy = map.matrix
	for cell in path:
		domain = copy[cell.row][cell.col]
		if domain >= MINIMUM_DOMAIN and domain <= MAXIMUM_DOMAIN: continue
		copy[cell.row][cell.col] = max(domain, get_bridge(direction, length))
	return Map(map.n_row, map.n_col, copy)


def get_bridge(direction: int, length: int) -> int:
	"""
	Given a specific direction and bridge length, return the
	number code associated with representing it on the number grid.

	This function runs in O(1) time.

	Parameters:
		direction (int): Direction to navigate.
		length (int): Length of the bridge.

	Returns:
		int: The number representing the bridge.
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

	Parameters:
		map (Map): Map class representing the grid.
	"""
	
	for row in range(map.n_row):
		for col in range(map.n_col):
			if (map.matrix[row][col] > 0 and map.matrix[row][col] < 13):
				new_island = Island(row, col, map.matrix[row][col])
				if (new_island.get_restricted_domain(map) == 0):
					print('\033[92m' + MATRIX_CODE[map.matrix[row][col]] + '\033[0m', end="")
				else:
					print('\033[31m' + MATRIX_CODE[map.matrix[row][col]] + '\033[0m', end="")

			else:    
				print(MATRIX_CODE[map.matrix[row][col]], end="")
		print()

def check_goal(map: Map) -> bool:
	count = 0
	islands = get_islands(map)
	for island in islands:
		if island.get_restricted_domain(map) == 0: 
			count += 1
	if count != len(islands):
		# print("\033[92mProblem not solved yet. " + str(count) + " / " + str(len(islands)) + " solved.\033[0m")
		return False
	print("\033[92mProblem solved!\033[0m")
	print_map(map)
	return True

def get_direction(map: Map, curr: Island, prev: Island) -> int:
	if (curr.row == prev.row):
		if (curr.col > prev.col):
			return RIGHT
		return LEFT
	if (curr.row > prev.row):
		return DOWN
	return TOP

def check_if_move_repeat(move_matrix, row, col, direction, num_bridges):
	if (move_matrix[row][col] == []):
		return False
	if ([direction, num_bridges] in move_matrix[row][col]):
		return True
	return False

def get_curr_domain(map: Map, island: Island) -> int:
	connections = island.get_adjacent_bridge_connections(map)
	total = 0
	for i in range(4):
		total += connections[i]
	return island.domain - total

def DFS_iterative(map: Map):
	# Setup no repeat moves
	matrix_stack = []
	matrix_stack.append(map.matrix.copy())
	curr_map = map

	unvisited_stack = []
	unvisited_stack.append(get_islands(map))
	print(len(unvisited_stack))

	curr_island_stack = []
	curr_island_stack.append(unvisited_stack[0][0])
	
	direction_stack = []
	direction_stack.append(5)

	depth = 0
	while not check_goal(curr_map):
		depth += 1
		# print("Iteration", depth)
		curr_matrix = matrix_stack.pop()
		prev_direction = direction_stack.pop()
		curr_island = curr_island_stack.pop()
		unvisited = unvisited_stack.pop()


		if (len(unvisited) == 0):
			continue

		if (len(unvisited) == 1):
			if (unvisited[0].row == curr_island.row and unvisited[0].col == curr_island.col):
				unvisited.pop()
		else:
			for i in range(0, len(unvisited) - 1):
				if (unvisited[i].row == curr_island.row and unvisited[i].col == curr_island.col):
					unvisited.pop(i)
		
		if (len(unvisited) == 0):
			continue
		curr_map = Map(map.n_row, map.n_col, curr_matrix)

		# Actual DFS
		paths = curr_island.get_adjacent_paths(curr_map)
		for i in range(len(paths)):
			if (paths[i] == None):
				continue
			# How many bridges to place
			path = paths[i]
			next_island = Island(path[-1].row, path[-1].col, curr_matrix[path[-1].row][path[-1].col])

			# Deals with additive bridge creation
			bridges_to_place = min(get_curr_domain(curr_map, curr_island), get_curr_domain(curr_map, next_island), 3)
			num_bridges = 1
			if (curr_matrix[path[0].row][path[0].col] > 0):
				match curr_matrix[path[0].row][path[0].col]:
					case 13 | 14:
						num_bridges += 1
						bridges_to_place += 1
					case 15 | 16:
						num_bridges += 2
						bridges_to_place += 2
					case 17 | 18:
						num_bridges += 3
						bridges_to_place += 3
			num_bridges = min(num_bridges, 3)
			bridges_to_place = min(bridges_to_place, 3)

			# Creates Bridges
			direction = get_direction(curr_map, curr_island, next_island)
			# Stops basic looping
			if (direction == TOP and prev_direction == DOWN):
				continue
			elif (direction == DOWN and prev_direction == TOP):
				continue
			elif (direction == LEFT and prev_direction == RIGHT):
				continue
			elif (direction == RIGHT and prev_direction == LEFT):
				continue

			# Stop Iterating on maxed bridge
			if (curr_matrix[path[0].row][path[0].col] > 16):
				continue
			while num_bridges <= bridges_to_place:
				temp_matrix = curr_matrix.copy()
				new_map = Map(map.n_row, map.n_col, temp_matrix)
				create_bridge(
					new_map, 
					path, 
					direction,
					num_bridges)
				direction_stack.append(direction)

				# Updates Stacks
				matrix_stack.append(temp_matrix)                
				curr_island_stack.append(next_island)
				unvisited_stack.append(unvisited.copy())

				num_bridges += 1

		# Floaters
		if (paths[0] == None and paths[1] == None and paths[2] == None and paths[3] == None and len(unvisited) != 0):
			temp_matrix = curr_matrix.copy()
			matrix_stack.append(temp_matrix)
			curr_island_stack.append(unvisited[0])
			unvisited_stack.append(unvisited.copy())
			direction_stack.append(5)

		curr_matrix = None
def main():
	n_row, n_col, matrix = scan_map()
	map = Map(n_row, n_col, matrix)

	# Helper code to estimate runtime of solution.
	start_time = time.time()
	result = simplify(map)
	print_map(result)
	DFS_iterative(result)
	print("\033[92mRUNTIME: %ss \033[0m" % (time.time() - start_time))



if __name__ == "__main__":
	main()

"""
5..5..5...
.5..6...1.
..........
5.2.b.6.2.
..........
.4..8..6.4
..........
5...9..8.6
..........
.1..6..6.4
"""

"""
.1...6...7....4.4.2.
..4.2..2...3.8...6.2
.....2..............
5.c.7..a.a..5.6..8.5
.............2......
...5...9.a..8.b.8.4.
4.5................3
....2..4..1.5...2...
.2.7.4...7.2..5...3.
............4..3.1.2
"""

"""
..........
6.7.6..4.3
......3...
..2....2..
4...8.6..6
..1.......
......4.2.
....3..2.8
3.6...5.2.
....3....6
"""

"""
.5.3.
.....
.7.3.
.....
.6.4.
"""

"""
6......6
.4..7.1.
........
.2..5..7
........
6...5..7
........
4...7..5
"""

"""
.........
3..5..9.6
.........
.5.7..8..
3........
....1.5.5
.........
.3.5...3.
1.1...4.4
"""

"""
4.8.6.6.3.
..........
7.a.5.a.5.
..........
..4.4.7..4
4..4.3.1..
......2...
4.5.6..6.6
..........
3.5.7..8.5
"""

"""
5.6..7.5.3
..........
...3.7.4.2
4.........
..1..9..3.
......1..2
4..8.9.2..
......3..4
4.3..2....
.3.7..4..1
"""

"""
4.1...4.5.5..3.4..7....9.7..7.6.4.7.4...
....................2.3....3.........2..
...4..a.8.9..6..5.4....3.....1....3....2
..1.3......3..9.....8.9..5..1.2.6...4...
...1....2....................5.3.....5.6
9.5.6.8...b.8.9.4........3....2.8..2....
........1....2.......................3.6
9...9.6.....2..3...7.8.7.5.8.5..8.3.....
.3.........4.7...5..........3..3.1...3.7
..3.8.....3..........6.5.4...3..3..7....
6.....5.6..4...3.6..........2........4.7
....2........3........3..8.a.7.5...6....
.5....5..3..1..6.5..........1........4.6
...........6.9..6..7.7.1.5.5..6.6.2.....
.4.2..5.4......4...............3.1.5.4.5
.......1.5.3....3..3.6.3.4..6.7.5.3.....
.4.5..6...2..8.6.5....5.1.2.............
...........................1....3..6....
5.....9..8..8..5.9..9.c..7...........4.6
........1..3................6..6.3.5....
.5.6..8...2..3.5.7..6.....5..........3.5
............5.1.......7.1........7.7....
....2.7..7.5......2.3..2.8..3........4.5
.3..........5..4.8...2.....6..8....3....
3..6..8.4.3.......6.6.b..6..3....3......
.5...2...3.......2.........3...3...6.7.5
...3..8.8.9.c..9..b.9.a.9.9.9.9..6..1.2.
..2.3..2...1...........1................
...2.3......3........3..4........5.4..3.
........4..7...8..9.4.1..............3.2
.8.8.6.7.7...9...3.3.9.9..7........5..1.
....5.2.......6...8...1.3...............
...6.3.5...1.7..1.........5.8......a.9.5
....6....a..3......1...5................
.9.b..7.3.....6.4.6..2..6.8.b..7...a..4.
....1..6.8.2.........................3..
................4.9.5..6.1...2.4.1......
....3..5.9.7.6.....2.5....4.7.4.3..6.4..
...2..1.................................
.6..8....8....7.7.9..5...2..6.7.5..6..6.
"""