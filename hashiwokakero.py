import numpy
import time

# This is an example of what the scan_print_map file returns after execution.

MATRIX_CODE = ".123456789abc-|=\"E#"

rowSize = 5
colSize = 5

def getMatrix():
#     return (numpy.array(
#             [
#                 [0, 4, 0, 9, 0, 0, 8, 0, 0, 6],
#                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                 [0, 5, 0, 9, 0, 0, 9, 0, 4, 0],
#                 [0, 0, 0, 0, 0, 2, 0, 0, 0, 0],
#                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                 [0, 5, 0, 8, 0, 5, 0, 0, 1, 0],
#                 [0, 0, 3, 0, 0, 0, 7, 0, 0, 7],
#                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                 [0, 1, 0, 0, 0, 1, 0, 0, 0, 4],
#                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#             ]
#         ))
    return (numpy.array(
            [
                [1, 0, 2, 0, 3],
                [0, 0, 0, 0, 0],
                [3, 0, 2, 0, 0],
                [0, 2, 0, 0, 4],
                [2, 0, 0, 1, 0],
            ]
        ))


class Coordinate:
    def __init__(self, row, col):
        self.row = row
        self.col = col


class Island:
    def __init__(self, coordinate, size):
        self.coordinate = coordinate
        self.size = size

    # DRAFT FUNCTIONS FOR GETTING ADJACENCIES
    def top(self, matrix):
        for i in range(self.coordinate.row, 0, -1):
            node = matrix[i][self.coordinate.col]
            if node == -1:
                return Coordinate(None, None)
            if i != self.coordinate.row and node != 0 and node <= 12:
                return Coordinate(i, self.coordinate.col)
        return Coordinate(None, None)

    def down(self, matrix):
        for i in range(self.coordinate.row + 1, rowSize):
            node = matrix[i][self.coordinate.col]
            if node == -1:
                return Coordinate(None, None)
            if i != self.coordinate.row and node != 0 and node <= 12:
                return Coordinate(i, self.coordinate.col)
        return Coordinate(None, None)

    def left(self, matrix):
        for i in range(self.coordinate.col, 0, -1):
            node = matrix[self.coordinate.row][i]
            if node == -1:
                return Coordinate(None, None)
            if i != self.coordinate.col and node != 0 and node <= 12:
                return Coordinate(self.coordinate.row, i)
        return Coordinate(None, None)

    def right(self, matrix):
        for i in range(self.coordinate.col, colSize):
            node = matrix[self.coordinate.row][i]
            if node == -1:
                return Coordinate(None, None)
            if i != self.coordinate.col and node != 0 and node <= 12:
                return Coordinate(self.coordinate.row, i)
        return Coordinate(None, None)


def getBridgeSize(domain):
    return int(max(0, ((domain - 10) / 2)))


def myTestingFunction():
    # me = Island(Coordinate(0, 1), 4)
    # print(me.size)
    # result = me.right()
    # print(result.row, result.col)
    # newMatrix = matrix
    # print(checkIfSolution(newMatrix))
    # visited = [[0, 0]]
    # visited.append([1, 1])
    # print(visited)

    setupDFS()


def setupDFS():
    newMatrix = getMatrix()
    visited = []
    unvisited = findUnvisited(newMatrix)
    # print(unvisited)
    # curr = Island(Coordinate(0, 0), 0)
    DFS(newMatrix, visited, unvisited, unvisited[0], None, 0)

def findUnvisited(newMatrix):
    unvisited = []
    for row in range(rowSize):
        for col in range(colSize):
            if (newMatrix[row][col] != 0):
                unvisited.append(Island(Coordinate(row, col), newMatrix[row][col]))
    
    return unvisited

def DFS(matrix, visited, unvisited, curr, prev, numBridges):
    # print(curr.coordinate.row, curr.coordinate.col)
    if (checkIfSolution(matrix)):
        print_matrix(matrix)
        print("==================== Solution Found ====================")
        return

    if (len(unvisited) == 0):
        return
    
    newMatrix = matrix.copy()
    newUnvisited = unvisited.copy()
    newVisited = visited.copy()

    newVisited.append(curr)
    # remove curr from unvisited
    for i in range(0, len(newUnvisited) - 1):
        if (newUnvisited[i].coordinate.row == curr.coordinate.row and newUnvisited[i].coordinate.col == curr.coordinate.col):
            newUnvisited.pop(i)

    # Creating the bridges between curr and prev
    if (numBridges != 0 and prev != None):
        # update curr and prev sizes
        curr.size -= numBridges
        newMatrix[curr.coordinate.row][curr.coordinate.col] -= numBridges
        if (newMatrix[curr.coordinate.row][curr.coordinate.col] == 0):
            newMatrix[curr.coordinate.row][curr.coordinate.col] = -1
        newMatrix[prev.coordinate.row][prev.coordinate.col] -= numBridges
        if (newMatrix[prev.coordinate.row][prev.coordinate.col] == 0):
            newMatrix[prev.coordinate.row][prev.coordinate.col] = -1

        if (curr.coordinate.row == prev.coordinate.row):
            start = min(prev.coordinate.col, curr.coordinate.col)
            end = max(prev.coordinate.col, curr.coordinate.col)
            for i in range(start + 1, end):
                newMatrix[curr.coordinate.row][i] = -1
        else:
            start = min(prev.coordinate.row, curr.coordinate.row)
            end = max(prev.coordinate.row, curr.coordinate.row)
            for i in range(start + 1, end):
                newMatrix[i][curr.coordinate.col] = -1
        # print_matrix(newMatrix)

    if (prev != None):
        print("prev = ", prev.coordinate.row, prev.coordinate.col, "adj prev:", "left:", prev.left(newMatrix).row, "right:", prev.right(newMatrix).row, "up:", prev.top(newMatrix).row, "down", prev.down(newMatrix).row)
        print_matrix(newMatrix)
        if (newMatrix[prev.coordinate.row][prev.coordinate.col] > 0):
            if (prev.left(newMatrix).row == None and
                prev.right(newMatrix).row == None and
                prev.top(newMatrix).row == None and
                prev.down(newMatrix).row == None):
                    print("HI")
                    return



    # places bridges to the right
    if (curr.right(newMatrix).row != None):
        # Work out how many bridges to place
        bridgesToPlace = min(newMatrix[curr.coordinate.row][curr.coordinate.col], newMatrix[curr.right(newMatrix).row][curr.right(newMatrix).col])
        if (bridgesToPlace > 3):
            bridgesToPlace = 3

        rightIsland = Island(curr.right(newMatrix), newMatrix[curr.right(newMatrix).row][curr.right(newMatrix).col])
        for i in range(1, bridgesToPlace + 1):
            DFS(newMatrix, newVisited, newUnvisited, rightIsland, curr, i)

    # places bridges to the left
    if (curr.left(newMatrix).row != None):
        # Work out how many bridges to place
        bridgesToPlace = min(newMatrix[curr.coordinate.row][curr.coordinate.col], newMatrix[curr.left(newMatrix).row][curr.left(newMatrix).col])
        if (bridgesToPlace > 3):
            bridgesToPlace = 3

        leftIsland = Island(curr.left(newMatrix), newMatrix[curr.left(newMatrix).row][curr.left(newMatrix).col])
        for i in range(1, bridgesToPlace + 1):
            DFS(newMatrix, newVisited, newUnvisited, leftIsland, curr, i)
            
    # places bridges to the top
    if (curr.top(newMatrix).row != None):
        # Work out how many bridges to place
        bridgesToPlace = min(newMatrix[curr.coordinate.row][curr.coordinate.col], newMatrix[curr.top(newMatrix).row][curr.top(newMatrix).col])
        if (bridgesToPlace > 3):
            bridgesToPlace = 3

        topIsland = Island(curr.top(newMatrix), newMatrix[curr.top(newMatrix).row][curr.top(newMatrix).col])
        for i in range(1, bridgesToPlace + 1):
            DFS(newMatrix, newVisited, newUnvisited, topIsland, curr, i)

    # places bridges to the bottom
    if (curr.down(newMatrix).row != None):
        # Work out how many bridges to place
        bridgesToPlace = min(newMatrix[curr.coordinate.row][curr.coordinate.col], newMatrix[curr.down(newMatrix).row][curr.down(newMatrix).col])
        if (bridgesToPlace > 3):
            bridgesToPlace = 3

        downIsland = Island(curr.down(newMatrix), newMatrix[curr.down(newMatrix).row][curr.down(newMatrix).col])
        # for i in range(1, bridgesToPlace + 1):
        #     DFS(newMatrix, newVisited, newUnvisited, downIsland, curr, i)
        DFS(newMatrix, newVisited, newUnvisited, downIsland, curr, 1)

    # Bloody floaters
    if (curr.left(newMatrix).row == None and 
        curr.right(newMatrix).row == None and
        curr.top(newMatrix).row == None and
        curr.down(newMatrix).row == None and
        len(newUnvisited) != 0):
        DFS(newMatrix, newVisited, newUnvisited, newUnvisited.pop(0), curr, 0)

    



def checkIfSolution(newMatrix):
    for row in range(rowSize):
        for col in range(colSize):
            if(newMatrix[row][col] > 0):
                return False
    return True
# TESTING FUNCTIONS
# island = Island(Coordinate(row, col), matrix[row][col])

def print_matrix(newMatrix):
    for row in range(rowSize):
        for col in range(colSize):
            print(MATRIX_CODE[newMatrix[row][col]],end="")
        print()

    print()

def main():
    print_matrix(getMatrix())

    start_time = time.time()
    myTestingFunction()
    print("--- %s seconds ---" % (time.time() - start_time))

    # for i in range(18):
    #     print(getBridgeSize(i))

if __name__ == "__main__":
    main()