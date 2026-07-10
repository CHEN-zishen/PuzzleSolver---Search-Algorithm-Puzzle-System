# PuzzleSolver - Search Algorithm Puzzle System

![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0%2B-green.svg)
![SQLite](https://img.shields.io/badge/database-sqlite-orange.svg)

一个交互式的搜索算法解谜系统，通过游戏界面展示搜索算法的建模、自动求解、动态演示与策略对比。系统包含迷宫、八数码、N皇后、数独和推箱子五类经典谜题，支持DFS、BFS、A*、回溯法四种搜索算法。

## ✨ 功能特性

### 🎮 谜题类型
- **迷宫** - 从起点寻找路径到达终点
- **八数码** - 将打乱的数字恢复到有序状态
- **N皇后** - 在N×N棋盘上放置N个互不攻击的皇后
- **数独** - 完成经典9×9数独谜题
- **推箱子** - 将所有箱子推到目标位置

### 🧠 算法支持
| 算法 | 数据结构 | 最优性 | 适用场景 |
|------|----------|--------|----------|
| DFS | 栈/递归 | 不保证 | 可行解搜索、遍历状态空间 |
| BFS | 队列 | 无权图保证最短 | 最短路径搜索 |
| A* | 优先队列 | 启发函数可采纳时保证最优 | 启发式路径搜索 |
| 回溯法 | 递归栈 | 取决于问题目标 | 约束满足问题 |

### 🎯 核心功能
- **自动求解** - 一键调用算法自动解决当前谜题
- **动态演示** - 播放/单步展示状态扩展、入队、访问、回退、剪枝和A*的f/g/h指标
- **策略对比** - 比较不同算法的路径长度、求解步数、访问节点、剪枝数量和耗时
- **学习助手** - 支持搜索算法概念、复杂度、适用场景的智能问答（本地知识库+DeepSeek API）
- **用户系统** - 注册、登录、关卡完成记录和个人进度统计
- **关卡生成** - 支持随机生成不同难度的谜题

### 🖼️ 界面预览

![首页截图](docs/screenshots/index.png)
![游戏界面截图](docs/screenshots/play.png)
![算法对比截图](docs/screenshots/compare.png)

## 🏗️ 项目架构

```mermaid
graph TD
    A[前端界面] -->|HTTP请求| B[Flask应用]
    B -->|数据库操作| C[(SQLite)]
    B -->|调用算法| D[算法模块]
    B -->|调用谜题| E[谜题模块]
    B -->|智能问答| F[学习助手]
    
    subgraph B [Flask应用 - app.py]
        B1[用户认证]
        B2[关卡管理]
        B3[求解API]
        B4[对比API]
        B5[助手API]
    end
    
    subgraph D [算法模块 - algorithms/]
        D1[DFS]
        D2[BFS]
        D3[A*]
        D4[回溯法]
    end
    
    subgraph E [谜题模块 - puzzles/]
        E1[迷宫]
        E2[八数码]
        E3[N皇后]
        E4[数独]
        E5[推箱子]
    end
    
    subgraph F [学习助手 - assistant/]
        F1[本地知识库]
        F2[DeepSeek API]
    end
    
    subgraph C [(SQLite - site.db)]
        C1[User]
        C2[Level]
        C3[SolveRecord]
    end
```

## 🚀 快速开始

### 环境要求
- Python 3.9+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动应用

```bash
python app.py
```

访问地址：`http://127.0.0.1:5000`

### 测试账号

```text
邮箱：test@demo.com
密码：123456
```

## 🔌 API 接口文档

### 求解接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/solve` | POST | 使用指定算法求解谜题 |
| `/api/compare_algorithms` | POST | 对比多种算法的求解结果 |
| `/api/generate_puzzle` | POST | 生成随机谜题 |

#### POST /api/solve

请求体：
```json
{
    "puzzle_type": "maze",
    "algorithm": "bfs",
    "input_data": [[2,0,1],[1,0,1],[0,0,3]],
    "level_id": 1
}
```

响应：
```json
{
    "success": true,
    "path": [...],
    "steps": [...],
    "algorithm": "BFS",
    "time_taken": 0.01,
    "steps_count": 10,
    "visited_count": 15
}
```

#### POST /api/compare_algorithms

请求体：
```json
{
    "puzzle_type": "eight_puzzle",
    "input_data": [[1,2,3],[4,0,5],[7,8,6]],
    "algorithms": ["bfs", "astar"]
}
```

响应：
```json
{
    "comparisons": [
        {"algorithm": "bfs", "success": true, "time_taken": 0.02, "path_length": 10, "visited_count": 50},
        {"algorithm": "astar", "success": true, "time_taken": 0.01, "path_length": 10, "visited_count": 25}
    ]
}
```

### 用户接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/complete_level` | POST | 标记关卡完成 |
| `/api/user_progress` | GET | 获取用户进度 |

### 学习助手接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/assistant` | POST | 向学习助手提问 |
| `/api/assistant/status` | GET | 获取助手状态 |
| `/api/assistant/learning_path` | GET | 获取学习路径 |
| `/api/assistant/algorithm_comparison` | GET | 获取算法对比信息 |

## 📊 算法实现

### DFS (深度优先搜索)

```python
class DFS:
    def solve(self):
        # 使用递归方式深度优先探索
        # visited集合防止重复访问
        # path记录当前路径，steps记录每一步操作
```

- **实现策略**：递归遍历每个分支，遇到目标状态返回成功，否则回溯
- **状态记录**：记录 visit、backtrack、goal_found 三种操作
- **复杂度**：时间 O(b^d)，空间 O(d)

### BFS (广度优先搜索)

```python
class BFS:
    def solve(self):
        # 使用deque队列按层扩展
        # parent字典记录路径回溯
```

- **实现策略**：队列存储状态和完整路径，按层扩展保证最短路径
- **状态记录**：记录 start、enqueue、goal_found 三种操作，包含队列大小
- **复杂度**：时间 O(b^d)，空间 O(b^d)

### A* (启发式搜索)

```python
class AStar:
    def solve(self):
        # 使用优先队列，按f=g+h排序
        # g: 起点到当前状态代价，h: 当前状态到目标的估计代价
```

- **实现策略**：使用 f(n) = g(n) + h(n) 评估节点优先级
- **启发函数**：各谜题实现自定义 heuristic() 方法（如八数码使用曼哈顿距离）
- **状态记录**：记录 f、g、h 三个指标，便于演示启发式搜索过程
- **复杂度**：时间 O(b^d)，空间 O(b^d)

### 回溯法

```python
class Backtracking:
    def solve(self):
        # 使用active_keys追踪当前路径（防止循环）
        # is_valid() 检查约束条件进行剪枝
```

- **实现策略**：逐步构造候选解，冲突时撤销选择并尝试其他分支
- **剪枝机制**：通过 is_valid() 检查约束，pruned_count 统计剪枝数量
- **状态记录**：记录 place、prune、prune_cycle、backtrack、goal_found 五种操作
- **复杂度**：时间 O(N!)，空间 O(N)

## 🧩 谜题状态建模

### 迷宫 (MazePuzzle)
- **状态表示**：二维数组，0=通道，1=墙壁，2=起点，3=终点
- **邻居生成**：上下左右四个方向，排除墙壁和边界

### 八数码 (EightPuzzle)
- **状态表示**：3×3二维数组，0=空格，1-8=数字
- **邻居生成**：空格与相邻位置交换
- **可解性检查**：逆序对数量判断
- **启发函数**：曼哈顿距离

### N皇后 (NQueenPuzzle)
- **状态表示**：一维数组，index=行号，value=列号（-1表示未放置）
- **邻居生成**：在下一行尝试所有合法列位置
- **约束检查**：列冲突、主对角线冲突、副对角线冲突

### 数独 (SudokuPuzzle)
- **状态表示**：9×9二维数组，0=空格，1-9=数字
- **邻居生成**：选择空格尝试填入1-9
- **约束检查**：行、列、3×3宫格冲突

### 推箱子 (SokobanPuzzle)
- **状态表示**：二维数组，0=空地，1=墙壁，2=玩家，3=目标点，4=箱子
- **邻居生成**：玩家推动箱子到新位置
- **启发函数**：箱子到最近目标的曼哈顿距离

## 🤖 学习助手配置

学习助手优先使用DeepSeek API进行智能问答，若未配置API Key则回退到本地知识库。

### 配置步骤

1. 复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的DeepSeek API Key：

```text
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-chat
```

3. 重启Flask服务

### 本地知识库

本地知识库支持以下主题的问答：
- DFS/BFS/A*/回溯法的概念、原理、复杂度
- 迷宫、八数码、N皇后、数独、推箱子的状态建模
- 启发函数、剪枝策略、状态空间分析

## 🧪 测试

运行核心算法测试：

```bash
python test_all.py
```

测试内容：
- 迷宫：DFS/BFS/A*/回溯法求解
- 八数码：DFS/BFS/A*/回溯法求解
- N皇后：DFS/BFS/A*/回溯法求解（4皇后）
- 数独：DFS/BFS/A*/回溯法求解
- 推箱子：DFS/BFS/A*/回溯法求解（简单难度）

## 📁 目录结构

```
├── app.py                    # Flask应用入口与API路由
├── models.py                 # 用户、关卡、求解记录模型（SQLAlchemy）
├── requirements.txt          # Python依赖列表
├── test_all.py               # 核心算法测试脚本
├── .env.example              # 环境变量配置模板
├── .gitignore                # Git忽略规则
├── algorithms/               # 搜索算法实现
│   ├── __init__.py
│   ├── dfs.py                # 深度优先搜索
│   ├── bfs.py                # 广度优先搜索
│   ├── astar.py              # A*启发式搜索
│   └── backtracking.py       # 回溯算法
├── puzzles/                  # 谜题状态建模
│   ├── __init__.py
│   ├── puzzle.py             # 基础谜题抽象类
│   ├── maze.py               # 迷宫谜题
│   ├── eight_puzzle.py       # 八数码谜题
│   ├── nqueen.py             # N皇后谜题
│   ├── sudoku.py             # 数独谜题
│   └── sokoban.py            # 推箱子谜题
├── assistant/                # 算法学习助手
│   ├── __init__.py
│   └── algorithm_assistant.py# 本地知识库+DeepSeek API集成
├── templates/                # Flask模板（HTML页面）
│   ├── index.html            # 首页
│   ├── login.html            # 登录页
│   ├── register.html         # 注册页
│   ├── play.html             # 游戏页面
│   ├── learn.html            # 学习页面
│   ├── profile.html          # 个人资料页
│   └── game_levels.html      # 关卡列表页
└── instance/
    └── site.db               # SQLite数据库文件（自动生成）
```

## 📋 当前关卡数量

| 谜题类型 | 简单 | 中等 | 困难 | 总计 |
|----------|------|------|------|------|
| 迷宫 | 2 | 1 | 2 | 5 |
| 八数码 | 1 | 2 | 2 | 5 |
| N皇后 | 2 | 1 | 2 | 5 |
| 数独 | 1 | 2 | 1 | 4 |
| 推箱子 | 1 | 2 | 1 | 4 |

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发规范
1. 代码风格遵循PEP 8
2. 使用清晰的变量和函数命名
3. 添加适当的注释说明复杂逻辑
4. 提交前运行测试确保代码正确

### 新增谜题/算法
1. 在`puzzles/`或`algorithms/`目录下新建文件
2. 继承基础类并实现必要方法
3. 在`__init__.py`中导出新类
4. 在`app.py`的`create_puzzle()`或`create_solver()`中注册
5. 添加测试用例

## 📄 License

MIT License

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue到项目仓库

---

**注意**：不要将包含真实密钥的`.env`文件提交到公开仓库。