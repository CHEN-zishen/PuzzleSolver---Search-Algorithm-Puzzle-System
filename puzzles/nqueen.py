import random

class NQueenPuzzle:
    def __init__(self, n=None, board=None):
        if board is not None:
            self.board = board
            self.n = len(board)
        elif n is not None:
            self.n = n
            self.board = [-1] * n
        else:
            self.n = 4
            self.board = [-1] * 4
    
    @staticmethod
    def generate(n=8):
        return NQueenPuzzle(n)
    
    def get_initial_state(self):
        return self.board[:]
    
    def is_goal(self, state):
        return -1 not in state
    
    def get_neighbors(self, state):
        neighbors = []
        row = state.index(-1) if -1 in state else self.n
        
        if row < self.n:
            for col in range(self.n):
                # 检查是否可以在(row, col)放置皇后
                valid = True
                for i in range(row):
                    if state[i] == col or \
                       abs(state[i] - col) == abs(i - row):
                        valid = False
                        break
                
                if valid:
                    new_state = state[:]
                    new_state[row] = col
                    neighbors.append(new_state)
        
        return neighbors
    
    def state_to_key(self, state):
        return tuple(state)
    
    def is_valid(self, state):
        row = state.index(-1) if -1 in state else self.n
        
        for i in range(row):
            for j in range(i + 1, row):
                if state[i] == state[j] or \
                   abs(state[i] - state[j]) == abs(i - j):
                    return False
        
        return True
    
    def heuristic(self, state):
        conflicts = 0
        placed = [i for i in range(self.n) if state[i] != -1]
        
        for i in range(len(placed)):
            for j in range(i + 1, len(placed)):
                row_i, row_j = state[placed[i]], state[placed[j]]
                if row_i == row_j or abs(row_i - row_j) == abs(placed[i] - placed[j]):
                    conflicts += 1
        
        return conflicts
    
    def export(self):
        return self.board
