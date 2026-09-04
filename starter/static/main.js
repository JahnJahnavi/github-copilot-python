// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let gameTimer;
let gameCompleted = false;
let completionRecord = null;
let checkRequestVersion = 0;
let leaderboard;
let hintsUsed = 0;
let noteMode = false;
let solving = false;

function setMessageState(messageElement, state) {
  messageElement.classList.remove('message-error', 'message-success');
  messageElement.classList.add(`message-${state}`);
}

function getBoardValues(inputs) {
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

function isValidMove(board, row, col, value) {
  if (value === 0) return true;

  for (let i = 0; i < SIZE; i++) {
    if ((i !== col && board[row][i] === value) ||
        (i !== row && board[i][col] === value)) {
      return false;
    }
  }

  const startRow = row - row % 3;
  const startCol = col - col % 3;
  for (let i = startRow; i < startRow + 3; i++) {
    for (let j = startCol; j < startCol + 3; j++) {
      if ((i !== row || j !== col) && board[i][j] === value) {
        return false;
      }
    }
  }
  return true;
}

function validateBoard() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = getBoardValues(inputs);
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const input = inputs[i * SIZE + j];
      if (input.disabled) continue;
      const value = board[i][j];
      input.classList.toggle('invalid', value !== 0 && !isValidMove(board, i, j, value));
    }
  }
}

function clearNumberHighlights() {
  const cells = document.querySelectorAll('.cell-container');
  cells.forEach(cell => cell.classList.remove('number-match', 'selected-number'));
}

function highlightMatchingNumber(cell) {
  clearNumberHighlights();
  const input = cell.querySelector('.sudoku-cell');
  const value = input.value;
  if (!value) return;

  const cells = document.querySelectorAll('.cell-container');
  for (const currentCell of cells) {
    if (currentCell.querySelector('.sudoku-cell').value === value) {
      currentCell.classList.add('number-match');
    }
  }
  cell.classList.add('selected-number');
}

function renderCellNotes(input) {
  const notes = input.parentElement.querySelector('.cell-notes');
  const values = input.dataset.notes || '';
  for (let value = 1; value <= 9; value++) {
    notes.children[value - 1].innerText = values.includes(String(value)) ? value : '';
  }
}

function toggleCellNote(input, value) {
  const notes = input.dataset.notes || '';
  input.dataset.notes = notes.includes(value)
    ? notes.replace(value, '')
    : `${notes}${value}`.split('').sort().join('');
  renderCellNotes(input);
}

function setNoteMode(enabled) {
  noteMode = enabled;
  const button = document.getElementById('note-mode');
  button.innerText = `Note Mode: ${enabled ? 'On' : 'Off'}`;
  button.setAttribute('aria-pressed', String(enabled));
}

function setCellAccessibility(input, row, column, locked) {
  const state = locked ? 'locked' : 'editable';
  input.setAttribute('aria-label', `Row ${row + 1}, column ${column + 1}, ${state} Sudoku cell`);
  input.setAttribute('aria-readonly', String(locked));
}

function moveFocus(event, input) {
  const directions = {
    ArrowUp: [-1, 0],
    ArrowDown: [1, 0],
    ArrowLeft: [0, -1],
    ArrowRight: [0, 1],
  };
  if (!directions[event.key]) return;

  const [rowDelta, columnDelta] = directions[event.key];
  const row = Number(input.dataset.row);
  const column = Number(input.dataset.col);
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  let nextRow = row + rowDelta;
  let nextColumn = column + columnDelta;
  while (nextRow >= 0 && nextRow < SIZE && nextColumn >= 0 && nextColumn < SIZE) {
    const nextInput = inputs[nextRow * SIZE + nextColumn];
    if (!nextInput.disabled) {
      event.preventDefault();
      nextInput.focus();
      return;
    }
    nextRow += rowDelta;
    nextColumn += columnDelta;
  }
}

function wait(milliseconds) {
  return new Promise(resolve => setTimeout(resolve, milliseconds));
}

function setSolvingState(disabled) {
  solving = disabled;
  document.querySelectorAll('.controls button, #difficulty').forEach(control => {
    control.disabled = disabled;
  });
  document.querySelectorAll('.sudoku-cell').forEach(input => {
    if (disabled) input.disabled = true;
  });
}

async function solvePuzzle() {
  if (solving) return;
  const response = await fetch('/solve', {method: 'POST'});
  const data = await response.json();
  const message = document.getElementById('message');
  if (data.error) {
    setMessageState(message, 'error');
    message.innerText = data.error;
    return;
  }

  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  setSolvingState(true);
  for (let row = 0; row < SIZE; row++) {
    for (let column = 0; column < SIZE; column++) {
      const index = row * SIZE + column;
      if (puzzle[row][column] !== 0) continue;
      const input = inputs[index];
      input.value = '';
      input.dataset.notes = '';
      renderCellNotes(input);
      await wait(80);
      input.value = data.solution[row][column];
      input.readOnly = true;
      input.classList.remove('invalid', 'incorrect', 'incomplete');
      input.classList.add('locked');
    }
  }
  document.querySelectorAll('.sudoku-cell').forEach(input => {
    input.disabled = true;
  });
  gameTimer.stop();
  setSolvingState(false);
  document.getElementById('solve-puzzle').disabled = true;
  setMessageState(message, 'success');
  message.innerText = 'Puzzle solved.';
}

function hasEmptyEditableCell(inputs) {
  return Array.from(inputs).some(input => !input.disabled && input.value === '');
}

function completePuzzle(messageElement) {
  if (gameCompleted) return;
  gameCompleted = true;
  gameTimer.stop();
  const playerName = window.prompt('Puzzle complete! Enter your name for the leaderboard:');
  completionRecord = {
    name: playerName && playerName.trim() ? playerName.trim() : 'Anonymous',
    time: gameTimer.completionTime,
    difficulty: document.getElementById('difficulty').value || 'Standard',
    hints: hintsUsed,
  };
  leaderboard.addScore(completionRecord);
  document.getElementById('hint').disabled = true;
  setMessageState(messageElement, 'success');
  messageElement.innerText = 'Congratulations! You solved it!';
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    rowDiv.setAttribute('role', 'row');
    for (let j = 0; j < SIZE; j++) {
      const cell = document.createElement('div');
      cell.className = 'cell-container';
      cell.setAttribute('role', 'gridcell');
      const notes = document.createElement('div');
      notes.className = 'cell-notes';
      notes.setAttribute('aria-hidden', 'true');
      for (let value = 1; value <= 9; value++) {
        const note = document.createElement('span');
        note.innerText = '';
        notes.appendChild(note);
      }
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.dataset.notes = '';
      setCellAccessibility(input, i, j, false);
      input.addEventListener('keydown', (e) => moveFocus(e, input));
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        if (noteMode) {
          e.target.value = '';
          if (val) toggleCellNote(e.target, val);
          return;
        }
        e.target.value = val;
        e.target.dataset.notes = '';
        renderCellNotes(e.target);
        validateBoard();
        const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
        if (!hasEmptyEditableCell(inputs)) checkPuzzle();
      });
      cell.appendChild(notes);
      cell.appendChild(input);
      rowDiv.appendChild(cell);
    }
    boardDiv.appendChild(rowDiv);
  }
  boardDiv.onclick = (event) => {
    const cell = event.target.closest('.cell-container');
    if (cell && boardDiv.contains(cell)) highlightMatchingNumber(cell);
  };
}

function renderPuzzle(puz) {
  puzzle = puz;
  gameCompleted = false;
  completionRecord = null;
  hintsUsed = 0;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      const isPrefilled = val !== 0;
      inp.classList.toggle('locked', isPrefilled);
      inp.classList.toggle('prefilled', isPrefilled);
      inp.readOnly = isPrefilled;
      inp.disabled = isPrefilled;
      setCellAccessibility(inp, i, j, isPrefilled);
      inp.dataset.notes = '';
      renderCellNotes(inp);
      if (isPrefilled) {
        inp.value = val;
      } else {
        inp.value = '';
      }
    }
  }
  document.getElementById('hint').disabled = false;
  document.getElementById('hint-count').innerText = 'Hints: 0';
}

async function newGame() {
  checkRequestVersion++;
  const difficulty = document.getElementById('difficulty').value;
  const query = difficulty ? `?difficulty=${encodeURIComponent(difficulty)}` : '';
  const res = await fetch(`/new${query}`);
  const data = await res.json();
  if (data.error) {
    document.getElementById('message').innerText = data.error;
    return;
  }
  renderPuzzle(data.puzzle);
  gameTimer.start();
  const message = document.getElementById('message');
  setMessageState(message, 'error');
  message.innerText = '';
}

async function useHint() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = getBoardValues(inputs);
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    setMessageState(msg, 'error');
    msg.innerText = data.error;
    return;
  }

  hintsUsed = data.hints_used;
  document.getElementById('hint-count').innerText = `Hints: ${hintsUsed}`;
  if (data.complete) {
    document.getElementById('hint').disabled = true;
    setMessageState(msg, 'success');
    msg.innerText = 'The puzzle is already complete.';
    return;
  }
  if (data.no_empty) {
    setMessageState(msg, 'error');
    msg.innerText = 'No empty cells available for a hint.';
    return;
  }

  const input = inputs[data.row * SIZE + data.col];
  input.value = data.value;
  input.dataset.notes = '';
  renderCellNotes(input);
  input.readOnly = true;
  input.disabled = true;
  setCellAccessibility(input, data.row, data.col, true);
  input.classList.remove('invalid', 'incorrect', 'incomplete');
  input.classList.add('locked');
  validateBoard();
  if (!hasEmptyEditableCell(inputs)) checkPuzzle();
}

function clearCheckHighlights(inputs) {
  for (const input of inputs) {
    if (input.disabled) continue;
    input.classList.remove('invalid', 'incorrect', 'incomplete');
  }
}

async function checkPuzzle() {
  const requestVersion = ++checkRequestVersion;
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = getBoardValues(inputs);
  clearCheckHighlights(inputs);
  validateBoard();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  if (requestVersion !== checkRequestVersion) return;
  const msg = document.getElementById('message');
  if (data.error) {
    setMessageState(msg, 'error');
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0] * SIZE + x[1]));
  let incorrectCount = 0;
  let emptyCount = 0;
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const input = inputs[idx];
      if (input.disabled) continue;
      if (board[i][j] === 0) {
        input.classList.add('incomplete');
        emptyCount++;
      } else if (incorrect.has(idx)) {
        input.classList.add('incorrect');
        incorrectCount++;
      }
    }
  }

  if (incorrectCount === 0 && emptyCount === 0) {
    completePuzzle(msg);
  } else if (incorrectCount === 0) {
    setMessageState(msg, 'success');
    msg.innerText = 'No mistakes found so far.';
  } else {
    setMessageState(msg, 'error');
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  gameTimer = new GameTimer(document.getElementById('timer'));
  leaderboard = new Leaderboard(
    'sudoku-top-scores',
    document.getElementById('leaderboard'),
  );
  new ThemeManager('sudoku-theme', document.getElementById('theme-toggle'));
  document.getElementById('note-mode').addEventListener('click', () => setNoteMode(!noteMode));
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('difficulty').addEventListener('change', newGame);
  document.getElementById('check-puzzle').addEventListener('click', checkPuzzle);
  document.getElementById('solve-puzzle').addEventListener('click', solvePuzzle);
  document.getElementById('hint').addEventListener('click', useHint);
  // initialize
  newGame();
});