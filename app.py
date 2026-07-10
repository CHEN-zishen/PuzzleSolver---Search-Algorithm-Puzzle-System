from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_cors import CORS
import json
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from algorithms.dfs import DFS
from algorithms.bfs import BFS
from algorithms.astar import AStar
from algorithms.backtracking import Backtracking
from puzzles.maze import MazePuzzle
from puzzles.eight_puzzle import EightPuzzle
from puzzles.nqueen import NQueenPuzzle
from puzzles.sudoku import SudokuPuzzle
from puzzles.sokoban import SokobanPuzzle
from assistant.algorithm_assistant import AlgorithmAssistant
from models import db, User, Level, SolveRecord

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
CORS(app)

assistant = AlgorithmAssistant()

def create_puzzle(puzzle_type, input_data, start_position=None):
    if puzzle_type == 'maze':
        return MazePuzzle(input_data, start=start_position)
    if puzzle_type == 'eight_puzzle':
        return EightPuzzle(input_data)
    if puzzle_type == 'nqueen':
        if isinstance(input_data, dict):
            return NQueenPuzzle(input_data.get('n', 4))
        return NQueenPuzzle(len(input_data), input_data)
    if puzzle_type == 'sudoku':
        return SudokuPuzzle(input_data)
    if puzzle_type == 'sokoban':
        return SokobanPuzzle(input_data)
    return None

def create_solver(algorithm, puzzle):
    if algorithm == 'dfs':
        return DFS(puzzle)
    if algorithm == 'bfs':
        return BFS(puzzle)
    if algorithm == 'astar':
        return AStar(puzzle)
    if algorithm == 'backtracking':
        return Backtracking(puzzle)
    return None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_test_user():
    """创建测试账号"""
    if not User.query.filter_by(email='test@demo.com').first():
        hashed_password = bcrypt.generate_password_hash('123456').decode('utf-8')
        test_user = User(username='测试用户', email='test@demo.com', password_hash=hashed_password)
        db.session.add(test_user)
        db.session.commit()
        print("测试账号已创建：test@demo.com / 123456")
    else:
        print("测试账号已存在：test@demo.com / 123456")

def init_levels():
    if Level.query.first():
        return
    
    levels = [
        {
            'name': '新手入门 - 简单迷宫',
            'puzzle_type': 'maze',
            'difficulty': 'easy',
            'description': '学习基本的搜索算法，找到从起点到终点的路径',
            'puzzle_data': json.dumps([[2,0,1],[1,0,1],[0,0,3]]),
            'hints': '尝试使用BFS算法找到最短路径',
            'order': 1
        },
        {
            'name': '初级挑战 - 中等迷宫',
            'puzzle_type': 'maze',
            'difficulty': 'medium',
            'description': '在更复杂的迷宫中应用搜索策略',
            'puzzle_data': json.dumps([[2,0,1,0,0,0,3],[0,0,1,0,1,1,0],[0,0,0,0,0,0,0],[1,1,1,0,1,1,1],[0,0,0,0,0,0,0],[0,1,1,0,1,1,0],[0,0,0,0,0,0,0]]),
            'hints': '注意观察路径的分支选择',
            'order': 2
        },
        {
            'name': '八数码入门',
            'puzzle_type': 'eight_puzzle',
            'difficulty': 'easy',
            'description': '学习经典的八数码问题，理解状态空间搜索',
            'puzzle_data': json.dumps([[1,2,3],[4,0,5],[7,8,6]]),
            'hints': '尝试使用A*算法，它会比DFS和BFS更高效',
            'order': 3
        },
        {
            'name': '八数码挑战',
            'puzzle_type': 'eight_puzzle',
            'difficulty': 'medium',
            'description': '更复杂的八数码配置，需要更多步数解决',
            'puzzle_data': '',
            'hints': 'A*算法的启发函数使用曼哈顿距离',
            'order': 4
        },
        {
            'name': '4皇后问题',
            'puzzle_type': 'nqueen',
            'difficulty': 'easy',
            'description': '学习回溯算法，在4x4棋盘上放置4个皇后',
            'puzzle_data': json.dumps([-1,-1,-1,-1]),
            'hints': '回溯法会尝试所有可能的放置位置',
            'order': 5
        },
        {
            'name': '6皇后问题',
            'puzzle_type': 'nqueen',
            'difficulty': 'medium',
            'description': '在6x6棋盘上放置6个皇后，练习剪枝技巧',
            'puzzle_data': json.dumps([-1]*6),
            'hints': '剪枝可以大大减少搜索空间',
            'order': 6
        },
        {
            'name': '数独入门',
            'puzzle_type': 'sudoku',
            'difficulty': 'easy',
            'description': '完成一个简单的数独谜题',
            'puzzle_data': json.dumps([
                [5,3,0,0,7,0,0,0,0],
                [6,0,0,1,9,5,0,0,0],
                [0,9,8,0,0,0,0,6,0],
                [8,0,0,0,6,0,0,0,3],
                [4,0,0,8,0,3,0,0,1],
                [7,0,0,0,2,0,0,0,6],
                [0,6,0,0,0,0,2,8,0],
                [0,0,0,4,1,9,0,0,5],
                [0,0,0,0,8,0,0,7,9]
            ]),
            'hints': '数独需要满足行、列、宫格的约束',
            'order': 7
        },
        {
            'name': '数独挑战',
            'puzzle_type': 'sudoku',
            'difficulty': 'hard',
            'description': '完成一个困难的数独谜题，需要高级策略',
            'puzzle_data': '',
            'hints': '尝试使用回溯法结合约束传播',
            'order': 8
        },
        {
            'name': '推箱子入门',
            'puzzle_type': 'sokoban',
            'difficulty': 'easy',
            'description': '学习推箱子游戏，将所有箱子推到目标位置',
            'puzzle_data': json.dumps([
                [1,1,1,1,1],
                [1,0,0,0,1],
                [1,0,2,0,1],
                [1,4,0,3,1],
                [1,1,1,1,1]
            ]),
            'hints': '推动箱子时要注意不要把箱子推到死角',
            'order': 9
        },
        {
            'name': '推箱子挑战',
            'puzzle_type': 'sokoban',
            'difficulty': 'medium',
            'description': '更复杂的推箱子关卡，需要更多策略',
            'puzzle_data': '',
            'hints': '规划好箱子的推动顺序',
            'order': 10
        },
        {
            'name': '高级迷宫',
            'puzzle_type': 'maze',
            'difficulty': 'hard',
            'description': '挑战一个大型复杂迷宫',
            'puzzle_data': json.dumps([[2,0,1,0,0,0,1,0,3],[0,0,1,0,1,1,1,0,1],[0,0,0,0,0,0,0,0,0],[1,1,1,0,1,1,1,0,1],[0,0,0,0,0,0,0,0,0],[0,1,0,0,1,0,0,1,0],[0,1,0,0,0,0,0,1,0],[0,0,0,0,1,0,0,0,0],[1,1,1,0,1,0,1,1,1]]),
            'hints': '比较不同算法的效率差异',
            'order': 13
        },
        {
            'name': '8皇后难题',
            'puzzle_type': 'nqueen',
            'difficulty': 'hard',
            'description': '在8x8棋盘上放置8个皇后，这是经典难题',
            'puzzle_data': json.dumps([-1]*8),
            'hints': '这道题有92种不同的解法',
            'order': 14
        }
    ]
    
    levels = [level for level in levels if level['puzzle_type'] != 'puzzle']

    for level_data in levels:
        level = Level(**level_data)
        db.session.add(level)
    db.session.commit()

def repair_level_data():
    """Keep the local level table playable and add enough verified levels."""
    catalog = [
        {
            'name': '迷宫入门',
            'puzzle_type': 'maze',
            'difficulty': 'easy',
            'description': '沿着通路从起点走到终点，练习边界和障碍判断。',
            'puzzle_data': [[2, 0, 1], [1, 0, 1], [0, 0, 3]],
            'hints': '先观察唯一通道，再用方向键移动。',
            'order': 1
        },
        {
            'name': '迷宫转角',
            'puzzle_type': 'maze',
            'difficulty': 'easy',
            'description': '稍复杂的 5x5 迷宫，适合比较 DFS 与 BFS。',
            'puzzle_data': [[2, 0, 0, 1, 0], [1, 1, 0, 1, 0], [0, 0, 0, 0, 0], [0, 1, 1, 1, 0], [0, 0, 0, 1, 3]],
            'hints': 'BFS 能稳定找到最短路线。',
            'order': 2
        },
        {
            'name': '迷宫岔路',
            'puzzle_type': 'maze',
            'difficulty': 'medium',
            'description': '包含多条岔路的 7x7 迷宫。',
            'puzzle_data': [[2, 0, 0, 1, 0, 0, 0], [1, 1, 0, 1, 0, 1, 0], [0, 0, 0, 0, 0, 1, 0], [0, 1, 1, 1, 0, 1, 1], [0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 3]],
            'hints': '记录访问过的位置，避免在岔路中绕圈。',
            'order': 3
        },
        {
            'name': '迷宫回廊',
            'puzzle_type': 'maze',
            'difficulty': 'hard',
            'description': '更大的回廊型迷宫，适合观察启发式搜索。',
            'puzzle_data': [[2, 0, 0, 1, 0, 0, 0, 0, 0], [0, 1, 0, 1, 0, 1, 1, 1, 0], [0, 1, 0, 0, 0, 0, 0, 1, 0], [0, 1, 1, 1, 1, 1, 0, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 1, 1, 1, 1, 1, 1, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 3]],
            'hints': 'A* 的曼哈顿距离会更偏向终点方向。',
            'order': 4
        },
        {
            'name': '迷宫长征',
            'puzzle_type': 'maze',
            'difficulty': 'hard',
            'description': '10x10 长路径迷宫，检验搜索效率。',
            'puzzle_data': [[2, 0, 1, 0, 0, 0, 1, 0, 0, 0], [0, 0, 1, 0, 1, 0, 1, 0, 1, 0], [0, 1, 1, 0, 1, 0, 0, 0, 1, 0], [0, 0, 0, 0, 1, 1, 1, 0, 1, 1], [1, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 1, 1, 1, 1, 0], [0, 1, 1, 0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 1, 1, 1, 0, 1, 0], [0, 1, 1, 1, 1, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 3]],
            'hints': '先找主通道，再处理分支。',
            'order': 5
        },
        {
            'name': '八数码入门',
            'puzzle_type': 'eight_puzzle',
            'difficulty': 'easy',
            'description': '一步步把数字恢复到 1-8 的顺序。',
            'puzzle_data': [[1, 2, 3], [4, 0, 5], [7, 8, 6]],
            'hints': '让空格靠近需要移动的数字。',
            'order': 1
        },
        {
            'name': '八数码交换',
            'puzzle_type': 'eight_puzzle',
            'difficulty': 'medium',
            'description': '需要绕一小圈才能恢复的状态。',
            'puzzle_data': [[1, 2, 3], [4, 8, 5], [7, 0, 6]],
            'hints': 'A* 配合曼哈顿距离会很快。',
            'order': 2
        },
        {
            'name': '八数码回环',
            'puzzle_type': 'eight_puzzle',
            'difficulty': 'medium',
            'description': '保证可解的中等八数码关卡。',
            'puzzle_data': [[4, 1, 3], [2, 8, 5], [7, 6, 0]],
            'hints': '先恢复上排，再处理下排。',
            'order': 3
        },
        {
            'name': '八数码进阶',
            'puzzle_type': 'eight_puzzle',
            'difficulty': 'hard',
            'description': '搜索空间更大，但仍经过 A* 验证可解。',
            'puzzle_data': [[5, 4, 1], [3, 0, 2], [7, 8, 6]],
            'hints': '不要只盯着一个数字，观察整体曼哈顿距离。',
            'order': 4
        },
        {
            'name': '八数码大师',
            'puzzle_type': 'eight_puzzle',
            'difficulty': 'hard',
            'description': '经典高难度可解状态，适合用 A* 演示。',
            'puzzle_data': [[8, 6, 7], [2, 5, 4], [3, 0, 1]],
            'hints': '这关建议直接使用 A*，DFS 会非常慢。',
            'order': 5
        },
        {
            'name': '4 皇后',
            'puzzle_type': 'nqueen',
            'difficulty': 'easy',
            'description': '在 4x4 棋盘上放置 4 个互不攻击的皇后。',
            'puzzle_data': {'n': 4, 'queens': []},
            'hints': '每行放一个皇后，注意列和对角线。',
            'order': 1
        },
        {
            'name': '5 皇后',
            'puzzle_type': 'nqueen',
            'difficulty': 'easy',
            'description': '5x5 棋盘更适合练习手动放置。',
            'puzzle_data': {'n': 5, 'queens': []},
            'hints': '从边缘行开始尝试，能减少冲突。',
            'order': 2
        },
        {
            'name': '6 皇后',
            'puzzle_type': 'nqueen',
            'difficulty': 'medium',
            'description': '6x6 棋盘开始体现回溯剪枝价值。',
            'puzzle_data': {'n': 6, 'queens': []},
            'hints': '冲突后退回上一行调整。',
            'order': 3
        },
        {
            'name': '8 皇后',
            'puzzle_type': 'nqueen',
            'difficulty': 'hard',
            'description': '经典 8 皇后问题。',
            'puzzle_data': {'n': 8, 'queens': []},
            'hints': '这关有 92 种解法。',
            'order': 4
        },
        {
            'name': '10 皇后',
            'puzzle_type': 'nqueen',
            'difficulty': 'hard',
            'description': '更大的棋盘，适合观察算法自动求解。',
            'puzzle_data': {'n': 10, 'queens': []},
            'hints': '优先使用回溯法。',
            'order': 5
        },
        {
            'name': '数独入门',
            'puzzle_type': 'sudoku',
            'difficulty': 'easy',
            'description': '经典入门数独，适合手动推理。',
            'puzzle_data': [[5, 3, 0, 0, 7, 0, 0, 0, 0], [6, 0, 0, 1, 9, 5, 0, 0, 0], [0, 9, 8, 0, 0, 0, 0, 6, 0], [8, 0, 0, 0, 6, 0, 0, 0, 3], [4, 0, 0, 8, 0, 3, 0, 0, 1], [7, 0, 0, 0, 2, 0, 0, 0, 6], [0, 6, 0, 0, 0, 0, 2, 8, 0], [0, 0, 0, 4, 1, 9, 0, 0, 5], [0, 0, 0, 0, 8, 0, 0, 7, 9]],
            'hints': '先找行、列、宫里唯一可填的格子。',
            'order': 1
        },
        {
            'name': '数独交叉',
            'puzzle_type': 'sudoku',
            'difficulty': 'medium',
            'description': '中等难度数独，需要更多排除。',
            'puzzle_data': [[0, 0, 0, 6, 0, 0, 4, 0, 0], [7, 0, 0, 0, 0, 3, 6, 0, 0], [0, 0, 0, 0, 9, 1, 0, 8, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 5, 0, 1, 8, 0, 0, 0, 3], [0, 0, 0, 3, 0, 6, 0, 4, 5], [0, 4, 0, 2, 0, 0, 0, 6, 0], [9, 0, 3, 0, 0, 0, 0, 0, 0], [0, 2, 0, 0, 0, 0, 1, 0, 0]],
            'hints': '优先处理给定数字较多的宫。',
            'order': 2
        },
        {
            'name': '数独进阶',
            'puzzle_type': 'sudoku',
            'difficulty': 'medium',
            'description': '经过回溯验证可解的进阶盘面。',
            'puzzle_data': [[0, 2, 0, 6, 0, 8, 0, 0, 0], [5, 8, 0, 0, 0, 9, 7, 0, 0], [0, 0, 0, 0, 4, 0, 0, 0, 0], [3, 7, 0, 0, 0, 0, 5, 0, 0], [6, 0, 0, 0, 0, 0, 0, 0, 4], [0, 0, 8, 0, 0, 0, 0, 1, 3], [0, 0, 0, 0, 2, 0, 0, 0, 0], [0, 0, 9, 8, 0, 0, 0, 3, 6], [0, 0, 0, 3, 0, 6, 0, 9, 0]],
            'hints': '可以让算法演示回溯过程。',
            'order': 3
        },
        {
            'name': '数独挑战',
            'puzzle_type': 'sudoku',
            'difficulty': 'hard',
            'description': '更稀疏的数独盘面，建议使用算法辅助。',
            'puzzle_data': [[0, 0, 5, 3, 0, 0, 0, 0, 0], [8, 0, 0, 0, 0, 0, 0, 2, 0], [0, 7, 0, 0, 1, 0, 5, 0, 0], [4, 0, 0, 0, 0, 5, 3, 0, 0], [0, 1, 0, 0, 7, 0, 0, 0, 6], [0, 0, 3, 2, 0, 0, 0, 8, 0], [0, 6, 0, 5, 0, 0, 0, 0, 9], [0, 0, 4, 0, 0, 0, 0, 3, 0], [0, 0, 0, 0, 0, 9, 7, 0, 0]],
            'hints': '这关适合观察搜索树。',
            'order': 4
        },
        {
            'name': '推箱子入门',
            'puzzle_type': 'sokoban',
            'difficulty': 'easy',
            'description': '把一个箱子推到目标点。',
            'puzzle_data': [[1, 1, 1, 1, 1], [1, 0, 0, 0, 1], [1, 2, 4, 3, 1], [1, 0, 0, 0, 1], [1, 1, 1, 1, 1]],
            'hints': '站到箱子左侧向右推。',
            'order': 1
        },
        {
            'name': '推箱子双箱',
            'puzzle_type': 'sokoban',
            'difficulty': 'medium',
            'description': '两个箱子的基础规划。',
            'puzzle_data': [[1, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 1], [1, 0, 3, 4, 3, 0, 1], [1, 0, 0, 2, 0, 0, 1], [1, 0, 3, 4, 3, 0, 1], [1, 0, 0, 0, 0, 0, 1], [1, 1, 1, 1, 1, 1, 1]],
            'hints': '先处理上方箱子，再处理下方箱子。',
            'order': 2
        },
        {
            'name': '推箱子走廊',
            'puzzle_type': 'sokoban',
            'difficulty': 'medium',
            'description': '狭窄走廊里的单箱规划。',
            'puzzle_data': [[1, 1, 1, 1, 1, 1], [1, 2, 0, 4, 3, 1], [1, 0, 0, 0, 0, 1], [1, 1, 1, 1, 1, 1]],
            'hints': '先调整站位，不要把箱子顶到墙角。',
            'order': 3
        },
        {
            'name': '推箱子回旋',
            'puzzle_type': 'sokoban',
            'difficulty': 'hard',
            'description': '需要绕行站位的可解关卡。',
            'puzzle_data': [[1, 1, 1, 1, 1, 1, 1], [1, 2, 0, 0, 0, 0, 1], [1, 0, 1, 0, 1, 0, 1], [1, 0, 4, 0, 3, 0, 1], [1, 0, 0, 0, 0, 0, 1], [1, 1, 1, 1, 1, 1, 1]],
            'hints': '绕到箱子左侧，再向右推进目标。',
            'order': 4
        },
    ]

    catalog = [level for level in catalog if level['puzzle_type'] != 'puzzle']
    removed = Level.query.filter_by(puzzle_type='puzzle').delete()
    changed = removed > 0
    for level_data in catalog:
        values = dict(level_data)
        values['puzzle_data'] = json.dumps(values['puzzle_data'])
        level = Level.query.filter_by(
            puzzle_type=values['puzzle_type'],
            order=values['order']
        ).first()

        if level is None:
            db.session.add(Level(**values))
            changed = True
            continue

        for key, value in values.items():
            if getattr(level, key) != value:
                setattr(level, key, value)
                changed = True

    if changed:
        db.session.commit()

@app.route('/')
@login_required
def index():
    levels = Level.query.order_by(Level.order).all()
    completed_levels = current_user.get_completed_levels()
    level_counts = {}
    for level in levels:
        level_counts[level.puzzle_type] = level_counts.get(level.puzzle_type, 0) + 1
    return render_template(
        'index.html',
        levels=[level.to_dict() for level in levels],
        completed_levels=completed_levels,
        level_counts=level_counts
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        data = request.form if request.form else request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已存在'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': '邮箱已被注册'}), 400
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': '注册成功'}), 200
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        data = request.form if request.form else request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        print(f"登录尝试 - 邮箱: {email}, 密码: {'*' * len(password) if password else 'None'}")
        
        user = User.query.filter_by(email=email).first()
        print(f"找到用户: {user.username if user else 'None'}")
        
        if user:
            is_valid = bcrypt.check_password_hash(user.password_hash, password)
            print(f"密码验证: {is_valid}")
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            if request.is_json:
                return jsonify({'message': '登录成功', 'user': user.username}), 200
            return redirect(url_for('index'))
        
        if request.is_json:
            return jsonify({'error': '邮箱或密码错误'}), 401
        flash('登录失败，请检查邮箱和密码', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/learn')
@login_required
def learn():
    return render_template('learn.html')

@app.route('/profile')
@login_required
def profile():
    levels = Level.query.order_by(Level.order).all()
    completed_levels = current_user.get_completed_levels()
    
    # 模拟收藏数据
    favorites = [
        {'id': 1, 'title': 'BFS广度优先搜索', 'description': '了解BFS算法的原理和应用'},
        {'id': 2, 'title': 'A*启发式搜索', 'description': '学习A*算法的启发函数设计'},
        {'id': 3, 'title': '回溯算法入门', 'description': '掌握回溯算法的基本思想'}
    ]
    
    return render_template(
        'profile.html',
        levels=levels,
        completed_levels=completed_levels,
        completed_count=len(completed_levels),
        total_count=len(levels),
        favorites=favorites,
        favorites_count=len(favorites),
        progress_percent=round(len(completed_levels)/len(levels)*100) if levels else 0
    )

@app.route('/level/<int:level_id>')
@login_required
def play_level(level_id):
    level = Level.query.get_or_404(level_id)
    return render_template('play.html', level=level)

@app.route('/games/<string:game_type>')
@login_required
def game_levels(game_type):
    if game_type == 'puzzle':
        flash('拼图游戏已移除，请选择其他算法游戏。', 'info')
        return redirect(url_for('index'))
    # 获取指定游戏类型的所有关卡
    levels = Level.query.filter_by(puzzle_type=game_type).order_by(Level.order).all()
    
    if not levels:
        # 如果没有找到对应类型的关卡，显示所有关卡
        levels = Level.query.order_by(Level.order).all()
        game_type = 'all'
    
    return render_template('game_levels.html', game_type=game_type, levels=levels)

@app.route('/api/solve', methods=['POST'])
@login_required
def solve_puzzle():
    data = request.json
    puzzle_type = data.get('puzzle_type')
    algorithm = data.get('algorithm')
    input_data = data.get('input_data')
    level_id = data.get('level_id')
    
    if puzzle_type == 'maze':
        # 获取自定义起点，如果有的话
        start_pos = data.get('start_position')
    elif puzzle_type == 'eight_puzzle':
        # 检查八数码状态是否可解
        tiles = [x for row in input_data for x in row]
        if not EightPuzzle._is_solvable(tiles):
            return jsonify({
                'error': '当前状态不可解',
                'message': '八数码问题存在不可解的状态。请点击"重新开始"按钮重新开始游戏。'
            })
        start_pos = None
    else:
        start_pos = None
    
    puzzle = create_puzzle(puzzle_type, input_data, start_pos)
    
    if not puzzle:
        return jsonify({'error': 'Invalid puzzle type'})
    
    solver = create_solver(algorithm, puzzle)
    
    if not solver:
        return jsonify({'error': 'Invalid algorithm'})
    
    start_time = time.time()
    result = solver.solve()
    time_taken = time.time() - start_time
    
    result['time_taken'] = round(time_taken, 2)
    result['steps_count'] = len(result['steps']) if result['success'] else 0
    return jsonify(result)

@app.route('/api/compare_algorithms', methods=['POST'])
@login_required
def compare_algorithms():
    data = request.json
    puzzle_type = data.get('puzzle_type')
    input_data = data.get('input_data')
    algorithms = data.get('algorithms') or ['bfs', 'astar']
    start_position = data.get('start_position')

    if puzzle_type == 'eight_puzzle':
        tiles = [x for row in input_data for x in row]
        solvable = EightPuzzle._is_solvable(tiles)
        if not solvable:
            return jsonify({'error': '当前状态不可解，无法进行算法对比。'}), 400

    comparisons = []
    for algorithm in algorithms:
        puzzle = create_puzzle(puzzle_type, input_data, start_position if puzzle_type == 'maze' else None)
        solver = create_solver(algorithm, puzzle)
        if not solver:
            continue

        start_time = time.time()
        try:
            result = solver.solve()
            error = None
        except Exception as exc:
            result = {'success': False, 'path': [], 'steps': []}
            error = str(exc)
        time_taken = time.time() - start_time

        comparisons.append({
            'algorithm': algorithm,
            'success': bool(result.get('success')),
            'time_taken': round(time_taken, 4),
            'path_length': len(result.get('path', [])),
            'steps_count': len(result.get('steps', [])),
            'visited_count': result.get('visited_count'),
            'pruned_count': result.get('pruned_count'),
            'error': error
        })

    return jsonify({'comparisons': comparisons})

@app.route('/api/complete_level', methods=['POST'])
@login_required
def complete_level():
    data = request.json
    level_id = data.get('level_id')
    algorithm = data.get('algorithm')
    steps = data.get('steps')
    time_taken = data.get('time_taken')
    
    if level_id:
        current_user.add_completed_level(level_id)
        
        record = SolveRecord(
            user_id=current_user.id,
            level_id=level_id,
            algorithm=algorithm,
            steps=steps,
            time_taken=time_taken
        )
        db.session.add(record)
        db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/assistant', methods=['POST'])
@login_required
def get_assistant_response():
    data = request.json
    question = data.get('question')
    context = data.get('context', {})
    
    response = assistant.answer(question, context)
    return jsonify({
        'response': response,
        'source': assistant.last_source,
        'api_error': assistant.last_error
    })

@app.route('/api/assistant/status', methods=['GET'])
@login_required
def get_assistant_status():
    return jsonify(assistant.get_status())

@app.route('/api/generate_puzzle', methods=['POST'])
@login_required
def generate_puzzle():
    data = request.json
    puzzle_type = data.get('puzzle_type')
    difficulty = data.get('difficulty', 'medium')
    
    puzzle = None
    if puzzle_type == 'maze':
        size = {'easy': 5, 'medium': 8, 'hard': 12}[difficulty]
        puzzle = MazePuzzle.generate(size)
    elif puzzle_type == 'eight_puzzle':
        puzzle = EightPuzzle.generate()
    elif puzzle_type == 'nqueen':
        size = {'easy': 4, 'medium': 6, 'hard': 8}[difficulty]
        puzzle = NQueenPuzzle.generate(size)
    elif puzzle_type == 'sudoku':
        puzzle = SudokuPuzzle.generate(difficulty)
    elif puzzle_type == 'sokoban':
        puzzle = SokobanPuzzle.generate(difficulty)
    if puzzle:
        return jsonify({'puzzle': puzzle.export()})
    return jsonify({'error': 'Invalid puzzle type'})

@app.route('/api/user_progress')
@login_required
def user_progress():
    completed = current_user.get_completed_levels()
    total_levels = Level.query.count()
    records = SolveRecord.query.filter_by(user_id=current_user.id).all()
    
    stats = {
        'completed_levels': len(completed),
        'total_levels': total_levels,
        'completion_rate': round(len(completed) / total_levels * 100, 1),
        'solve_count': len(records)
    }
    
    return jsonify(stats)

@app.route('/api/level/<int:level_id>')
@login_required
def get_level(level_id):
    level = Level.query.get_or_404(level_id)
    return jsonify(level.to_dict())

@app.route('/api/assistant/learning_path', methods=['GET'])
@login_required
def get_learning_path():
    level = request.args.get('level', 1, type=int)
    path = assistant.get_learning_path(level)
    return jsonify(path)

@app.route('/api/assistant/algorithm_comparison', methods=['GET'])
@login_required
def get_algorithm_comparison():
    comparison = assistant.get_algorithm_comparison()
    return jsonify(comparison)

@app.route('/api/assistant/analyze_complexity', methods=['POST'])
@login_required
def analyze_complexity():
    data = request.json
    algorithm = data.get('algorithm')
    problem_size = data.get('problem_size', 8)
    analysis = assistant.analyze_complexity(algorithm, problem_size)
    return jsonify(analysis)

@app.route('/api/assistant/ask', methods=['POST'])
@login_required
def ask_assistant():
    data = request.json
    question = data.get('question')
    context = data.get('context', {})
    
    response = assistant.answer(question, context)
    return jsonify({
        'response': response,
        'question': question,
        'timestamp': time.time()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_test_user()
        init_levels()
        repair_level_data()
    app.run(debug=True)
