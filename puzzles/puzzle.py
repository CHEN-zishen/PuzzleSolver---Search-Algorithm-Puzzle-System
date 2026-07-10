import random


class SlidingPuzzle:
    def __init__(self, grid=None):
        if grid is not None:
            self.grid = grid
            self.size = len(grid)
            self.empty_pos = self._find_empty()
        else:
            self.grid = []
            self.size = 3
            self.empty_pos = (0, 0)

    @staticmethod
    def generate(size=3, difficulty='easy'):
        numbers = list(range(size * size))
        random.shuffle(numbers)

        while not SlidingPuzzle._is_solvable(numbers, size):
            random.shuffle(numbers)

        grid = [numbers[i * size:(i + 1) * size] for i in range(size)]
        return SlidingPuzzle(grid)

    @staticmethod
    def _is_solvable(numbers, size):
        inversions = 0
        nums = [n for n in numbers if n != 0]

        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] > nums[j]:
                    inversions += 1

        if size % 2 == 1:
            return inversions % 2 == 0

        empty_row = numbers.index(0) // size
        row_from_bottom = size - empty_row
        return (inversions + row_from_bottom) % 2 == 1

    def _find_empty(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    return (i, j)
        return (0, 0)

    def get_initial_state(self):
        return tuple(tuple(row) for row in self.grid)

    def is_goal(self, state):
        numbers = []
        for row in state:
            numbers.extend(row)

        for i in range(len(numbers) - 1):
            if numbers[i] != i + 1:
                return False
        return numbers[-1] == 0

    def get_neighbors(self, state):
        empty_row, empty_col = self._find_empty_in_state(state)
        neighbors = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dr, dc in directions:
            new_row, new_col = empty_row + dr, empty_col + dc

            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                new_grid = [list(row) for row in state]
                new_grid[empty_row][empty_col], new_grid[new_row][new_col] = (
                    new_grid[new_row][new_col],
                    new_grid[empty_row][empty_col],
                )
                neighbors.append(tuple(tuple(row) for row in new_grid))

        return neighbors

    def _find_empty_in_state(self, state):
        for i in range(self.size):
            for j in range(self.size):
                if state[i][j] == 0:
                    return (i, j)
        return (0, 0)

    def state_to_key(self, state):
        return state

    def heuristic(self, state):
        total_dist = 0
        for i in range(self.size):
            for j in range(self.size):
                value = state[i][j]
                if value != 0:
                    target_row = (value - 1) // self.size
                    target_col = (value - 1) % self.size
                    total_dist += abs(i - target_row) + abs(j - target_col)
        return total_dist

    def is_valid(self, state):
        return True

    def export(self):
        return self.grid
