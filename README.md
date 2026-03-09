# Hitori Puzzle Solver (数壹谜题求解器)

A Python program that solves Hitori (数壹) logic puzzles using logical deduction with backtracking fallback.

## Hitori Rules

Hitori is a logic puzzle where you must:

1. **Black out some cells** so that:
   - No two black cells are adjacent (horizontally or vertically)
   - No number appears more than once in any row or column among white cells
   - All white cells form a single connected region

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for package management.

```bash
# Install dependencies
uv sync
```

## Usage

```bash
# Run with example puzzle
uv run python main.py

# Run with custom puzzle input
uv run python main.py --input

# Run without ANSI colors
uv run python main.py --no-color

# Fetch and solve puzzle from website
uv run python fetch_puzzle.py --solve
```

## Project Structure

```
puzzle_hitorio/
├── main.py              # CLI entry point with user interface
├── hitori_solver.py     # Core solver with logical deduction
├── fetch_puzzle.py      # Web scraper for fetching puzzles
├── CLAUDE.md            # Development guidelines
└── README.md            # This file
```

## Solver Algorithm

The solver uses a two-phase approach:

### Phase 1: Logical Deduction Rules

1. **Sandwich Rule (ABA pattern)**: If two same numbers have one cell between them, the middle must be WHITE
2. **Adjacent Pair Rule**: If one of two adjacent same numbers is WHITE, the other must be BLACK
3. **Black Neighbor Rule**: All neighbors of BLACK cells must be WHITE
4. **White Exclusion Rule**: When a cell is WHITE, same numbers in row/column must be BLACK
5. **Connectivity Rule**: If blackening a cell would isolate white cells, it must be WHITE

### Phase 2: Backtracking Search

- Prioritizes cells that conflict with existing WHITE cells
- Applies logical rules after each assignment for constraint propagation
- Uses time and node limits to prevent infinite search

## Supported Puzzle Sizes

- 5x5
- 10x10
- 15x15
- 20x20 (larger sizes may timeout)

## Puzzle Data Format

The website encodes puzzles as strings where:
- Digits `0-9` represent numbers `1-9`
- Letters `a-z` represent numbers `10-35`
- Example: `"31425"` encodes a 5x5 grid row

## Example Output

```
数壹谜题求解器
==============

输入谜题（直接回车使用示例）: 31425
或直接回车使用示例

正在求解...

原始网格:
   0   1   2   3   4
0 [3] [1] [4] [2] [5]
1 [2] [5] [1] [3] [4]
2 [1] [3] [5] [4] [2]
3 [4] [2] [3] [5] [1]
4 [5] [4] [2] [1] [3]

求解完成！

最终网格:
   0   1   2   3   4
0 [3] [1] [4] [2] [5]
1 [2] [5] [1] [3] [4]
2 [1] [3] [5] [4] [2]
3 [4] [2] [3] [5] [1]
4 [5] [4] [2] [1] [3]

(黑色格子以 ■ 显示)
```

## License

MIT License
