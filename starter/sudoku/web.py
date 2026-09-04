from pathlib import Path

from flask import Flask, jsonify, render_template, request

from .game import GameState
from . import logic as default_logic

DIFFICULTY_CLUES = {
    'easy': 40,
    'medium': 32,
    'hard': 26,
}


def create_app(logic=default_logic, state=None):
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        static_folder=project_root / 'static',
        template_folder=project_root / 'templates',
    )
    game_state = state or GameState()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/new')
    def new_game():
        difficulty = request.args.get('difficulty')
        if difficulty is None:
            clues = int(request.args.get('clues', 35))
        elif difficulty not in DIFFICULTY_CLUES:
            return jsonify({'error': 'Invalid difficulty'}), 400
        else:
            clues = DIFFICULTY_CLUES[difficulty]
        puzzle, solution = logic.generate_puzzle(clues)
        game_state.start(puzzle, solution)
        return jsonify({'puzzle': puzzle})

    @app.route('/check', methods=['POST'])
    def check_solution():
        data = request.json
        board = data.get('board')
        if game_state.solution is None:
            return jsonify({'error': 'No game in progress'}), 400
        return jsonify({
            'incorrect': game_state.incorrect_cells(board, logic.SIZE),
        })

    @app.route('/hint', methods=['POST'])
    def hint():
        if game_state.solution is None:
            return jsonify({'error': 'No game in progress'}), 400
        board = request.json.get('board')
        result = game_state.hint(board, logic.EMPTY)
        if result is None:
            if not game_state.is_complete(board, logic.SIZE):
                return jsonify({
                    'complete': False,
                    'no_empty': True,
                    'hints_used': game_state.hints_used,
                })
            return jsonify({
                'complete': True,
                'hints_used': game_state.hints_used,
            })
        row, column, value = result
        return jsonify({
            'row': row,
            'col': column,
            'value': value,
            'hints_used': game_state.hints_used,
        })

    @app.route('/solve', methods=['POST'])
    def solve():
        if game_state.puzzle is None:
            return jsonify({'error': 'No game in progress'}), 400
        solution = logic.solve_board(game_state.puzzle)
        if solution is None:
            return jsonify({'error': 'Puzzle cannot be solved'}), 422
        return jsonify({'solution': solution})

    app.game_state = game_state
    return app
