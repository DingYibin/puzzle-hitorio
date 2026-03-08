"""
从 puzzle-hitori.com 获取谜题

网站 URL 参数说明:
- size=0: 5x5 简单 (主页)
- size=1: 5x5 普通
- size=2: 5x5 困难
- size=3: 10x10 简单
- size=4: 10x10 普通
- size=5: 10x10 困难
- size=6: 15x15 简单
- size=7: 15x15 普通
- size=8: 15x15 困难
- size=9: 20x20 简单
- size=10: 20x20 普通
- size=11: 20x20 困难
- size=12: 每日谜题
- size=13: 每周谜题
- size=14: 每月谜题

使用方法:
    uv run python fetch_puzzle.py              # 获取 5x5 普通
    uv run python fetch_puzzle.py --size 5     # 获取 5x5 普通
    uv run python fetch_puzzle.py --size 5 --diff easy   # 获取 5x5 简单
    uv run python fetch_puzzle.py --size 10    # 获取 10x10 普通
    uv run python fetch_puzzle.py --daily      # 获取每日谜题
    uv run python fetch_puzzle.py --weekly     # 获取每周谜题
    uv run python fetch_puzzle.py --monthly    # 获取每月谜题
    uv run python fetch_puzzle.py --solve      # 获取并求解
    uv run python fetch_puzzle.py --size 10 --solve  # 获取 10x10 并求解
    uv run python fetch_puzzle.py --solve --time 60  # 设置 60 秒时间限制
"""

import requests
import re
import sys

from hitori_solver import HitoriSolver


# URL 参数映射
SIZE_MAP = {
    '5': '1',       # 5x5 普通 (默认)
    '5e': '0',      # 5x5 简单 (主页)
    '5n': '1',      # 5x5 普通
    '5h': '2',      # 5x5 困难
    '10': '4',      # 10x10 普通 (默认)
    '10e': '3',     # 10x10 简单
    '10n': '4',     # 10x10 普通
    '10h': '5',     # 10x10 困难
    '15': '7',      # 15x15 普通 (默认)
    '15e': '6',     # 15x15 简单
    '15n': '7',     # 15x15 普通
    '15h': '8',     # 15x15 困难
    '20': '10',     # 20x20 普通 (默认)
    '20e': '9',     # 20x20 简单
    '20n': '10',    # 20x20 普通
    '20h': '11',    # 20x20 困难
    'daily': '12',   # 每日谜题
    'weekly': '13',  # 每周谜题
    'monthly': '14', # 每月谜题
}


def fetch_puzzle_data(url: str) -> str | None:
    """
    从网站获取谜题数据字符串

    Returns:
        谜题数据字符串（如 '4515451443254454253154453'），失败返回 None
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        html = response.text

        # 查找 var task = '...'
        match = re.search(r"var\s+task\s*=\s*'([^']+)'", html)
        if match:
            return match.group(1)

        return None

    except Exception as e:
        print(f"获取谜题时出错：{e}")
        return None


def parse_task_string(task: str, size: int) -> list[list[int]]:
    """
    解析任务字符串为二维网格

    Args:
        task: 谜题字符串（如 '4515451443254454253154453'，其中 'a'=10, 'b'=11, etc.）
        size: 网格大小

    Returns:
        二维列表表示的谜题网格
    """
    grid = []

    for r in range(size):
        row = []
        for c in range(size):
            idx = r * size + c
            if idx < len(task):
                char = task[idx]
                if char.isdigit():
                    row.append(int(char))
                elif char.islower():
                    # 'a' = 10, 'b' = 11, etc.
                    row.append(ord(char) - ord('a') + 10)
                else:
                    row.append(0)
            else:
                row.append(0)
        grid.append(row)

    return grid


def get_puzzle_by_size(size_param: str) -> tuple[list[list[int]] | None, int]:
    """
    根据 size 参数获取谜题

    Args:
        size_param: 尺寸参数，如 '12' (每日), '13' (每周), '14' (每月), 或 '1'-'11' (普通谜题)

    Returns:
        (网格，大小) 或 (None, 0)
    """
    url = f"https://cn.puzzle-hitori.com/?size={size_param}"

    task_data = fetch_puzzle_data(url)

    if task_data:
        grid_size = int(len(task_data) ** 0.5)
        print(f"获取到谜题 ({grid_size}x{grid_size})")
        grid = parse_task_string(task_data, grid_size)
        return grid, grid_size

    return None, 0


def get_daily_puzzle() -> tuple[list[list[int]] | None, int]:
    """获取每日谜题"""
    return get_puzzle_by_size('12')


def get_weekly_puzzle() -> tuple[list[list[int]] | None, int]:
    """获取每周谜题"""
    return get_puzzle_by_size('13')


def get_monthly_puzzle() -> tuple[list[list[int]] | None, int]:
    """获取每月谜题"""
    return get_puzzle_by_size('14')


def get_puzzle(size: str = "5", difficulty: str = "easy") -> tuple[list[list[int]] | None, int]:
    """
    获取指定大小和难度的谜题

    Args:
        size: 谜题大小 "5", "10", "15", "20"
        difficulty: 难度 "easy", "normal", "hard"

    Returns:
        (网格，大小) 或 (None, 0)
    """
    # 构建尺寸键
    diff_short = {'easy': 'e', 'normal': 'n', 'hard': 'h'}
    diff_map = {'e': 'e', 'n': 'n', 'h': 'h'}

    # 尝试不同的 URL 格式
    size_key = f"{size}{diff_short.get(difficulty, 'n')}"
    size_param = SIZE_MAP.get(size_key, SIZE_MAP.get(size, '1'))

    return get_puzzle_by_size(size_param)


def main():
    """主函数"""
    print("=" * 50)
    print("Hitori 谜题下载器")
    print("=" * 50)

    should_solve = '--solve' in sys.argv or '-s' in sys.argv

    # 解析参数
    size = None
    difficulty = "easy"

    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == '--size' and i < len(sys.argv) - 1:
            size = sys.argv[i + 1]
        elif arg == '--diff' and i < len(sys.argv) - 1:
            difficulty = sys.argv[i + 1]

    if '--daily' in sys.argv or '-d' in sys.argv:
        print("获取每日谜题...")
        grid, grid_size = get_daily_puzzle()
    elif '--weekly' in sys.argv or '-w' in sys.argv:
        print("获取每周谜题...")
        grid, grid_size = get_weekly_puzzle()
    elif '--monthly' in sys.argv or '-m' in sys.argv:
        print("获取每月谜题...")
        grid, grid_size = get_monthly_puzzle()
    elif size:
        print(f"获取 {size}x{size} {difficulty} 谜题...")
        grid, grid_size = get_puzzle(size, difficulty)
    else:
        # 默认获取 5x5 简单
        print("获取 5x5 简单谜题...")
        grid, grid_size = get_puzzle("5", "easy")

    if grid:
        print(f"\n获取到的谜题 ({grid_size}x{grid_size}):")
        for row in grid:
            print(row)

        if should_solve:
            print("\n" + "=" * 50)
            print("开始求解...")
            print("=" * 50)

            # 解析 --time 参数
            time_limit = 5.0
            for i, arg in enumerate(sys.argv):
                if arg == '--time' and i + 1 < len(sys.argv):
                    try:
                        time_limit = float(sys.argv[i + 1])
                    except ValueError:
                        pass
                    break

            solver = HitoriSolver(time_limit=time_limit)
            solver.set_grid(grid)

            if solver.solve():
                solver.print_solution()
            else:
                print("未找到解")
                print(f"提示：增大网格会增加求解时间")
    else:
        print("未能获取谜题")
        print("\n可能的原因:")
        print("  1. 网络连接问题")
        print("  2. 网站结构变更")


if __name__ == "__main__":
    main()
