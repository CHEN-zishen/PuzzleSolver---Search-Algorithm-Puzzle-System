import random

class SudokuPuzzle:
    def __init__(self, grid=None):
        if grid is not None:
            self.grid = grid
        else:
            self.grid = [[0 for _ in range(9)] for _ in range(9)]
    
    @staticmethod
    def generate(difficulty='medium'):
        grid = [[0 for _ in range(9)] for _ in range(9)]
        SudokuPuzzle._fill_grid(grid)
        
        cells_to_remove = {'easy': 30, 'medium': 40, 'hard': 50}[difficulty]
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)
        
        for i, j in positions[:cells_to_remove]:
            grid[i][j] = 0
        
        return SudokuPuzzle(grid)
    
    @staticmethod
    def _fill_grid(grid):
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        
        def solve(grid):
            for i in range(9):
                for j in range(9):
                    if grid[i][j] == 0:
                        local_numbers = list(numbers)
                        random.shuffle(local_numbers)
                        for num in local_numbers:
                            if SudokuPuzzle._is_valid_move(grid, i, j, num):
                                grid[i][j] = num
                                if solve(grid):
                                    return True
                                grid[i][j] = 0
                        return False
            return True
        
        solve(grid)
    
    @staticmethod
    def _is_valid_move(grid, row, col, num):
        for i in range(9):
            if grid[row][i] == num:
                return False
        
        for i in range(9):
            if grid[i][col] == num:
                return False
        
        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        for i in range(3):
            for j in range(3):
                if grid[box_row + i][box_col + j] == num:
                    return False
        
        return True
    
    def get_initial_state(self):
        return [row[:] for row in self.grid]
    
    def is_goal(self, state):
        for row in state:
            if 0 in row:
                return False
        return True
    
    def get_neighbors(self, state):
        neighbors = []
        
        for i in range(9):
            for j in range(9):
                if state[i][j] == 0:
                    for num in range(1, 10):
                        if self._is_valid_move(state, i, j, num):
                            new_state = [row[:] for row in state]
                            new_state[i][j] = num
                            neighbors.append(new_state)
                    return neighbors
        
        return []
    
    def state_to_key(self, state):
        return tuple(tuple(row) for row in state)
    
    def is_valid(self, state):
        return True
    
    def heuristic(self, state):
        empty_cells = 0
        for row in state:
            empty_cells += row.count(0)
        return empty_cells
    
    def export(self):
        return self.grid
