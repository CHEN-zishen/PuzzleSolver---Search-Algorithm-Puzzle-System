from algorithms.dfs import DFS
from algorithms.bfs import BFS
from algorithms.astar import AStar
from algorithms.backtracking import Backtracking

from puzzles.maze import MazePuzzle
from puzzles.eight_puzzle import EightPuzzle
from puzzles.nqueen import NQueenPuzzle
from puzzles.sudoku import SudokuPuzzle
from puzzles.sokoban import SokobanPuzzle

def test():
    print("Testing Maze...")
    for alg in [DFS, BFS, AStar, Backtracking]:
        try:
            m = MazePuzzle.generate()
            m.grid[1][1] = 0
            m.grid[0][0] = 2
            m.grid[-1][-1] = 3
            res = alg(m).solve()
            print(f"Maze {alg.__name__} path length:", len(res['path']))
        except Exception as e:
            print(f"Maze {alg.__name__} error:", e)

    print("Testing EightPuzzle...")
    for alg in [DFS, BFS, AStar, Backtracking]:
        try:
            p = EightPuzzle([[1,2,3],[4,5,6],[7,0,8]])
            res = alg(p).solve()
            print(f"EightPuzzle {alg.__name__} success:", res['success'])
        except Exception as e:
            print(f"EightPuzzle {alg.__name__} error:", type(e).__name__, e)

    print("Testing NQueen...")
    for alg in [DFS, BFS, AStar, Backtracking]:
        try:
            p = NQueenPuzzle(4)
            res = alg(p).solve()
            print(f"NQueen {alg.__name__} success:", res['success'])
        except Exception as e:
            print(f"NQueen {alg.__name__} error:", e)

    print("Testing Sudoku...")
    for alg in [DFS, BFS, AStar, Backtracking]:
        try:
            p = SudokuPuzzle.generate()
            res = alg(p).solve()
            print(f"Sudoku {alg.__name__} success:", res['success'])
        except Exception as e:
            print(f"Sudoku {alg.__name__} error:", e)

    print("Testing Sokoban...")
    for alg in [DFS, BFS, AStar, Backtracking]:
        try:
            p = SokobanPuzzle.generate('easy')
            res = alg(p).solve()
            print(f"Sokoban {alg.__name__} success:", res['success'])
        except Exception as e:
            print(f"Sokoban {alg.__name__} error:", e)

if __name__ == '__main__':
    test()
