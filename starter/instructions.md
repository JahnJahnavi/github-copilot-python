# GitHub Copilot Instructions for the Flask Sudoku Refactoring Project

## Project Goal
Refactor the Flask-based Sudoku application into a polished, testable, and user-friendly experience with:
- a robust Sudoku generator and solver backend,
- a responsive browser-based UI,
- a live timer and game controls,
- a leaderboard that persists high scores in browser localStorage,
- and unit tests that verify both Flask routes and Sudoku logic.

## Repository Structure
- Keep the core Sudoku engine and puzzle-generation logic in starter/sudoku_logic.py.
- Keep Flask routes, request handling, and API responses in starter/app.py.
- Keep the UI templates and frontend assets in starter/templates/ and starter/static/.
- Keep automated tests in tests/ and ensure they continue to pass after changes.

## Python Coding Standards
- Follow PEP 8 style guidelines for Python code.
- Write clear, modular functions with descriptive names.
- Use type hints for function parameters and return values where practical.
- Add docstrings to public functions and non-trivial helpers.
- Prefer small, single-responsibility functions over large monolithic blocks.
- Keep business logic in Python and avoid mixing Flask routing logic with Sudoku solver logic.

## Architecture Constraints
- Pure Sudoku solver and generator logic must remain strictly inside starter/sudoku_logic.py.
- Flask routes in starter/app.py should only handle HTTP requests, delegate to logic functions, and return JSON or rendered templates.
- Avoid placing core puzzle-generation or backtracking logic in JavaScript or HTML templates.
- Keep UI behavior simple and state-driven; the frontend should consume the backend API rather than reimplementing solver logic.

## Sudoku-Specific Rules
- Generated Sudoku boards must always have exactly one unique solution.
- Use backtracking with a solution counter to validate uniqueness.
- The solver must enforce early termination when the solution count exceeds one, using the logic that returns as soon as count >= 2.
- Prevent infinite loops or excessive recursion by stopping search branches as soon as multiple solutions are detected.
- Preserve the single-solution guarantee when removing clues during puzzle generation.

## Frontend and UI Guidelines
- Build the 9x9 Sudoku board using CSS Grid.
- Use accessible, high-contrast colors and distinguish 3x3 sub-grids with alternating styling.
- Support interactive game controls such as timer, hint, and answer checking.
- Persist leaderboard scores in browser localStorage.
- Keep the interface responsive and easy to use on desktop and mobile screens.

## Testing Expectations
- Add or update pytest tests when introducing new behavior.
- Verify both backend and frontend-related changes with relevant tests.
- Ensure puzzle generation still produces boards with exactly one unique solution after refactoring.

## General Guidance
- Prefer maintainable and readable code over clever shortcuts.
- Document complex algorithms clearly so future contributors can understand them quickly.
- Preserve the existing project intent while improving structure, reliability, and test coverage.