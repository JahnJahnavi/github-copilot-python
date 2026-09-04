import copy
import random

SIZE = 9
EMPTY = 0


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False

    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def solve_board(board):
    solved = deep_copy(board)
    return solved if fill_board(solved) else None


def _is_valid_complete_board(board):
    expected_values = set(range(1, SIZE + 1))
    return (
        all(set(row) == expected_values for row in board)
        and all(
            {board[row][column] for row in range(SIZE)} == expected_values
            for column in range(SIZE)
        )
        and all(
            {
                board[row][column]
                for row in range(box_row, box_row + 3)
                for column in range(box_column, box_column + 3)
            }
            == expected_values
            for box_row in range(0, SIZE, 3)
            for box_column in range(0, SIZE, 3)
        )
    )


def count_solutions(board, limit=2):
    board = deep_copy(board)
    solutions = 0

    def search():
        nonlocal solutions
        if solutions >= limit:
            return

        for row in range(SIZE):
            for col in range(SIZE):
                if board[row][col] == EMPTY:
                    for candidate in range(1, SIZE + 1):
                        if is_safe(board, row, col, candidate):
                            board[row][col] = candidate
                            search()
                            board[row][col] = EMPTY
                            if solutions >= limit:
                                return
                    return

        if _is_valid_complete_board(board):
            solutions += 1

    search()
    return solutions


def remove_cells(board, clues):
    cells = [
        (row, col)
        for row in range(SIZE)
        for col in range(SIZE)
        if board[row][col] != EMPTY
    ]
    random.shuffle(cells)

    for row, col in cells:
        if sum(cell != EMPTY for current_row in board for cell in current_row) <= clues:
            break
        value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board) != 1:
            board[row][col] = value


def generate_puzzle(clues=35):
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
