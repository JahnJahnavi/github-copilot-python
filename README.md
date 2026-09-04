# Flask Sudoku

A browser-based Sudoku game built with Flask and vanilla JavaScript. The application generates puzzles with a unique solution and includes difficulty levels, locked clues, live validation, hints, a timer, completion tracking, a persistent Top 10 leaderboard, responsive styling, and Light/Dark Mode.

## Requirements

- Python 3.10 or newer
- A modern web browser

## Installation

From the repository root, create and activate a virtual environment:

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r starter/requirements.txt
```

## Run the Application

Run Flask from the `starter` directory:

```bash
cd starter
python app.py
```

Open <http://127.0.0.1:5000> in a browser.

## Run the Tests

From the repository root, with the virtual environment active:

```bash
python -m pytest -q
```

The repository-level `pytest.ini` discovers tests in `starter/tests` and adds `starter` to the Python path.

## Project Structure

```text
starter/
	app.py                 Flask entry point and compatibility API
	sudoku_logic.py        Backward-compatible Sudoku logic imports
	sudoku/
		game.py              Game state, hints, and completion checks
		logic.py             Puzzle generation and solution counting
		web.py               Flask app factory and routes
	static/
		main.js              Board interaction and game workflow
		timer.js             Timer component
		leaderboard.js       LocalStorage leaderboard component
		theme.js             Persistent theme component
		styles.css           Responsive themed UI styles
	templates/
		index.html           Game page
	tests/
		test_sudoku.py       Sudoku logic and Flask route tests
```

## Notes

- Puzzle solutions remain on the server and are not returned to the browser.
- Leaderboard entries and the theme preference are stored in browser localStorage.
- Leaderboard data is local to each browser and is not shared between users.
