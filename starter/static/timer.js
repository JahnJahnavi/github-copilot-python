class GameTimer {
  constructor(displayElement) {
    this.displayElement = displayElement;
    this.intervalId = null;
    this.elapsedSeconds = 0;
    this.completionTime = null;
    this.render();
  }

  start() {
    this.stop();
    this.elapsedSeconds = 0;
    this.completionTime = null;
    this.render();
    this.intervalId = setInterval(() => {
      this.elapsedSeconds++;
      this.render();
    }, 1000);
  }

  stop() {
    if (this.intervalId !== null) {
      clearInterval(this.intervalId);
      this.intervalId = null;
      this.completionTime = this.elapsedSeconds;
    }
  }

  reset() {
    this.stop();
    this.elapsedSeconds = 0;
    this.completionTime = null;
    this.render();
  }

  render() {
    const minutes = Math.floor(this.elapsedSeconds / 60);
    const seconds = this.elapsedSeconds % 60;
    this.displayElement.innerText = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }
}
