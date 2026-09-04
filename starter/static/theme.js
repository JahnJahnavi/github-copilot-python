class ThemeManager {
  constructor(storageKey, toggleButton, storage = window.localStorage) {
    this.storageKey = storageKey;
    this.toggleButton = toggleButton;
    this.storage = storage;
    this.theme = this.getSavedTheme();
    this.apply();
    this.toggleButton.addEventListener('click', () => this.toggle());
  }

  getSavedTheme() {
    try {
      return this.storage.getItem(this.storageKey) === 'dark' ? 'dark' : 'light';
    } catch (error) {
      return 'light';
    }
  }

  toggle() {
    this.theme = this.theme === 'dark' ? 'light' : 'dark';
    try {
      this.storage.setItem(this.storageKey, this.theme);
    } catch (error) {
      // The theme still applies when storage is unavailable.
    }
    this.apply();
  }

  apply() {
    document.documentElement.dataset.theme = this.theme;
    const isDark = this.theme === 'dark';
    this.toggleButton.innerText = isDark ? 'Light Mode' : 'Dark Mode';
    this.toggleButton.setAttribute('aria-pressed', String(isDark));
  }
}
