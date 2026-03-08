"""
Hitori Puzzle Solver - 基于逻辑推理的求解器

Hitori 规则:
1. 每一行和每一列中，未被涂黑的数字不能重复
2. 涂黑的格子不能水平或垂直相邻
3. 所有未被涂黑的格子必须连通

状态：0=未知，1=白色 (保留)，2=黑色 (涂黑)
"""

import time
import copy
from collections import deque
from typing import Optional


class UnionFind:
    """并查集数据结构，用于高效检查和合并连通分量"""

    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        """查找根节点，带路径压缩"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int):
        """合并两个集合，按秩合并"""
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return

        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1


class HitoriSolver:
    # 状态常量
    UNKNOWN = 0
    WHITE = 1
    BLACK = 2

    def __init__(self, time_limit: float = 5.0):
        self.time_limit = time_limit
        self.start_time = 0
        self.grid = []
        self.size = 0
        self.state = []  # 每个格子的状态
        self.propagation_queue = deque()  # 传播队列

    def set_grid(self, grid: list[list[int]]):
        """设置谜题网格"""
        self.size = len(grid)
        self.grid = grid
        self.state = [[self.UNKNOWN] * self.size for _ in range(self.size)]
        self.start_time = 0
        self.propagation_queue = deque()

    def get_state_name(self, s: int) -> str:
        """获取状态名称"""
        return ["未知", "白", "黑"][s]

    def set_cell_state(self, r: int, c: int, state: int):
        """
        设置格子状态，并将变化加入传播队列
        """
        if self.state[r][c] != state:
            self.state[r][c] = state
            self.propagation_queue.append((r, c))

    def propagate_changes(self) -> bool:
        """
        使用队列传播规则 4 和规则 5
        规则 4: 黑色格子的邻居必须是白色
        规则 5: 白色格子的同行同列相同数字必须是黑色
        返回是否有变化
        """
        changed = False

        while self.propagation_queue:
            r, c = self.propagation_queue.popleft()
            current_state = self.state[r][c]

            if current_state == self.BLACK:
                # 规则 4: 黑色格子的邻居必须是白色
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.size and 0 <= nc < self.size:
                        if self.state[nr][nc] == self.UNKNOWN:
                            self.set_cell_state(nr, nc, self.WHITE)
                            changed = True

            elif current_state == self.WHITE:
                # 规则 5: 白色格子的同行同列相同数字必须是黑色
                val = self.grid[r][c]

                # 同行
                for cc in range(self.size):
                    if cc != c and self.grid[r][cc] == val:
                        if self.state[r][cc] == self.UNKNOWN:
                            self.set_cell_state(r, cc, self.BLACK)
                            changed = True

                # 同列
                for rr in range(self.size):
                    if rr != r and self.grid[rr][c] == val:
                        if self.state[rr][c] == self.UNKNOWN:
                            self.set_cell_state(rr, c, self.BLACK)
                            changed = True

        return changed

    # ========== 基础推理规则 ==========

    def rule_sandwich_must_be_white(self) -> bool:
        """
        规则 1: 两个相同数字中间隔一个数字，中间的数字必须是白色（静态规则）
        例如：3 X 3，那么 X 必须是白色
        因为如果 X 是黑色，两个 3 都必须是白色，但它们在同一行/列会冲突
        """
        changed = False

        # 检查行中的 "ABA" 模式
        for r in range(self.size):
            for c in range(self.size - 2):
                if self.grid[r][c] == self.grid[r][c + 2]:
                    # 中间格子必须是白色
                    if self.state[r][c + 1] == self.UNKNOWN:
                        self.set_cell_state(r, c + 1, self.WHITE)
                        changed = True

        # 检查列中的 "ABA" 模式
        for c in range(self.size):
            for r in range(self.size - 2):
                if self.grid[r][c] == self.grid[r + 2][c]:
                    # 中间格子必须是白色
                    if self.state[r + 1][c] == self.UNKNOWN:
                        self.set_cell_state(r + 1, c, self.WHITE)
                        changed = True

        return changed

    def rule_corner_sandwich(self) -> bool:
        """
        规则 2: L 形三个相同数字，角上的必须是白色（静态规则）
        例如：
          3 3
          3
        角上的 3 如果是黑色，会导致两个相邻黑色
        """
        changed = False

        for r in range(self.size - 1):
            for c in range(self.size - 1):
                val = self.grid[r][c]
                if self.grid[r][c + 1] == val and self.grid[r + 1][c] == val:
                    # 三个数字形成 L 形
                    if self.state[r][c] == self.UNKNOWN:
                        self.set_cell_state(r, c, self.WHITE)
                        changed = True

        return changed

    def rule_adjacent_same_pair(self) -> bool:
        """
        规则 3: 两个相邻的相同数字（静态规则）

        如果一行/列中有两个相邻的相同数字（如 3 3），则：
        - 这两个数字中必有一个是黑色（不能同时为白色）
        - 这行/列中其他位置的相同数字必须是黑色
          （因为无论哪个相邻数字是白色，都会排除其他相同数字）

        例如：3 3 X 3，那么 X 和最后一个 3 必须是黑色
        """
        changed = False

        # 检查水平相邻的相同数字
        for r in range(self.size):
            for c in range(self.size - 1):
                if self.grid[r][c] == self.grid[r][c + 1]:
                    val = self.grid[r][c]
                    # 这行中其他相同数字必须是黑色
                    for cc in range(self.size):
                        if cc != c and cc != c + 1 and self.grid[r][cc] == val:
                            if self.state[r][cc] == self.UNKNOWN:
                                self.set_cell_state(r, cc, self.BLACK)
                                changed = True

        # 检查垂直相邻的相同数字
        for c in range(self.size):
            for r in range(self.size - 1):
                if self.grid[r][c] == self.grid[r + 1][c]:
                    val = self.grid[r][c]
                    # 这列中其他相同数字必须是黑色
                    for rr in range(self.size):
                        if rr != r and rr != r + 1 and self.grid[rr][c] == val:
                            if self.state[rr][c] == self.UNKNOWN:
                                self.set_cell_state(rr, c, self.BLACK)
                                changed = True

        return changed

    def rule_black_neighbors_must_be_white(self) -> bool:
        """
        规则 4: 黑色格子的相邻格子必须是白色
        注意：这个规则主要由 propagate_changes 通过队列处理
        """
        # 这个规则已经在 propagate_changes 中处理
        return False

    def rule_white_excludes_same(self) -> bool:
        """
        规则 5: 当一个数字被标记为白色，同行/同列的相同数字必须为黑色
        注意：这个规则主要由 propagate_changes 通过队列处理
        """
        # 这个规则已经在 propagate_changes 中处理
        return False

    def _check_connectivity_uf(self) -> bool:
        """
        使用并查集检查所有白色格子是否连通
        直接使用坐标计算索引：idx = r * size + c
        """
        # 找到第一个白色格子
        first_white = -1
        white_count = 0

        for r in range(self.size):
            for c in range(self.size):
                if self.state[r][c] == self.WHITE:
                    if first_white == -1:
                        first_white = r * self.size + c
                    white_count += 1

        if white_count <= 1:
            return True  # 0 或 1 个白色格子，连通性自动满足

        # 初始化并查集（最大可能的大小）
        uf = UnionFind(self.size * self.size)

        # 合并相邻的白色格子
        for r in range(self.size):
            for c in range(self.size):
                if self.state[r][c] == self.WHITE:
                    idx = r * self.size + c
                    # 只检查右和下，避免重复
                    if c + 1 < self.size and self.state[r][c + 1] == self.WHITE:
                        uf.union(idx, r * self.size + (c + 1))
                    if r + 1 < self.size and self.state[r + 1][c] == self.WHITE:
                        uf.union(idx, (r + 1) * self.size + c)

        # 检查是否所有白色格子在同一连通分量
        root = uf.find(first_white)
        for r in range(self.size):
            for c in range(self.size):
                if self.state[r][c] == self.WHITE:
                    if uf.find(r * self.size + c) != root:
                        return False

        return True

    # ========== 预处理和规则应用 ==========

    def preprocess(self) -> int:
        """
        预处理：应用所有静态规则（只需运行一次）
        静态规则：只依赖网格数字模式，不依赖格子状态变化
        返回变化的次数
        """
        changes = 0

        # 规则 1: 三明治规则 (ABA 模式)
        if self.rule_sandwich_must_be_white():
            changes += 1

        # 规则 2: 角落规则 (L 形三同数)
        if self.rule_corner_sandwich():
            changes += 1

        # 规则 3: 相邻相同数字对（排除同行/列其他相同数字）
        if self.rule_adjacent_same_pair():
            changes += 1

        return changes

    def rule_white_single_unknown_neighbor(self) -> bool:
        """
        规则 6: 如果一个白色格子的周围恰好只有一个未知格子，其他都是黑色，
               就把那个未知格子标记为白色
        原因：如果这个未知格子是黑色，白色格子会被黑色包围，可能导致孤立
        """
        changed = False

        for r in range(self.size):
            for c in range(self.size):
                if self.state[r][c] != self.WHITE:
                    continue

                # 统计邻居状态
                unknown_neighbors = []
                black_count = 0
                white_count = 0

                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.size and 0 <= nc < self.size:
                        neighbor_state = self.state[nr][nc]
                        if neighbor_state == self.UNKNOWN:
                            unknown_neighbors.append((nr, nc))
                        elif neighbor_state == self.BLACK:
                            black_count += 1
                        elif neighbor_state == self.WHITE:
                            white_count += 1

                # 检查：恰好一个未知，且其他都是黑色（没有白色邻居也可以）
                # 更准确的条件：未知邻居数为 1，且黑色邻居数 >= 1
                # 或者：未知邻居数为 1，且总邻居数 - 黑色数 - 未知数 = 0
                if len(unknown_neighbors) == 1:
                    # 所有非未知邻居都必须是黑色
                    total_neighbors = black_count + white_count + len(unknown_neighbors)
                    if black_count + len(unknown_neighbors) == total_neighbors:
                        ur, uc = unknown_neighbors[0]
                        self.set_cell_state(ur, uc, self.WHITE)
                        changed = True

        return changed

    def rule_connectivity_single_unknown(self) -> bool:
        """
        规则 7: 基于连通性的推理
        从任一未访问过的白色格子开始 BFS 扩张：
        - 访问白色邻居时，加入队列继续扩张
        - 访问未知邻居时，记录下来但不继续扩张
        如果白色格子没有完全连通，且访问到的未知格子仅有一个，
        就把这个未知格子标记为白色（它是连接孤立白色区域的关键）

        注意：用一个整数 round 记录访问轮次，visited[r][c] == round 表示
        在当前轮次已访问，避免每次都重新创建二维数组。
        """
        changed = False

        # 初始统计白色格子数量
        white_count = sum(
            1 for r in range(self.size) for c in range(self.size)
            if self.state[r][c] == self.WHITE
        )

        if white_count == 0:
            return False

        # visited[r][c] = k 表示第 k 轮访问过，0 表示未访问
        visited = [[0] * self.size for _ in range(self.size)]
        round_num = 0

        while True:
            round_num += 1  # 新一轮，只需递增轮次
            # 找第一个未访问的白色格子作为起点
            start = None
            for r in range(self.size):
                for c in range(self.size):
                    if self.state[r][c] == self.WHITE and visited[r][c] == 0:
                        start = (r, c)
                        break
                if start:
                    break

            if start is None:
                break

            # BFS 扩张
            queue = deque([start])
            visited[start[0]][start[1]] = round_num
            component_size = 1
            while queue:
                unknown_neighbors = []  # 该连通分量相邻的未知格子

                while queue:
                    r, c = queue.popleft()

                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.size and 0 <= nc < self.size:
                            neighbor_state = self.state[nr][nc]

                            if neighbor_state == self.WHITE:
                                # 白色邻居，加入队列继续扩张
                                if visited[nr][nc] != round_num:
                                    visited[nr][nc] = round_num
                                    component_size += 1
                                    queue.append((nr, nc))
                            elif neighbor_state == self.UNKNOWN:
                                # 未知邻居，记录下来
                                if (nr, nc) not in unknown_neighbors:
                                    unknown_neighbors.append((nr, nc))

                # 检查是否所有白色格子都在这个连通分量中
                if component_size < white_count:
                    # 白色格子不完全连通
                    # 如果只有一个未知邻居可以连接，就标记为白色
                    if len(unknown_neighbors) == 1:
                        ur, uc = unknown_neighbors[0]
                        self.set_cell_state(ur, uc, self.WHITE)
                        changed = True
                        # 标记发生变化，需要从新标记的白色格子重新开始
                        white_count += 1  # 只需加 1，无需重新统计
                        queue.append((ur, uc))
                        visited[ur][uc] = round_num

                else:
                    # 所有白色格子已连通，无需继续
                    break
            if component_size == white_count:
                break
        return changed

    def apply_logical_rules(self) -> int:
        """
        应用动态逻辑推理规则
        动态规则：依赖格子状态变化，需要反复应用
        """
        changed = False
        run_again = True

        while run_again:
            run_again = False
            # 应用新规则 6：白色格子单一未知邻居
            if self.rule_white_single_unknown_neighbor():
                run_again = True
                changed = True
            # 应用新规则 7：基于连通性的单一未知推理
            if self.rule_connectivity_single_unknown():
                run_again = True
                changed = True
            if self.apply_rules_fast():
                run_again = True
                changed = True

        return 1 if changed else 0

    def apply_rules_fast(self) -> bool:
        """
        快速应用规则 4 和规则 5（黑邻居必白，白排除同值）
        使用持续维护的传播队列
        返回是否有变化
        """
        return self.propagate_changes()

    # ========== 检查和验证 ==========

    def check_adjacent_black(self) -> bool:
        """检查是否有两个黑色格子相邻"""
        for r in range(self.size):
            for c in range(self.size):
                if self.state[r][c] != self.BLACK:
                    continue
                if c + 1 < self.size and self.state[r][c + 1] == self.BLACK:
                    return False
                if r + 1 < self.size and self.state[r + 1][c] == self.BLACK:
                    return False
        return True

    def check_duplicate_white(self) -> bool:
        """检查是否有重复的白色数字在同一行/列"""
        # 检查行
        for r in range(self.size):
            seen = {}
            for c in range(self.size):
                if self.state[r][c] == self.WHITE:
                    val = self.grid[r][c]
                    if val in seen:
                        return False
                    seen[val] = c

        # 检查列
        for c in range(self.size):
            seen = {}
            for r in range(self.size):
                if self.state[r][c] == self.WHITE:
                    val = self.grid[r][c]
                    if val in seen:
                        return False
                    seen[val] = r

        return True

    def is_complete(self) -> bool:
        """检查是否所有格子都有确定状态"""
        for r in range(self.size):
            for c in range(self.size):
                if self.state[r][c] == self.UNKNOWN:
                    return False
        return True

    def is_valid(self) -> bool:
        """检查当前状态是否有效"""
        return (
            self.check_adjacent_black() and
            self.check_duplicate_white() and
            self._check_connectivity_uf()
        )

    # ========== 回溯求解 ==========

    def solve(self) -> bool:
        """求解 Hitori 谜题"""
        self.start_time = time.time()

        # 第一阶段：预处理（静态规则，只需运行一次）
        print("预处理：应用静态规则...")
        preprocessed = self.preprocess()
        print(f"  预处理完成{'（有变化）' if preprocessed else '（无变化）'}")

        # 第二阶段：动态规则传播
        print("应用动态规则...")
        rules_applied = self.apply_logical_rules()
        print(f"  应用了 {rules_applied} 次动态规则")

        # 检查是否已经解决
        if self.is_complete() and self.is_valid():
            print("  逻辑推理已完成求解！")
            elapsed = time.time() - self.start_time
            print(f"\n求解时间：{elapsed:.3f} 秒")
            return True

        # 打印推理后的状态
        print("  推理后的状态:")
        self.print_state_summary()
        print("\n  中间状态（网格形式）:")
        self.print_state_details()

        # 如果还有未知格子，使用回溯法
        if not self.is_complete():
            # 收集所有未知格子并打乱顺序
            import random
            unknown_cells = [
                (r, c) for r in range(self.size) for c in range(self.size)
                if self.state[r][c] == self.UNKNOWN
            ]
            random.shuffle(unknown_cells)
            print(f"  开始回溯搜索... ({len(unknown_cells)} 个未知格子)")

            # 保存回溯前的状态
            state_before_backtrack = copy.deepcopy(self.state)

            if self.backtrack_solve(unknown_cells, 0):
                elapsed = time.time() - self.start_time
                print(f"\n求解时间：{elapsed:.3f} 秒")
                return True

            # 回溯失败，打印回溯前的状态
            print("\n  回溯搜索失败，回溯前状态:")
            self.state = state_before_backtrack
            self.print_state_details()
            return False

        return self.is_valid()

    def print_state_summary(self):
        """打印状态摘要"""
        unknown = sum(1 for r in range(self.size) for c in range(self.size) if self.state[r][c] == self.UNKNOWN)
        white = sum(1 for r in range(self.size) for c in range(self.size) if self.state[r][c] == self.WHITE)
        black = sum(1 for r in range(self.size) for c in range(self.size) if self.state[r][c] == self.BLACK)
        print(f"    未知：{unknown}, 白色：{white}, 黑色：{black}")

    def print_state_details(self):
        """打印详细状态（网格形式），未知格子按灰色显示"""
        BLACK_BG = "\033[40m"
        WHITE_BG = "\033[47m"
        GRAY_BG = "\033[100m"
        BLACK_FG = "\033[30m"
        WHITE_FG = "\033[97m"
        RESET = "\033[0m"
        BOLD = "\033[1m"

        # 计算最大数字位数，用于对齐
        max_num = max(max(row) for row in self.grid)
        num_width = len(str(max_num))
        cell_width = max(2, num_width + 2)

        print("\n  回溯前状态（未知格子按灰色显示）:")

        # 列标题
        header = "   " + "".join(f"{BOLD}{c:^{cell_width}}{RESET}" for c in range(self.size))
        print(header)
        print("   " + "─" * (cell_width * self.size))

        for r in range(self.size):
            row_str = f"{BOLD}{r:2}{RESET}│"
            for c in range(self.size):
                num = self.grid[r][c]
                num_str = f"{num:>{num_width}}"
                if self.state[r][c] == self.BLACK:
                    cell = f"{BLACK_BG}{WHITE_FG} {num_str} {RESET}"
                elif self.state[r][c] == self.WHITE:
                    cell = f"{WHITE_BG}{BLACK_FG} {num_str} {RESET}"
                else:
                    # 未知格子按灰色显示
                    cell = f"{GRAY_BG}{WHITE_FG} {num_str} {RESET}"
                row_str += cell
            print(row_str)

        print("   " + "─" * (cell_width * self.size))

    def backtrack_solve(self, unknown_cells: list, idx: int) -> bool:
        """
        回溯法求解剩余的未知格子

        Args:
            unknown_cells: 未知格子列表（已打乱）
            idx: 当前处理到列表中的第几个格子
        """
        if time.time() - self.start_time > self.time_limit:
            return False

        # 跳过已经确定状态的格子
        while idx < len(unknown_cells):
            r, c = unknown_cells[idx]
            if self.state[r][c] != self.UNKNOWN:
                idx += 1
            else:
                break

        # 所有格子都处理完了
        if idx >= len(unknown_cells):
            return self._check_connectivity_uf()

        r, c = unknown_cells[idx]

        # 保存当前状态（使用深拷贝）
        saved_state = copy.deepcopy(self.state)
        saved_queue = deque(self.propagation_queue)

        # 尝试标记为白色
        self.set_cell_state(r, c, self.WHITE)
        self.apply_rules_fast()  # 传播规则

        # 检查是否有相邻黑色或重复白色
        if self.check_adjacent_black() and self.check_duplicate_white():
            if self.backtrack_solve(unknown_cells, idx + 1):
                return True

        # 恢复状态，尝试标记为黑色
        self.state = saved_state
        self.propagation_queue = saved_queue

        self.set_cell_state(r, c, self.BLACK)
        self.apply_rules_fast()  # 传播规则

        # 检查是否有相邻黑色或重复白色
        if self.check_adjacent_black() and self.check_duplicate_white():
            if self.backtrack_solve(unknown_cells, idx + 1):
                return True

        # 恢复状态
        self.state = saved_state
        self.propagation_queue = saved_queue
        return False

    # ========== 输出 ==========

    def print_solution(self, use_color: bool = True):
        """打印解决方案"""
        BLACK_BG = "\033[40m"
        WHITE_BG = "\033[47m"
        BLACK_FG = "\033[30m"
        WHITE_FG = "\033[97m"
        RESET = "\033[0m"
        BOLD = "\033[1m"
        GREEN = "\033[92m"
        RED = "\033[91m"

        print("\n" + "=" * 50)
        print(f"{BOLD}Hitori 求解结果{RESET}")
        print("=" * 50)

        # 计算最大数字位数，用于对齐
        max_num = max(max(row) for row in self.grid)
        num_width = len(str(max_num))
        cell_width = max(2, num_width + 2)

        # 列标题
        header = "   " + "".join(f"{BOLD}{c:^{cell_width}}{RESET}" for c in range(self.size))
        print(header)
        print("   " + "─" * (cell_width * self.size))

        for r in range(self.size):
            row_str = f"{BOLD}{r:2}{RESET}│"
            for c in range(self.size):
                num = self.grid[r][c]
                # 根据数字位数格式化，确保对齐
                num_str = f"{num:>{num_width}}"
                if self.state[r][c] == self.BLACK:
                    if use_color:
                        cell = f"{BLACK_BG}{WHITE_FG} {num_str} {RESET}"
                    else:
                        cell = f"[{num_str}]"
                else:
                    if use_color:
                        cell = f"{WHITE_BG}{BLACK_FG} {num_str} {RESET}"
                    else:
                        cell = f" {num_str} "
                row_str += cell
            print(row_str)

        print("   " + "─" * (cell_width * self.size))

        print(f"\n{BOLD}图例:{RESET}")
        if use_color:
            print(f"  {BLACK_BG}{WHITE_FG} 1 {RESET} = 黑色    {WHITE_BG}{BLACK_FG} 1 {RESET} = 白色")
        else:
            print("  [1] = 黑色    1 = 白色")

        black_count = sum(1 for r in range(self.size) for c in range(self.size) if self.state[r][c] == self.BLACK)
        white_count = sum(1 for r in range(self.size) for c in range(self.size) if self.state[r][c] == self.WHITE)
        print(f"\n{BOLD}统计:{RESET} 黑色 {black_count} | 白色 {white_count} | 总共 {self.size * self.size}")

        print(f"\n{BOLD}验证:{RESET}")
        checks = [
            ("黑色格子不相邻", self.check_adjacent_black()),
            ("每行/列无重复白色数字", self.check_duplicate_white()),
            ("白色格子连通", self._check_connectivity_uf()),
        ]
        for name, result in checks:
            status = f"{GREEN}✓{RESET}" if result else f"{RED}✗{RESET}"
            print(f"  {status} {name}")

        print("=" * 50)

    def get_black_cells(self) -> list[tuple[int, int]]:
        """获取所有黑色格子坐标"""
        return [
            (r, c) for r in range(self.size) for c in range(self.size)
            if self.state[r][c] == self.BLACK
        ]

    def print_simple(self):
        """简单打印"""
        print("\n求解结果:")
        for r in range(self.size):
            row = []
            for c in range(self.size):
                if self.state[r][c] == self.BLACK:
                    row.append(f"[{self.grid[r][c]}]")
                else:
                    row.append(f" {self.grid[r][c]} ")
            print("".join(row))


def solve_example():
    """解决示例谜题"""
    grid = [
        [3, 1, 4, 2, 5],
        [2, 5, 3, 3, 1],
        [4, 3, 2, 5, 4],
        [5, 2, 5, 1, 3],
        [1, 4, 1, 4, 2],
    ]

    solver = HitoriSolver()
    solver.set_grid(grid)

    print("原始网格:")
    for row in grid:
        print(row)

    if solver.solve():
        solver.print_solution()
    else:
        print("未找到解")


if __name__ == "__main__":
    solve_example()
