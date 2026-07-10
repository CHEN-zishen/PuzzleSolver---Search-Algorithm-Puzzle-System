import random

class EightPuzzle:
    def __init__(self, tiles=None):
        if tiles is not None:
            self.tiles = tiles
        else:
            self.tiles = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    
    @staticmethod
    def generate():
        goal = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        tiles = goal[:]
        while True:
            random.shuffle(tiles)
            if tiles != goal and EightPuzzle._is_solvable(tiles):
                break
        return EightPuzzle([tiles[i*3:(i+1)*3] for i in range(3)])
    
    @staticmethod
    def _is_solvable(tiles):
        inversions = 0
        tiles = [x for x in tiles if x != 0]
        for i in range(len(tiles)):
            for j in range(i+1, len(tiles)):
                if tiles[i] > tiles[j]:
                    inversions += 1
        return inversions % 2 == 0
    
    def get_initial_state(self):
        return [row[:] for row in self.tiles]
    
    def is_goal(self, state):
        goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        return state == goal
    
    def get_neighbors(self, state):
        neighbors = []
        empty_row, empty_col = None, None
        
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    empty_row, empty_col = i, j
                    break
        
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            new_row, new_col = empty_row + dr, empty_col + dc
            if 0 <= new_row < 3 and 0 <= new_col < 3:
                new_state = [row[:] for row in state]
                new_state[empty_row][empty_col], new_state[new_row][new_col] = \
                    new_state[new_row][new_col], new_state[empty_row][empty_col]
                neighbors.append(new_state)
        
        return neighbors
    
    def state_to_key(self, state):
        return tuple(tuple(row) for row in state)
    
    def heuristic(self, state):
        distance = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] != 0:
                    goal_row = (state[i][j] - 1) // 3
                    goal_col = (state[i][j] - 1) % 3
                    distance += abs(i - goal_row) + abs(j - goal_col)
        return distance
    
    def is_valid(self, state):
        return True
    
    def export(self):
        return self.tiles
