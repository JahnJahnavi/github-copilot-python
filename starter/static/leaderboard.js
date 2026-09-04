class Leaderboard {
  constructor(storageKey, displayElement, storage = window.localStorage) {
    this.storageKey = storageKey;
    this.displayElement = displayElement;
    this.storage = storage;
    this.render();
  }

  getScores() {
    try {
      const scores = JSON.parse(this.storage.getItem(this.storageKey) || '[]');
      return Array.isArray(scores) ? scores : [];
    } catch (error) {
      return [];
    }
  }

  addScore(score) {
    const scores = this.getScores();
    scores.push({
      name: score.name,
      time: score.time,
      difficulty: score.difficulty,
      hints: score.hints,
    });
    scores.sort((first, second) => first.time - second.time);
    const topScores = scores.slice(0, 10);
    this.storage.setItem(this.storageKey, JSON.stringify(topScores));
    this.render(topScores);
  }

  render(scores = this.getScores()) {
    this.displayElement.innerHTML = '';
    if (scores.length === 0) {
      this.displayElement.innerText = 'No scores yet.';
      return;
    }

    const table = document.createElement('table');
    table.innerHTML = `
      <caption>Top 10</caption>
      <thead>
        <tr><th>Rank</th><th>Name</th><th>Time</th><th>Difficulty</th><th>Hints</th></tr>
      </thead>
      <tbody></tbody>
    `;
    const body = table.querySelector('tbody');
    scores.forEach((score, index) => {
      const row = document.createElement('tr');
      [
        index + 1,
        score.name,
        Leaderboard.formatTime(score.time),
        score.difficulty,
        score.hints,
      ].forEach(value => {
        const cell = document.createElement('td');
        cell.innerText = value;
        row.appendChild(cell);
      });
      body.appendChild(row);
    });
    this.displayElement.appendChild(table);
  }

  static formatTime(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }
}
