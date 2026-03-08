# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hitori Puzzle Solver - A Python program that solves Hitori (数壹) logic puzzles using logical deduction with backtracking fallback.

**Hitori Rules:**
1. Black out some cells so that:
   - No two black cells are adjacent (horizontally or vertically)
   - No number appears more than once in any row or column among white cells
   - All white cells form a single connected region

## Commands

```bash
# Run with example puzzle
uv run python main.py

# Run with custom puzzle input
uv run python main.py --input

# Run without ANSI colors
uv run python main.py --no-color

# Run the solver module directly
uv run python hitori_solver.py

# Fetch and solve puzzle from website
uv run python fetch_puzzle.py --solve

# Add new dependencies
uv add <package>
```

## Architecture

- `main.py` - CLI entry point with user interface
- `hitori_solver.py` - Core solver with:
  - Three-state cell system: UNKNOWN, WHITE, BLACK
  - Logical deduction rules for constraint propagation
  - Backtracking search for remaining unknowns
- `fetch_puzzle.py` - Web scraping utility using requests (no browser needed)

## Solver Algorithm

The solver uses a two-phase approach:

### Phase 1: Logical Deduction Rules
1. **Sandwich Rule (ABA pattern)**: If two same numbers have one cell between them, the middle must be WHITE
2. **Corner Rule (L-shape)**: Three same numbers in L-shape, the corner must be WHITE
3. **Adjacent Pair Rule**: If one of two adjacent same numbers is WHITE, the other must be BLACK
4. **Black Neighbor Rule**: All neighbors of BLACK cells must be WHITE
5. **White Exclusion Rule**: When a cell is WHITE, same numbers in row/column must be BLACK
6. **Connectivity Rule**: If blackening a cell would isolate white cells, it must be WHITE

### Phase 2: Backtracking Search
- Prioritizes cells that conflict with existing WHITE cells
- Applies logical rules after each assignment for constraint propagation
- Uses time and node limits to prevent infinite search

## Puzzle Data Format

Website encodes puzzles as strings where:
- Digits 0-9 represent numbers 1-9
- Letters 'a'-'z' represent numbers 10-35
- Example: "31425" encodes a 5x5 grid row

## Supported Sizes

5x5, 10x10, 15x15, 20x20 (larger sizes may timeout)
