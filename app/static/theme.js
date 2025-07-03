(() => {
  const root = document.documentElement;

  const applyTheme = (theme, toggle) => {
    root.dataset.theme = theme;

    if (!toggle) {
      return;
    }

    const isDark = theme === "dark";
    const label = toggle.querySelector("[data-theme-label]");
    toggle.setAttribute("aria-pressed", String(isDark));

    if (label) {
      label.textContent = isDark ? "다크 모드" : "라이트 모드";
    }
  };

  document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector("[data-theme-toggle]");
    const currentTheme = root.dataset.theme || "light";

    applyTheme(currentTheme, toggle);

    if (!toggle) {
      return;
    }

    toggle.addEventListener("click", () => {
      const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
      localStorage.setItem("theme", nextTheme);
      applyTheme(nextTheme, toggle);
    });
  });
})();
