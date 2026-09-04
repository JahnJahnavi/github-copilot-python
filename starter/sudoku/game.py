import random


class GameState:
    def __init__(self):
        self.data = {
            'puzzle': None,
            'solution': None,
            'hints_used': 0,
        }

    @property
    def solution(self):
        return self.data['solution']

    def start(self, puzzle, solution):
        self.data['puzzle'] = puzzle
        self.data['solution'] = solution
        self.data['hints_used'] = 0

    def reset(self):
        self.data.update(puzzle=None, solution=None, hints_used=0)

    def hint(self, board, empty):
        candidates = [
            (row, column)
            for row in range(len(self.puzzle))
            for column in range(len(self.puzzle[row]))
            if self.puzzle[row][column] == empty and board[row][column] == empty
        ]
        if not candidates:
            return None

        row, column = random.choice(candidates)
        self.data['hints_used'] += 1
        return row, column, self.solution[row][column]

    def is_complete(self, board, size):
        return all(
            board[row][column] == self.solution[row][column]
            for row in range(size)
            for column in range(size)
        )

    @property
    def puzzle(self):
        return self.data['puzzle']

    @property
    def hints_used(self):
        return self.data['hints_used']

    def incorrect_cells(self, board, size):
        incorrect = []
        for row in range(size):
            for column in range(size):
                if board[row][column] != self.solution[row][column]:
                    incorrect.append([row, column])
        return incorrect
