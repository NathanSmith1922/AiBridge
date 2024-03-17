#!/usr/bin/python3

"""
We have created three main classes, called Map, Cell and Island to represent the entire Hashi problem.
The idea before applying any search techniques was to restrict and simplify the problem as much as we
can to cut off combinations of the puzzle. The simplify algorithm in turn, places guaranteed bridges
based on an islands domain, and number of adjacent islands, returning the new map after completion.

The function simplify() follows three conditions:
	- Single connection bridges -> Islands with 1 adjacency with the domains 1 - 3.
	- Fully connected islands -> Islands with a domain multiple of 3 with adjacencies matching 'domain / 3'
	- Guaranteed partial connections -> Islands with domains not a multiple of 3 with adjacencies matching 'int(domain / 3 + 1)'.
	  Integer cast is used here because we need to round this number down.
	  
	  Example -> 4 node with 2 adjacencies has a guaranteed single connection on the 2 adjacent sides.

Simplify will continue to loop until no more guaranteed connections can be made.

Afterwards, Our backtracking algorithm to attempt the hashi problem is a modified DFS.
At each iteration, it completes one move and then appends all next possible moves to a stack.
We add all potential moves to ensure that islands that are not connecting to our starting 
island will still be solved. When checking if a move is valid, the dfs uses arc consistency 
by checking if the islands surrounding the current and next islands have bridge capacities 
such that they can solve the current and next islands after the current move (i.e. an island 
with 2 required bridges and only 1 adjacent island should never make a bridge connection not 
equal to 2). Additionally, we have implemented a set containing hashed versions of previous 
map states to ensure that a map state already proven to fail is not repeated.
"""

import numpy as np
import sys

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
			if sum(self.get_adjacent_bridge_connections(map, [])) == self.domain:
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
					sum(Island(row, col, domain).get_adjacent_bridge_connections(map, []))
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

	def get_adjacent_bridge_connections(self, map: Map, ignore_direction: list[int]) -> list[int]:
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
			0 if TOP in ignore_direction else get_bridge_size(top) if top % 2 == 0 else 0,
			0 if DOWN in ignore_direction else get_bridge_size(down) if down % 2 == 0 else 0,
			0 if LEFT in ignore_direction else get_bridge_size(left) if left % 2 == 1 else 0,
			0 if RIGHT in ignore_direction else get_bridge_size(right) if right % 2 == 1 else 0,
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
		bridge_connections = self.get_adjacent_bridge_connections(map, [])
		restricted_domain = self.domain

		for i in range(4):
			if paths[i] == None and bridge_connections[i] > 0:
				restricted_domain -= bridge_connections[i]

		return restricted_domain
	
	def get_curr_domain(self, map: Map) -> int:
		"""
		This functions runs in O(1) time

		Parameters:
			map (Map): Map class representing the grid.

		Returns:
			int: The domain of the island after subtracting all surrounding bridges.	
		"""
		return (self.domain - sum(self.get_adjacent_bridge_connections(map, [4])))	


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
			print(MATRIX_CODE[map.matrix[row][col]], end="")
		print()

def check_goal(map: Map) -> bool:
	count = 0
	islands = get_islands(map)
	for island in islands:
		if island.get_restricted_domain(map) == 0: 
			count += 1
	if count != len(islands):
		return False
	print_map(map)
	return True


def DFS(map: Map):
	
	visited = set()
	stack = [Map(map.n_row, map.n_col, map.matrix.copy())]

	while len(stack) > 0:
		current_map = stack.pop()

		if check_goal(current_map):
			return current_map
		
		# Mark current state as visited
		hashable = tuple(tuple(row) for row in current_map.matrix)
		visited.add(hash(hashable))
		
		# Iterate and find any islands that have incomplete paths.
		for current_island in get_islands(current_map):
			# Ignores islands that have been otherwise completed.
			if current_island.get_restricted_domain(current_map) == 0: continue

			direction = 0
			curr_domain = current_island.get_curr_domain(current_map)

			# Get the sum of domains arround the current island
			paths = current_island.get_adjacent_paths(current_map)
			surrounding_domains = 0
			for path in paths:
				if path is not None:
					temp_island = Island(path[-1].row, path[-1].col, current_map.matrix[path[-1].row][path[-1].col])
					surrounding_domains += temp_island.get_curr_domain(current_map)

			# Checks and finds the incomplete paths of this island.
			for path in paths:
				# Once it discoveres a path it can connect to, commit that choice to a new map and add to the stack.
				if path is not None:
					next_island = Island(path[-1].row, path[-1].col, current_map.matrix[path[-1].row][path[-1].col])
					next_domain = next_island.get_curr_domain(current_map)

					# Get the sum of domains arround the next island
					next_surrounding_domains = 0
					for next_path in next_island.get_adjacent_paths(current_map):
						if next_path is not None:
							temp_island = Island(next_path[-1].row, next_path[-1].col, current_map.matrix[next_path[-1].row][next_path[-1].col])
							next_surrounding_domains += temp_island.get_curr_domain(current_map)

					# Out of the two selected islands, what is the maximum bridge size that can be placed between them?
					maximum_bridge_size_attemptable = min(
						curr_domain + get_bridge_size(current_map.matrix[path[0].row][path[0].col]),
						next_domain + get_bridge_size(current_map.matrix[path[0].row][path[0].col]),
						3
					)
					
					for i in range(0, maximum_bridge_size_attemptable + 1):
						if get_bridge_size(current_map.matrix[path[0].row][path[0].col]) >= i: continue

						# Arc Consistency:
						# Ignore attempt if islands surronding curr_island cannot complete curr_island after new bridge
						if (
							(curr_domain + get_bridge_size(current_map.matrix[path[0].row][path[0].col]) - i) >
							(surrounding_domains - next_domain)
							):
							continue
						# Ignore attempt if islands surronding next_island cannot complete next_island after new bridge
						if (
							(next_domain + get_bridge_size(current_map.matrix[path[0].row][path[0].col]) - i) > 
							(next_surrounding_domains - curr_domain)
							):
							continue


						temp = Map(current_map.n_row, current_map.n_col, current_map.matrix.copy())

						new_map = create_bridge(temp, path, direction, i)

						# Checks for cycles. i.e already picked routes.
						hashable = tuple(tuple(row) for row in new_map.matrix)
						if hash(hashable) in visited:
							continue  # Skip visited states to prevent loops

						stack.append(new_map)
				direction += 1
		# Helps garbage collector
		current_map.matrix = None
		current_map = None
	print("\033[91mCOULDN'T FIND SOLUTION (CHECK CODE)\033[0m")	
	return

####################################################################################################
		
def main():
	n_row, n_col, matrix = scan_map()
	map = Map(n_row, n_col, matrix)

	# Helper code to estimate runtime of solution.
	result = simplify(map)
	DFS(result)

if __name__ == "__main__":
	main()