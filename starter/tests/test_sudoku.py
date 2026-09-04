import pytest

import app
import sudoku_logic


@pytest.fixture
def client():
    app.app.config.update(TESTING=True)
    app.CURRENT.update(puzzle=None, solution=None)
    with app.app.test_client() as test_client:
        yield test_client
    app.CURRENT.update(puzzle=None, solution=None)


def assert_valid_solution(board):
    expected_values = set(range(1, sudoku_logic.SIZE + 1))

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(set(row) == expected_values for row in board)
    assert all(
        {board[row][column] for row in range(sudoku_logic.SIZE)}
        == expected_values
        for column in range(sudoku_logic.SIZE)
    )


def test_generate_puzzle_returns_valid_grid_and_solution():
    puzzle, solution = sudoku_logic.generate_puzzle()

    assert_valid_solution(solution)
    assert sudoku_logic.count_solutions(puzzle) == 1
    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(
        puzzle[row][column] in range(sudoku_logic.SIZE + 1)
        for row in range(sudoku_logic.SIZE)
        for column in range(sudoku_logic.SIZE)
    )
    assert all(
        puzzle[row][column] in (0, solution[row][column])
        for row in range(sudoku_logic.SIZE)
        for column in range(sudoku_logic.SIZE)
    )


def test_generate_puzzle_respects_requested_clue_count():
    clues = 40

    puzzle, _ = sudoku_logic.generate_puzzle(clues)

    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == clues


@pytest.mark.parametrize(
    ('difficulty', 'expected_clues'),
    [('easy', 40), ('medium', 32), ('hard', 26)],
)
def test_new_route_maps_difficulty_to_clue_count(client, monkeypatch, difficulty, expected_clues):
    requested_clues = []
    board = sudoku_logic.create_empty_board()

    def generate_puzzle(clues):
        requested_clues.append(clues)
        return board, board

    monkeypatch.setattr(sudoku_logic, 'generate_puzzle', generate_puzzle)

    response = client.get(f'/new?difficulty={difficulty}')

    assert response.status_code == 200
    assert requested_clues == [expected_clues]


def test_new_route_rejects_unknown_difficulty(client, monkeypatch):
    monkeypatch.setattr(
        sudoku_logic,
        'generate_puzzle',
        lambda clues: pytest.fail('generator should not be called'),
    )

    response = client.get('/new?difficulty=expert')

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Invalid difficulty'}


def test_new_route_exposes_only_the_puzzle(client, monkeypatch):
    puzzle = sudoku_logic.create_empty_board()
    solution = sudoku_logic.create_empty_board()
    monkeypatch.setattr(sudoku_logic, 'generate_puzzle', lambda clues: (puzzle, solution))

    response = client.get('/new?difficulty=easy')

    assert response.get_json() == {'puzzle': puzzle}
    assert 'solution' not in response.get_json()


def test_hint_route_returns_one_empty_cell_and_tracks_usage(client, monkeypatch):
    puzzle = sudoku_logic.create_empty_board()
    solution = [[1] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE)]
    solution[0] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    monkeypatch.setattr(sudoku_logic, 'generate_puzzle', lambda clues: (puzzle, solution))
    client.get('/new')

    response = client.post('/hint', json={'board': puzzle})
    data = response.get_json()

    assert response.status_code == 200
    assert data['row'] in range(sudoku_logic.SIZE)
    assert data['col'] in range(sudoku_logic.SIZE)
    assert data['value'] == solution[data['row']][data['col']]
    assert data['hints_used'] == 1
    assert set(data) == {'row', 'col', 'value', 'hints_used'}


def test_hint_route_does_not_repeat_a_filled_cell(client, monkeypatch):
    puzzle = sudoku_logic.create_empty_board()
    solution = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ]
    monkeypatch.setattr(sudoku_logic, 'generate_puzzle', lambda clues: (puzzle, solution))
    client.get('/new')

    first = client.post('/hint', json={'board': puzzle}).get_json()
    board = sudoku_logic.create_empty_board()
    board[first['row']][first['col']] = first['value']
    second = client.post('/hint', json={'board': board}).get_json()

    assert second['hints_used'] == 2
    assert (second['row'], second['col']) != (first['row'], first['col'])


def test_hint_route_reports_complete_puzzle(client, monkeypatch):
    board = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ]
    monkeypatch.setattr(sudoku_logic, 'generate_puzzle', lambda clues: (board, board))
    client.get('/new')

    response = client.post('/hint', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'complete': True, 'hints_used': 0}


def test_hint_route_does_not_mark_incorrect_full_board_complete(client, monkeypatch):
    solution = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ]
    puzzle = [row[:] for row in solution]
    puzzle[0][0], puzzle[0][1] = puzzle[0][1], puzzle[0][0]
    monkeypatch.setattr(sudoku_logic, 'generate_puzzle', lambda clues: (puzzle, solution))
    client.get('/new')

    response = client.post('/hint', json={'board': puzzle})

    assert response.status_code == 200
    assert response.get_json() == {
        'complete': False,
        'no_empty': True,
        'hints_used': 0,
    }


def test_hint_route_requires_a_game_in_progress(client):
    response = client.post('/hint', json={'board': sudoku_logic.create_empty_board()})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_solve_route_returns_solution_without_starting_a_game(client, monkeypatch):
    solution = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ]
    puzzle = [row[:] for row in solution]
    puzzle[0][0] = sudoku_logic.EMPTY
    monkeypatch.setattr(sudoku_logic, 'generate_puzzle', lambda clues: (puzzle, solution))
    client.get('/new')

    response = client.post('/solve')

    assert response.status_code == 200
    assert response.get_json() == {'solution': solution}


def test_solve_route_requires_a_game_in_progress(client):
    response = client.post('/solve')

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_count_solutions_stops_after_finding_two_solutions():
    assert sudoku_logic.count_solutions(sudoku_logic.create_empty_board()) == 2


def test_count_solutions_returns_one_for_a_solved_board():
    board = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ]

    assert sudoku_logic.count_solutions(board) == 1


def test_count_solutions_rejects_an_invalid_completed_board():
    board = [[1] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE)]

    assert sudoku_logic.count_solutions(board) == 0


def test_check_route_accepts_the_generated_solution(client, monkeypatch):
    puzzle = sudoku_logic.create_empty_board()
    solution = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ]
    monkeypatch.setattr(sudoku_logic, 'generate_puzzle', lambda clues: (puzzle, solution))

    new_game_response = client.get('/new?clues=0')
    check_response = client.post('/check', json={'board': solution})

    assert new_game_response.status_code == 200
    assert check_response.status_code == 200
    assert check_response.get_json() == {'incorrect': []}


def test_check_route_reports_incorrect_cells(client):
    solution = sudoku_logic.create_empty_board()
    solution[0][0] = 1
    app.CURRENT['solution'] = solution

    response = client.post('/check', json={'board': [[0] * 9 for _ in range(9)]})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [[0, 0]]}


def test_check_route_requires_a_game_in_progress(client):
    response = client.post('/check', json={'board': [[0] * 9 for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


@pytest.mark.parametrize('route', ['/', '/new'])
def test_basic_routes_are_available(client, route):
    response = client.get(route)

    assert response.status_code == 200