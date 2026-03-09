"""
Hitori Puzzle Solver - 主程序

使用方法:
    uv run python main.py                    # 运行示例谜题
    uv run python main.py --input           # 手动输入谜题
    uv run python main.py --size 10         # 指定大小
    uv run python main.py --fetch           # 从网站获取随机谜题
    uv run python main.py --id 5            # 获取指定编号的谜题
    uv run python main.py --id 5 --size 10  # 获取 10x10 编号 5 的谜题
"""

import sys
import json
from hitori_solver import HitoriSolver


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


def main():
    """主函数"""
    print_banner()

    # 解析命令行参数
    show_color = '--no-color' not in sys.argv
    use_input = '--input' in sys.argv or '-i' in sys.argv
    use_fetch = '--fetch' in sys.argv or '-f' in sys.argv

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

    if use_input:
        # 手动输入模式
        grid = input_grid()
        if grid:
            solve_grid(grid, show_color)
        else:
            print("已取消")
    elif use_fetch or puzzle_id is not None:
        # 从网站获取谜题
        from fetch_puzzle import get_puzzle, get_puzzle_by_id, SIZE_MAP

        diff_short = {'easy': 'e', 'normal': 'n', 'hard': 'h'}
        size_key = f"{size_param}{diff_short.get(difficulty, 'n')}"
        size_code = SIZE_MAP.get(size_key, SIZE_MAP.get(size_param, '1'))

        if puzzle_id is not None:
            # 使用指定编号获取谜题
            print(f"获取 {size_param}x{size_param} {difficulty} 编号 {puzzle_id} 的谜题...")
            grid, grid_size = get_puzzle_by_id(size_code, puzzle_id)
        else:
            # 根据大小和难度获取随机谜题
            print(f"获取 {size_param}x{size_param} {difficulty} 谜题...")
            grid, grid_size = get_puzzle(size_param, difficulty)

        if grid:
            solve_grid(grid, show_color)
        else:
            print("未能获取谜题")
            print("\n可能的原因:")
            print("  1. 网络连接问题")
            print("  2. 网站结构变更")
            print("  3. 编号不存在")
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
        print("      使用 --fetch 或 -f 参数从网站获取谜题")
        print("      使用 --id <编号> 获取指定编号的谜题")
        print("      使用 --no-color 禁用颜色输出")


if __name__ == "__main__":
    main()
