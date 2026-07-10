from collections import deque

class BFS:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.visited = set()
        self.parent = {}
    
    def solve(self):
        self.visited = set()
        self.parent = {}
        steps = []
        
        initial_state = self.puzzle.get_initial_state()
        queue = deque([(initial_state, [initial_state])])
        self.visited.add(self.puzzle.state_to_key(initial_state))
        
        steps.append({
            'state': initial_state,
            'action': 'start',
            'queue_size': 1,
            'visited_count': 1
        })
        
        while queue:
            current_state, path = queue.popleft()
            
            if self.puzzle.is_goal(current_state):
                steps.append({
                    'state': current_state,
                    'action': 'goal_found',
                    'queue_size': len(queue),
                    'visited_count': len(self.visited),
                    'path_length': len(path)
                })
                return {
                    'success': True,
                    'path': path,
                    'steps': steps,
                    'algorithm': 'BFS',
                    'visited_count': len(self.visited)
                }
            
            for next_state in self.puzzle.get_neighbors(current_state):
                state_key = self.puzzle.state_to_key(next_state)
                if state_key not in self.visited:
                    self.visited.add(state_key)
                    new_path = path + [next_state]
                    queue.append((next_state, new_path))
                    
                    steps.append({
                        'state': next_state,
                        'action': 'enqueue',
                        'queue_size': len(queue),
                        'visited_count': len(self.visited),
                        'path_length': len(new_path)
                    })
        
        return {
            'success': False,
            'path': [],
            'steps': steps,
            'algorithm': 'BFS',
            'visited_count': len(self.visited)
        }
