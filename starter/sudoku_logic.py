"""Backward-compatible imports for the Sudoku logic module."""

from sudoku.logic import (
    EMPTY,
    SIZE,
    create_empty_board,
    count_solutions,
    deep_copy,
    fill_board,
    generate_puzzle,
    is_safe,
    remove_cells,
    solve_board,
)

__all__ = [
    'EMPTY',
    'SIZE',
    'create_empty_board',
    'count_solutions',
    'deep_copy',
    'fill_board',
    'generate_puzzle',
    'is_safe',
    'remove_cells',
    'solve_board',
]
