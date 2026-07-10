class Backtracking:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.path = []
        self.steps = []
        self.pruned_count = 0
        self.active_keys = set()
    
    def solve(self):
        self.path = []
        self.steps = []
        self.pruned_count = 0
        self.active_keys = set()
        
        initial_state = self.puzzle.get_initial_state()
        success = self._backtrack(initial_state)
        
        return {
            'success': success,
            'path': self.path,
            'steps': self.steps,
            'algorithm': 'Backtracking',
            'pruned_count': self.pruned_count
        }
    
    def _backtrack(self, state):
        state_key = self.puzzle.state_to_key(state)
        if state_key in self.active_keys:
            self.pruned_count += 1
            self.steps.append({
                'state': state,
                'action': 'prune_cycle',
                'path_length': len(self.path),
                'pruned_count': self.pruned_count
            })
            return False

        self.active_keys.add(state_key)
        self.path.append(state)
        
        self.steps.append({
            'state': state,
            'action': 'place',
            'path_length': len(self.path),
            'pruned_count': self.pruned_count
        })
        
        if self.puzzle.is_goal(state):
            self.steps.append({
                'state': state,
                'action': 'goal_found',
                'path_length': len(self.path),
                'pruned_count': self.pruned_count
            })
            return True
        
        for next_state in self.puzzle.get_neighbors(state):
            if self.puzzle.is_valid(next_state):
                if self._backtrack(next_state):
                    return True
            else:
                self.pruned_count += 1
                self.steps.append({
                    'state': next_state,
                    'action': 'prune',
                    'path_length': len(self.path),
                    'pruned_count': self.pruned_count
                })
        
        self.path.pop()
        self.active_keys.remove(state_key)
        self.steps.append({
            'state': state,
            'action': 'backtrack',
            'path_length': len(self.path),
            'pruned_count': self.pruned_count
        })
        
        return False
