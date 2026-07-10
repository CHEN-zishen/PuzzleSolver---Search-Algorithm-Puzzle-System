class DFS:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.visited = set()
        self.path = []
        self.steps = []
    
    def solve(self):
        self.visited = set()
        self.path = []
        self.steps = []
        success = self._dfs(self.puzzle.get_initial_state())
        
        return {
            'success': success,
            'path': self.path,
            'steps': self.steps,
            'algorithm': 'DFS',
            'visited_count': len(self.visited)
        }
    
    def _dfs(self, state):
        state_key = self.puzzle.state_to_key(state)
        
        if state_key in self.visited:
            return False
        
        self.visited.add(state_key)
        self.path.append(state)
        
        self.steps.append({
            'state': state,
            'action': 'visit',
            'path_length': len(self.path),
            'visited_count': len(self.visited)
        })
        
        if self.puzzle.is_goal(state):
            self.steps.append({
                'state': state,
                'action': 'goal_found',
                'path_length': len(self.path),
                'visited_count': len(self.visited)
            })
            return True
        
        for next_state in self.puzzle.get_neighbors(state):
            if self._dfs(next_state):
                return True
        
        self.path.pop()
        self.steps.append({
            'state': state,
            'action': 'backtrack',
            'path_length': len(self.path),
            'visited_count': len(self.visited)
        })
        
        return False
