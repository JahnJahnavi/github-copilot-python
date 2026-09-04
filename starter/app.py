import sudoku_logic

from sudoku.game import GameState
from sudoku.web import create_app

game_state = GameState()
app = create_app(logic=sudoku_logic, state=game_state)
CURRENT = game_state.data

if __name__ == '__main__':
    app.run(debug=True)