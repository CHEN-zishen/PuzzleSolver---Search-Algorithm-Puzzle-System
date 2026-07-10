import heapq

class AStar:
    def __init__(self, puzzle):
        self.puzzle = puzzle
    
    def solve(self):
        visited = {}
        parent = {}
        steps = []
        
        initial_state = self.puzzle.get_initial_state()
        initial_key = self.puzzle.state_to_key(initial_state)
        
        g = {initial_key: 0}
        h = self.puzzle.heuristic(initial_state)
        f = {initial_key: h}
        
        priority_queue = [(f[initial_key], h, initial_state)]
        visited[initial_key] = True
        
        steps.append({
            'state': initial_state,
            'action': 'start',
            'f': f[initial_key],
            'g': 0,
            'h': h,
            'queue_size': 1,
            'visited_count': 1
        })
        
        while priority_queue:
            f_val, h_val, current_state = heapq.heappop(priority_queue)
            current_key = self.puzzle.state_to_key(current_state)
            
            if self.puzzle.is_goal(current_state):
                path = self._reconstruct_path(parent, current_state)
                steps.append({
                    'state': current_state,
                    'action': 'goal_found',
                    'f': f_val,
                    'g': g[current_key],
                    'h': h_val,
                    'queue_size': len(priority_queue),
                    'visited_count': len(visited),
                    'path_length': len(path)
                })
                return {
                    'success': True,
                    'path': path,
                    'steps': steps,
                    'algorithm': 'A*',
                    'visited_count': len(visited)
                }
            
            for next_state in self.puzzle.get_neighbors(current_state):
                next_key = self.puzzle.state_to_key(next_state)
                tentative_g = g[current_key] + 1
                
                if next_key not in visited or tentative_g < g.get(next_key, float('inf')):
                    visited[next_key] = True
                    parent[next_key] = current_state
                    g[next_key] = tentative_g
                    h_next = self.puzzle.heuristic(next_state)
                    f[next_key] = tentative_g + h_next
                    heapq.heappush(priority_queue, (f[next_key], h_next, next_state))
                    
                    steps.append({
                        'state': next_state,
                        'action': 'expand',
                        'f': f[next_key],
                        'g': tentative_g,
                        'h': h_next,
                        'queue_size': len(priority_queue),
                        'visited_count': len(visited)
                    })
        
        return {
            'success': False,
            'path': [],
            'steps': steps,
            'algorithm': 'A*',
            'visited_count': len(visited)
        }
    
    def _reconstruct_path(self, parent, state):
        path = [state]
        key = self.puzzle.state_to_key(state)
        while key in parent:
            state = parent[key]
            path.append(state)
            key = self.puzzle.state_to_key(state)
        return path[::-1]
