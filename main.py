"""
Hitori Puzzle Solver - 主程序

使用方法:
    uv run python main.py                    # 运行示例谜题
    uv run python main.py --input           # 手动输入谜题
    uv run python main.py --size 10         # 指定大小
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

    # 示例谜题（来自 puzzle-hitori.com）
    example_grids = {
        '5': [
            [3, 1, 4, 2, 5],
            [2, 5, 3, 3, 1],
            [4, 3, 2, 5, 4],
            [5, 2, 5, 1, 3],
            [1, 4, 1, 4, 2],
        ],
        '10': [
            [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
            [2, 3, 4, 5, 1, 2, 3, 4, 5, 1],
            [3, 4, 5, 1, 2, 3, 4, 5, 1, 2],
            [4, 5, 1, 2, 3, 4, 5, 1, 2, 3],
            [5, 1, 2, 3, 4, 5, 1, 2, 3, 4],
            [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
            [2, 3, 4, 5, 1, 2, 3, 4, 5, 1],
            [3, 4, 5, 1, 2, 3, 4, 5, 1, 2],
            [4, 5, 1, 2, 3, 4, 5, 1, 2, 3],
            [5, 1, 2, 3, 4, 5, 1, 2, 3, 4],
        ],
    }

    if use_input:
        # 手动输入模式
        grid = input_grid()
        if grid:
            solve_grid(grid, show_color)
        else:
            print("已取消")
    else:
        # 示例模式
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
        print("      使用 --no-color 禁用颜色输出")


if __name__ == "__main__":
    main()
