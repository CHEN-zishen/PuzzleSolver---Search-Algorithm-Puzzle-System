import random

class MazePuzzle:
    def __init__(self, grid=None, start=None):
        if grid is not None:
            self.grid = grid
            self.rows = len(grid)
            self.cols = len(grid[0])
            # 如果提供了自定义起点，则使用它，否则查找原始起点
            if start is not None:
                self.start = start
            else:
                self.start = self._find_start()
            self.goal = self._find_goal()
        else:
            self.grid = []
            self.rows = 0
            self.cols = 0
            self.start = (0, 0)
            self.goal = (0, 0)
    
    @staticmethod
    def generate(size=9):
        grid = [[1 for _ in range(size)] for _ in range(size)]
        
        def carve(row, col):
            grid[row][col] = 0
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(directions)
            
            for dr, dc in directions:
                new_row, new_col = row + 2 * dr, col + 2 * dc
                if 0 <= new_row < size and 0 <= new_col < size and grid[new_row][new_col] == 1:
                    grid[row + dr][col + dc] = 0
                    carve(new_row, new_col)
        
        carve(0, 0)
        grid[0][0] = 2
        grid[size-1][size-1] = 3
        
        return MazePuzzle(grid)
    
    def _find_start(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == 2:
                    return (i, j)
        return (0, 0)
    
    def _find_goal(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == 3:
                    return (i, j)
        return (self.rows-1, self.cols-1)
    
    def get_initial_state(self):
        return self.start
    
    def is_goal(self, state):
        return state == self.goal
    
    def get_neighbors(self, state):
        row, col = state
        neighbors = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                if self.grid[new_row][new_col] != 1:
                    neighbors.append((new_row, new_col))
        
        return neighbors
    
    def state_to_key(self, state):
        return (state[0], state[1])
    
    def heuristic(self, state):
        return abs(state[0] - self.goal[0]) + abs(state[1] - self.goal[1])
    
    def is_valid(self, state):
        return True
    
    def export(self):
        return self.grid
