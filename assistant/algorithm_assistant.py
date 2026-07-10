import os
import requests

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        env_path = os.path.join(os.getcwd(), ".env")
        if not os.path.exists(env_path):
            return False
        with open(env_path, "r", encoding="utf-8") as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
        return True


load_dotenv()


class AlgorithmAssistant:
    def __init__(self):
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        self.deepseek_api_url = os.getenv(
            "DEEPSEEK_API_URL",
            "https://api.deepseek.com/v1/chat/completions"
        ).strip()
        self.deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()
        self.last_source = "local"
        self.last_error = None

    def _build_messages(self, question, context):
        puzzle_type = context.get("puzzle_type") or "未指定"
        algorithm = context.get("algorithm") or "未指定"
        page = context.get("page") or "未指定"

        system_prompt = (
            "你是一个算法学习助手，面向《算法设计与分析》课程项目。"
            "请直接回答用户的问题，不要说用户没有提问。"
            "回答必须使用清晰中文，围绕搜索算法、状态空间、复杂度、剪枝、启发函数、"
            "迷宫、八数码、N皇后、数独、推箱子等内容展开。"
            "如果用户问概念，请给出定义、核心思想、适用场景和简单例子。"
            "如果用户问当前关卡，请结合上下文解释当前算法为什么这样扩展状态。"
            "回答长度控制在 3 到 8 句话，必要时可使用简短列表。"
        )

        user_prompt = (
            f"页面：{page}\n"
            f"当前谜题类型：{puzzle_type}\n"
            f"当前算法：{algorithm}\n"
            f"用户问题：{question}\n\n"
            "请直接针对用户问题回答。"
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _is_bad_api_answer(self, answer):
        if not answer:
            return True

        bad_phrases = [
            "没有收到",
            "没有输入具体问题",
            "没有具体的提问内容",
            "只包含问号",
            "无法理解您的问题",
            "请补充信息",
            "????????",
        ]
        return any(phrase in answer for phrase in bad_phrases)

    def call_deepseek_api(self, question, context=None):
        self.last_error = None

        if not self.deepseek_api_key:
            self.last_error = "未配置 DEEPSEEK_API_KEY"
            return None

        context = context or {}
        payload = {
            "model": self.deepseek_model,
            "messages": self._build_messages(question, context),
            "temperature": 0.4,
            "max_tokens": 1200,
        }

        try:
            response = requests.post(
                self.deepseek_api_url,
                headers={
                    "Authorization": f"Bearer {self.deepseek_api_key}",
                    "Content-Type": "application/json; charset=utf-8",
                },
                json=payload,
                timeout=30,
            )
            if response.status_code != 200:
                self.last_error = f"DeepSeek API HTTP {response.status_code}: {response.text[:200]}"
                return None

            response.encoding = "utf-8"
            result = response.json()
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            answer = answer.strip()
            if self._is_bad_api_answer(answer):
                self.last_error = "DeepSeek API 返回内容无效，已回退本地知识库"
                return None
            return answer
        except Exception as exc:
            self.last_error = f"DeepSeek API 请求失败：{exc}"
            return None

    def _local_answer(self, question, context=None):
        text = (question or "").lower()
        context = context or {}
        algorithm = (context.get("algorithm") or "").lower()

        if any(word in text for word in ["dfs", "深度优先"]) or algorithm == "dfs":
            return (
                "深度优先搜索（DFS）会沿着一条分支尽可能向深处探索，走不通时再回退到上一个分支点。"
                "它通常用递归或栈实现，空间开销较小，适合寻找可行解、遍历状态空间和回溯类问题。"
                "但 DFS 不保证找到最短路径，若没有 visited 集合还可能在有环状态中重复搜索。"
            )

        if any(word in text for word in ["bfs", "广度优先"]) or algorithm == "bfs":
            return (
                "广度优先搜索（BFS）从起点开始按层扩展状态，先访问距离起点 1 步的状态，再访问 2 步的状态。"
                "它通常用队列实现，在无权图或每一步代价相同的谜题中可以保证最短路径。"
                "缺点是需要保存大量待扩展节点，空间复杂度通常高于 DFS。"
            )

        if any(word in text for word in ["a*", "astar", "启发", "启发式"]) or algorithm == "astar":
            return (
                "A* 是启发式搜索算法，使用 f(n)=g(n)+h(n) 评估节点优先级。"
                "其中 g(n) 是从起点到当前状态的实际代价，h(n) 是到目标状态的估计代价。"
                "当 h(n) 不高估真实代价时，A* 能在保证最优解的同时减少无效扩展，八数码常用曼哈顿距离作为启发函数。"
            )

        if any(word in text for word in ["回溯", "backtracking", "剪枝"]) or algorithm == "backtracking":
            return (
                "回溯法会逐步构造候选解，每做一个选择就检查是否满足约束。"
                "如果当前选择导致冲突，就撤销选择并尝试其他分支。"
                "剪枝是在搜索中提前排除不可能成功的分支，能显著减少 N 皇后、数独等问题的搜索空间。"
            )

        if any(word in text for word in ["复杂度", "时间", "空间"]):
            return (
                "搜索算法复杂度通常和分支因子 b、搜索深度 d 有关。"
                "DFS 的时间复杂度常写作 O(b^d)，空间复杂度约为 O(d)；BFS 和 A* 需要保存更多候选节点，空间复杂度常为 O(b^d)。"
                "回溯法在 N 皇后这类组合问题中最坏可达到阶乘级，但剪枝能明显减少实际搜索量。"
            )

        if any(word in text for word in ["迷宫", "路径"]):
            return (
                "迷宫问题可以建模为状态空间搜索：每个格子位置是一个状态，上下左右移动是状态转移。"
                "BFS 适合寻找最短路径，DFS 适合演示深入探索和回退，A* 可以利用当前位置到终点的曼哈顿距离加速搜索。"
            )

        if any(word in text for word in ["八数码", "数码"]):
            return (
                "八数码的状态是 3x3 棋盘排列，操作是把空格与相邻数字交换。"
                "它的状态空间较大，BFS 能保证最短步数，但扩展节点多；A* 配合曼哈顿距离通常更高效。"
            )

        if any(word in text for word in ["皇后", "n皇后", "n 皇后"]):
            return (
                "N 皇后是约束满足问题，需要在 N 行 N 列棋盘中放置 N 个互不攻击的皇后。"
                "常用回溯法逐行放置皇后，并用列冲突、主对角线冲突、副对角线冲突进行剪枝。"
            )

        if any(word in text for word in ["数独"]):
            return (
                "数独可以用回溯法求解：选择一个空格，尝试填入 1 到 9，并检查行、列和 3x3 宫是否冲突。"
                "如果某个数字导致后续无解，就回退并尝试下一个数字。"
            )

        if any(word in text for word in ["推箱子", "箱子"]):
            return (
                "推箱子可以看作状态空间搜索，状态由玩家位置和箱子位置共同决定。"
                "搜索时不仅要判断玩家能否移动，还要判断箱子能否被推动到合法位置，避免推入死角。"
            )

        return (
            "我可以解释 DFS、BFS、A*、回溯法、剪枝、启发函数和复杂度，也可以结合迷宫、八数码、N皇后、数独、推箱子说明搜索过程。"
            "你可以直接问：什么是 A*？BFS 为什么能找到最短路径？N 皇后为什么适合回溯？"
        )

    def answer(self, question, context=None):
        context = context or {}

        api_answer = self.call_deepseek_api(question, context)
        if api_answer:
            self.last_source = "deepseek"
            return api_answer

        self.last_source = "local"
        return self._local_answer(question, context)

    def get_status(self):
        return {
            "api_configured": bool(self.deepseek_api_key),
            "api_url": self.deepseek_api_url,
            "model": self.deepseek_model,
            "last_source": self.last_source,
            "last_error": self.last_error,
        }

    def get_learning_path(self, level=1):
        paths = {
            1: {
                "stage": "入门阶段",
                "algorithms": ["DFS", "BFS"],
                "puzzles": ["迷宫"],
                "goals": ["理解状态空间", "掌握栈和队列", "能手动模拟搜索过程"],
            },
            2: {
                "stage": "进阶阶段",
                "algorithms": ["A*", "启发函数"],
                "puzzles": ["八数码", "迷宫"],
                "goals": ["理解 f(n)=g(n)+h(n)", "学习曼哈顿距离", "比较 BFS 与 A* 效率"],
            },
            3: {
                "stage": "提高阶段",
                "algorithms": ["回溯法", "剪枝"],
                "puzzles": ["N皇后", "数独", "推箱子"],
                "goals": ["理解约束满足问题", "设计剪枝条件", "分析搜索树规模"],
            },
        }
        return paths.get(level, paths[1])

    def get_algorithm_comparison(self):
        return {
            "algorithms": ["DFS", "BFS", "A*", "回溯法"],
            "time_complexity": ["O(b^d)", "O(b^d)", "O(b^d)", "O(N!)"],
            "space_complexity": ["O(d)", "O(b^d)", "O(b^d)", "O(N)"],
            "optimality": ["不保证", "无权图保证最短", "启发函数可采纳时保证最优", "取决于问题目标"],
            "best_for": ["可行解搜索", "最短路径", "启发式路径搜索", "约束满足问题"],
            "data_structure": ["栈/递归", "队列", "优先队列", "递归栈"],
        }

    def analyze_complexity(self, algorithm, problem_size):
        analysis = {
            "dfs": {
                "time": f"O(b^{problem_size})",
                "space": f"O({problem_size})",
                "explanation": "DFS 最坏情况下需要搜索到指定深度，空间主要来自递归栈或显式栈。",
            },
            "bfs": {
                "time": f"O(b^{problem_size})",
                "space": f"O(b^{problem_size})",
                "explanation": "BFS 需要保存同一层的大量候选节点，因此空间开销较大。",
            },
            "astar": {
                "time": f"O(b^{problem_size})",
                "space": f"O(b^{problem_size})",
                "explanation": "A* 的实际效率取决于启发函数质量，好的启发函数能显著减少扩展节点。",
            },
            "backtracking": {
                "time": f"O({problem_size}!)",
                "space": f"O({problem_size})",
                "explanation": "回溯法最坏情况下可能枚举大量组合，但剪枝可以显著降低实际搜索量。",
            },
        }
        return analysis.get(algorithm, {})
