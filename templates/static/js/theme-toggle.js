class ThemeManager {
  constructor() {
    this.isInIframe = window.self !== window.top;
    this.init();
  }

  init() {
    if (this.isInIframe) {
      // Listen for theme messages from parent dashboard
      window.addEventListener("message", (event) => {
        if (event.data?.type === "THEME_CHANGE") {
          this.setTheme(event.data.theme, false); // Don't save to localStorage in iframe
        }
      });

      // Request current theme from parent
      window.parent.postMessage({ type: "REQUEST_THEME" }, "*");
    } else {
      // Standalone mode - normal theme management
      let saved = localStorage.getItem("theme");
      if (!saved) {
        saved = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      }
      this.setTheme(saved);
      this.showThemeToggle();
    }

    // Apply initial theme based on system preference if auto
    this.applyAutoTheme();
  }

  setTheme(theme, saveToStorage = true) {
    document.documentElement.setAttribute("data-theme", theme);

    if (saveToStorage && !this.isInIframe) {
      localStorage.setItem("theme", theme);

      // Broadcast theme change to all iframes if this is the parent
      const iframes = document.querySelectorAll("iframe");
      iframes.forEach((iframe) => {
        try {
          iframe.contentWindow?.postMessage(
            {
              type: "THEME_CHANGE",
              theme: theme,
            },
            "*",
          );
        } catch (error) {
          // Ignore cross-origin errors
          console.debug("Could not send theme message to iframe:", error);
        }
      });
    }

    // Apply auto theme logic
    if (theme === "auto") {
      this.applyAutoTheme();
    }
  }

  applyAutoTheme() {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    if (currentTheme === "auto") {
      // The CSS media queries will handle the actual styling
      // But we can add a class to help with any JS-dependent features
      const prefersDark = window.matchMedia(
        "(prefers-color-scheme: dark)",
      ).matches;
      document.documentElement.classList.toggle("auto-dark", prefersDark);
      document.documentElement.classList.toggle("auto-light", !prefersDark);
    }
  }

  toggleTheme() {
    if (this.isInIframe) return; // Only parent can toggle

    const current = document.documentElement.getAttribute("data-theme");
    // Simple toggle: light -> dark -> light
    const next = current === "light" ? "dark" : "light";
    this.setTheme(next);
  }

  showThemeToggle() {
    // Only show toggle button when running standalone
    const toggleButton = document.querySelector(".theme-toggle");
    if (toggleButton) {
      toggleButton.style.display = "flex";
    }
  }

  // Get the effective theme (resolving 'auto' to actual light/dark)
  getEffectiveTheme() {
    const theme = document.documentElement.getAttribute("data-theme");
    if (theme === "auto") {
      return window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
    }
    return theme;
  }
}

// Initialize theme manager when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    window.themeManager = new ThemeManager();
  });
} else {
  window.themeManager = new ThemeManager();
}

// Listen for system theme changes to update auto theme
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", () => {
    if (window.themeManager) {
      window.themeManager.applyAutoTheme();
    }
  });

// For debugging in development
if (
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
) {
  window.debugTheme = {
    getTheme: () => document.documentElement.getAttribute("data-theme"),
    setTheme: (theme) => window.themeManager?.setTheme(theme),
    isInIframe: () => window.themeManager?.isInIframe,
    getEffectiveTheme: () => window.themeManager?.getEffectiveTheme(),
  };
}
