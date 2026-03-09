"""
Hitori Puzzle Solver - 主程序

使用方法:
    uv run python main.py                    # 运行示例谜题
    uv run python main.py --input           # 手动输入谜题
    uv run python main.py --fetch           # 从网站获取随机谜题
    uv run python main.py --id 5            # 获取指定编号的谜题
    uv run python main.py --daily           # 获取每日谜题
    uv run python main.py --weekly          # 获取每周谜题
    uv run python main.py --monthly         # 获取每月谜题
    uv run python main.py --id 5 --size 10  # 获取 10x10 编号 5 的谜题
"""

import sys
import json
import requests
import re
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


def print_banner():
    """打印欢迎横幅"""
    print("""
╔════════════════════════════════════════════════╗
║           Hitori Puzzle Solver                 ║
║           数壹谜题求解器                       ║
╚════════════════════════════════════════════════╝
""")


def input_grid() -> list[list[int]]:
    """
    从用户输入获取谜题网格
    支持多种输入格式：
    1. 每行输入数字，用空格或逗号分隔
    2. 输入 JSON 格式
    3. 输入连续数字字符串
    """
    print("请输入谜题网格（支持 5x5, 10x10, 15x15, 20x20）")
    print("输入格式示例:")
    print("  3 1 4 2 5")
    print("  2 5 3 3 1")
    print("  ...")
    print("\n或者输入 JSON: [[3,1,4,2,5],[2,5,3,3,1],...]")
    print("输入 'q' 退出\n")

    grid = []
    line_count = 0

    while True:
        try:
            line = input(f"行 {line_count + 1}: ").strip()

            if line.lower() == 'q':
                return []

            # 尝试 JSON 格式
            if line.startswith('['):
                try:
                    # 可能是完整的 JSON 数组
                    full_json = line
                    while not full_json.count(']') == full_json.count('['):
                        full_json += input()
                    data = json.loads(full_json)
                    if isinstance(data, list) and all(isinstance(row, list) for row in data):
                        return data
                except json.JSONDecodeError:
                    print("JSON 格式错误，请重试")
                    continue

            # 解析普通行输入
            if ',' in line:
                # 逗号分隔
                numbers = [int(x.strip()) for x in line.split(',') if x.strip()]
            else:
                # 空格分隔或连续数字
                parts = line.split()
                if len(parts) == 1 and len(line) > 1 and line.isdigit():
                    # 连续数字
                    numbers = [int(c) for c in line]
                else:
                    numbers = [int(x) for x in parts if x.isdigit()]

            if numbers:
                if line_count == 0:
                    expected_size = len(numbers)

                if len(numbers) != expected_size:
                    print(f"  错误：此行有 {len(numbers)} 个数字，期望 {expected_size} 个")
                    continue

                grid.append(numbers)
                line_count += 1

                # 检查是否完成
                if line_count == expected_size:
                    print(f"\n已输入 {expected_size}x{expected_size} 网格")
                    break

        except ValueError as e:
            print(f"输入错误：{e}")
        except KeyboardInterrupt:
            return []

    return grid


def solve_grid(grid: list[list[int]], show_color: bool = True):
    """解决并显示谜题"""
    if not grid or not grid[0]:
        print("无效的网格")
        return False

    size = len(grid)
    print(f"\n解决 {size}x{size} 谜题...")

    solver = HitoriSolver()
    solver.set_grid(grid)

    print("\n原始网格:")
    solver.print_simple()

    if solver.solve():
        solver.print_solution(use_color=show_color)
        return True
    else:
        print("\n❌ 未找到解决方案")
        print("可能的原因:")
        print("  1. 谜题本身无解")
        print("  2. 输入的数据有误")
        print("  3. 数字不符合 Hitori 规则")
        return False


def fetch_puzzle_data(url: str) -> tuple[str | None, str | None]:
    """
    从网站获取谜题数据字符串和题号

    Returns:
        (谜题数据字符串，题号)，失败返回 (None, None)
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
        task_match = re.search(r"var\s+task\s*=\s*'([^']+)'", html)
        task_data = task_match.group(1) if task_match else None

        # 查找 puzzleID 题号
        puzzle_id = None
        id_match = re.search(r'id="puzzleID"\s*>\s*([0-9,]+)', html)
        if id_match:
            puzzle_id = id_match.group(1)
        else:
            # 尝试查找特殊谜题的日期格式 (如 "Mar 09, 2026")
            date_match = re.search(r'<option[^>]+selected="selected"[^>]*>\s*([A-Za-z]+\s+\d+,\s*\d+)\s*</option>', html)
            if date_match:
                puzzle_id = date_match.group(1).strip()

        return task_data, puzzle_id

    except Exception as e:
        print(f"获取谜题时出错：{e}")
        return None, None


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


def get_puzzle_by_size(size_param: str) -> tuple[list[list[int]] | None, int, str | None]:
    """
    根据 size 参数获取谜题

    Args:
        size_param: 尺寸参数，如 '12' (每日), '13' (每周), '14' (每月), 或 '1'-'11' (普通谜题)

    Returns:
        (网格，大小，题号) 或 (None, 0, None)
    """
    url = f"https://cn.puzzle-hitori.com/?size={size_param}"

    task_data, puzzle_id = fetch_puzzle_data(url)

    if task_data:
        grid_size = int(len(task_data) ** 0.5)
        if puzzle_id:
            print(f"获取到谜题 ({grid_size}x{grid_size}, 题号：{puzzle_id})")
        else:
            print(f"获取到谜题 ({grid_size}x{grid_size})")
        grid = parse_task_string(task_data, grid_size)
        return grid, grid_size, puzzle_id

    return None, 0, None


def get_daily_puzzle() -> tuple[list[list[int]] | None, int, str | None]:
    """获取每日谜题"""
    return get_puzzle_by_size('12')


def get_weekly_puzzle() -> tuple[list[list[int]] | None, int, str | None]:
    """获取每周谜题"""
    return get_puzzle_by_size('13')


def get_monthly_puzzle() -> tuple[list[list[int]] | None, int, str | None]:
    """获取每月谜题"""
    return get_puzzle_by_size('14')


def get_puzzle(size: str = "5", difficulty: str = "easy") -> tuple[list[list[int]] | None, int, str | None]:
    """
    获取指定大小和难度的谜题

    Args:
        size: 谜题大小 "5", "10", "15", "20"
        difficulty: 难度 "easy", "normal", "hard"

    Returns:
        (网格，大小，题号) 或 (None, 0, None)
    """
    diff_short = {'easy': 'e', 'normal': 'n', 'hard': 'h'}
    size_key = f"{size}{diff_short.get(difficulty, 'n')}"
    size_param = SIZE_MAP.get(size_key, SIZE_MAP.get(size, '1'))

    return get_puzzle_by_size(size_param)


def get_puzzle_by_id(size_param: str, puzzle_id: int) -> tuple[list[list[int]] | None, int, str | None]:
    """
    根据大小和编号获取指定谜题

    Args:
        size_param: 尺寸参数，如 '0' (5x5 简单), '1' (5x5 普通), etc.
        puzzle_id: 谜题编号

    Returns:
        (网格，大小，题号) 或 (None, 0, None)
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # POST 到主页获取指定谜题
    post_data = f"specific=1&size={size_param}&specid={puzzle_id}"

    try:
        response = requests.post(
            "https://cn.puzzle-hitori.com/",
            headers=headers,
            data=post_data,
            timeout=30
        )
        response.raise_for_status()
        html = response.text

        # 查找 var task = '...'
        task_match = re.search(r"var\s+task\s*=\s*'([^']+)'", html)
        if task_match:
            task_data = task_match.group(1)
            grid_size = int(len(task_data) ** 0.5)

            # 查找 puzzleID 题号
            puzzle_id_match = re.search(r'id="puzzleID"\s*>\s*([0-9,]+)', html)
            displayed_id = puzzle_id_match.group(1) if puzzle_id_match else str(puzzle_id)

            print(f"获取到谜题 (大小：{grid_size}x{grid_size}, 题号：{displayed_id})")
            grid = parse_task_string(task_data, grid_size)
            return grid, grid_size, displayed_id

        return None, 0, None

    except Exception as e:
        print(f"获取谜题时出错：{e}")
        return None, 0, None


def main():
    """主函数"""
    print_banner()

    # 解析命令行参数
    show_color = '--no-color' not in sys.argv
    use_input = '--input' in sys.argv or '-i' in sys.argv
    use_fetch = '--fetch' in sys.argv or '-f' in sys.argv

    # 特殊获取模式
    use_daily = '--daily' in sys.argv or '-d' in sys.argv
    use_weekly = '--weekly' in sys.argv or '-w' in sys.argv
    use_monthly = '--monthly' in sys.argv or '-m' in sys.argv

    # 解析 --id 参数（指定谜题编号）
    puzzle_id = None
    size_param = '5'
    difficulty = 'easy'

    for i, arg in enumerate(sys.argv[1:], 1):
        if arg in ('--id', '-id') and i < len(sys.argv) - 1:
            try:
                puzzle_id = int(sys.argv[i + 1])
            except ValueError:
                pass
        elif arg in ('--size', '-size') and i < len(sys.argv) - 1:
            size_param = sys.argv[i + 1]
        elif arg in ('--diff', '-diff') and i < len(sys.argv) - 1:
            difficulty = sys.argv[i + 1]

    # 特殊模式优先
    if use_daily:
        print("获取每日谜题...")
        grid, grid_size, puzzle_id_str = get_daily_puzzle()
        if grid:
            solve_grid(grid, show_color)
        else:
            print("未能获取每日谜题")
    elif use_weekly:
        print("获取每周谜题...")
        grid, grid_size, puzzle_id_str = get_weekly_puzzle()
        if grid:
            solve_grid(grid, show_color)
        else:
            print("未能获取每周谜题")
    elif use_monthly:
        print("获取每月谜题...")
        grid, grid_size, puzzle_id_str = get_monthly_puzzle()
        if grid:
            solve_grid(grid, show_color)
        else:
            print("未能获取每月谜题")
    elif use_fetch or puzzle_id is not None:
        # 从网站获取谜题
        diff_short = {'easy': 'e', 'normal': 'n', 'hard': 'h'}
        size_key = f"{size_param}{diff_short.get(difficulty, 'n')}"
        size_code = SIZE_MAP.get(size_key, SIZE_MAP.get(size_param, '1'))

        if puzzle_id is not None:
            print(f"获取 {size_param}x{size_param} {difficulty} 编号 {puzzle_id} 的谜题...")
        else:
            print(f"获取 {size_param}x{size_param} {difficulty} 谜题...")

        grid, grid_size, puzzle_id_str = get_puzzle_by_id(size_code, puzzle_id) if puzzle_id is not None else get_puzzle(size_param, difficulty)

        if grid:
            solve_grid(grid, show_color)
        else:
            print("未能获取谜题")
            print("\n可能的原因:")
            print("  1. 网络连接问题")
            print("  2. 网站结构变更")
            print("  3. 编号不存在")
    elif use_input:
        # 手动输入模式
        grid = input_grid()
        if grid:
            solve_grid(grid, show_color)
        else:
            print("已取消")
    else:
        # 示例模式
        example_grids = {
            '5': [
                [3, 1, 4, 2, 5],
                [2, 5, 3, 3, 1],
                [4, 3, 2, 5, 4],
                [5, 2, 5, 1, 3],
                [1, 4, 1, 4, 2],
            ],
            '10': [
                [8, 10, 7, 1, 1, 8, 10, 7, 2, 4],
                [2, 9, 10, 7, 6, 3, 4, 6, 8, 4],
                [7, 5, 1, 1, 10, 3, 2, 8, 7, 3],
                [7, 4, 10, 6, 8, 5, 6, 10, 4, 2],
                [6, 6, 3, 8, 9, 7, 8, 7, 10, 5],
                [6, 2, 1, 8, 4, 1, 8, 3, 2, 10],
                [8, 6, 4, 10, 2, 2, 10, 6, 3, 3],
                [5, 3, 8, 9, 7, 4, 1, 1, 5, 6],
                [4, 9, 7, 10, 2, 2, 1, 1, 6, 9],
                [5, 7, 2, 6, 1, 10, 6, 10, 4, 5],
            ],
            '20': [
                [20, 8, 14, 8, 12, 18, 8, 19, 6, 6, 17, 15, 1, 16, 16, 15, 4, 15, 7, 15],
                [5, 19, 13, 18, 3, 12, 16, 17, 13, 15, 13, 9, 5, 10, 2, 11, 13, 4, 5, 12],
                [19, 15, 5, 4, 3, 17, 20, 2, 12, 15, 1, 2, 3, 18, 13, 3, 9, 11, 11, 10],
                [9, 4, 9, 17, 8, 12, 9, 16, 9, 19, 9, 3, 13, 9, 3, 6, 3, 18, 14, 3],
                [1, 13, 12, 2, 16, 2, 10, 3, 7, 13, 5, 18, 2, 14, 6, 3, 15, 3, 9, 4],
                [2, 11, 4, 5, 2, 15, 17, 20, 4, 10, 9, 3, 18, 2, 19, 9, 17, 2, 1, 4],
                [16, 17, 3, 7, 10, 16, 9, 2, 5, 16, 11, 13, 15, 20, 3, 8, 3, 12, 7, 19],
                [13, 14, 19, 14, 17, 16, 7, 14, 9, 18, 4, 14, 11, 14, 15, 14, 1, 14, 12, 14],
                [4, 3, 8, 20, 2, 19, 4, 10, 19, 13, 16, 12, 8, 1, 8, 7, 19, 17, 18, 6],
                [9, 5, 17, 5, 18, 7, 2, 20, 8, 4, 20, 14, 6, 19, 20, 13, 20, 1, 10, 20],
                [15, 14, 15, 16, 15, 10, 17, 5, 19, 17, 13, 7, 12, 17, 1, 15, 18, 6, 15, 11],
                [10, 8, 7, 20, 19, 20, 18, 8, 17, 1, 2, 8, 9, 4, 8, 12, 8, 15, 11, 20],
                [17, 18, 13, 19, 4, 9, 19, 7, 16, 3, 8, 10, 13, 3, 11, 15, 5, 17, 6, 15],
                [5, 7, 5, 13, 5, 11, 14, 1, 5, 2, 19, 5, 16, 12, 5, 18, 20, 9, 5, 3],
                [6, 10, 20, 10, 7, 19, 5, 18, 14, 9, 10, 17, 19, 11, 16, 1, 18, 8, 13, 10],
                [17, 12, 6, 10, 17, 5, 17, 9, 7, 3, 18, 7, 2, 17, 4, 17, 16, 7, 17, 13],
                [3, 16, 9, 6, 1, 14, 11, 14, 18, 9, 10, 4, 9, 13, 3, 20, 9, 19, 15, 9],
                [2, 5, 8, 5, 9, 4, 5, 11, 5, 16, 14, 5, 17, 5, 12, 5, 13, 5, 3, 18],
                [18, 9, 10, 11, 17, 13, 6, 10, 3, 17, 14, 8, 14, 15, 14, 4, 10, 16, 19, 14],
                [12, 20, 18, 6, 11, 6, 3, 4, 16, 20, 15, 16, 10, 5, 14, 16, 7, 13, 8, 17],
            ],
        }

        size = '5'
        for arg in sys.argv[1:]:
            if arg.isdigit() and arg in example_grids:
                size = arg
                break

        print(f"使用 {size}x{size} 示例谜题")
        print("=" * 50)

        grid = example_grids[size]
        solve_grid(grid, show_color)

        print("\n" + "=" * 50)
        print("提示：使用 --input 或 -i 参数输入自己的谜题")
        print("      使用 --daily/-d、--weekly/-w、--monthly/-m 获取特殊谜题")
        print("      使用 --id <编号> 获取指定编号的谜题")
        print("      使用 --no-color 禁用颜色输出")


if __name__ == "__main__":
    main()
