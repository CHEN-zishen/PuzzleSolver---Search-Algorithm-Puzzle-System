import random

class SokobanPuzzle:
    def __init__(self, grid=None):
        if grid is not None:
            self.grid = grid
            self.rows = len(grid)
            self.cols = len(grid[0])
            self.player_pos = self._find_player()
            self.boxes = self._find_boxes()
            self.targets = self._find_targets()
        else:
            self.grid = []
            self.rows = 0
            self.cols = 0
            self.player_pos = (0, 0)
            self.boxes = []
            self.targets = []
    
    @staticmethod
    def generate(difficulty='easy'):
        templates = {
            'easy': [
                [1, 1, 1, 1, 1],
                [1, 0, 0, 0, 1],
                [1, 2, 4, 3, 1],
                [1, 0, 0, 0, 1],
                [1, 1, 1, 1, 1]
            ],
            'medium': [
                [1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 1],
                [1, 0, 3, 4, 3, 0, 1],
                [1, 0, 0, 2, 0, 0, 1],
                [1, 0, 3, 4, 3, 0, 1],
                [1, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 1, 1, 1, 1]
            ],
            'hard': [
                [1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 1],
                [1, 0, 3, 4, 3, 0, 1],
                [1, 0, 0, 2, 0, 0, 1],
                [1, 0, 3, 4, 3, 0, 1],
                [1, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 1, 1, 1, 1]
            ]
        }
        
        grid = templates.get(difficulty, templates['easy'])
        return SokobanPuzzle(grid)
    
    def _find_player(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == 2 or self.grid[i][j] == 5:
                    return (i, j)
        return (0, 0)
    
    def _find_boxes(self):
        boxes = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == 4 or self.grid[i][j] == 6:
                    boxes.append((i, j))
        return boxes
    
    def _find_targets(self):
        targets = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == 3 or self.grid[i][j] == 5 or self.grid[i][j] == 6:
                    targets.append((i, j))
        return targets
    
    def get_initial_state(self):
        return (self.player_pos, tuple(self.boxes))
    
    def is_goal(self, state):
        player_pos, boxes = state
        return all(box in self.targets for box in boxes)
    
    def get_neighbors(self, state):
        player_pos, boxes = state
        row, col = player_pos
        neighbors = []
        directions = [((0, 1), '右'), ((0, -1), '左'), ((1, 0), '下'), ((-1, 0), '上')]
        
        for (dr, dc), action in directions:
            new_row, new_col = row + dr, col + dc
            
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                cell = self.grid[new_row][new_col]
                
                if cell == 1:
                    continue
                
                if (new_row, new_col) in boxes:
                    box_new_row, box_new_col = new_row + dr, new_col + dc
                    if 0 <= box_new_row < self.rows and 0 <= box_new_col < self.cols:
                        if self.grid[box_new_row][box_new_col] != 1 and (box_new_row, box_new_col) not in boxes:
                            new_boxes = list(boxes)
                            new_boxes.remove((new_row, new_col))
                            new_boxes.append((box_new_row, box_new_col))
                            neighbors.append(((new_row, new_col), tuple(new_boxes)))
                else:
                    neighbors.append(((new_row, new_col), boxes))
        
        return neighbors
    
    def state_to_key(self, state):
        player_pos, boxes = state
        return (player_pos, tuple(sorted(boxes)))
    
    def heuristic(self, state):
        player_pos, boxes = state
        total_dist = 0
        for box in boxes:
            min_dist = min(abs(box[0] - t[0]) + abs(box[1] - t[1]) for t in self.targets)
            total_dist += min_dist
        return total_dist
    
    def is_valid(self, state):
        return True
    
    def export(self):
        return self.grid
