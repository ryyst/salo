# Template Refactor Specification

Based on your `template_refactor.md` document and analysis of the existing templates, here's a comprehensive specification for unifying the template architecture across all applications.

## Current State Analysis

### Existing Templates
- **swimmi/template.html**: Complex pool schedule with specialized table layout (24px font, #e5e5e5 bg)
- **auki/template.html**: Simple store hours with basic cards (24px font, #e5e5e5 bg)
- **tori/template.html**: Events with filtering & interactions (18px font, #f8f9fa bg)
- **leffa/template.html**: Movie listings with posters (18px font, #f8f9fa bg)

### Key Inconsistencies
1. **Typography**: Font sizes vary (24px vs 18px)
2. **Colors**: Background colors differ (#e5e5e5 vs #f8f9fa), text colors (#111 vs #212529)
3. **Layout patterns**: Different approaches to cards, headers, spacing
4. **No unified theme system**: All styles hardcoded, no CSS variables
5. **No dark mode support**: Single light theme only
6. **No template inheritance**: All HTML duplicated across files

## Refactor Objectives

### 1. Unified Design System
Create a consistent visual identity across all applications with:
- Standardized typography scale
- Unified color palette with CSS custom properties
- Consistent spacing and layout patterns
- Modern, accessible design with excellent contrast ratios

### 2. Template Architecture Modernization
- **Base template**: Shared HTML structure, head, meta tags, common styles
- **Jinja inheritance**: Child templates extend base with content blocks
- **Unified header & footer**: Consistent page structure across all applications
- **Macro library**: Reusable UI components (cards, buttons, headers)
- **Theme system**: CSS variables for easy customization and dark mode
- **Self-contained output**: All CSS and JavaScript inlined in single index.html files

### 3. Dark Mode Support & Iframe Integration
- CSS custom properties for light/dark themes
- **Global theme coordination**: Apps run in iframes on main salo.fyi dashboard
- **Smart theme toggle**: Show toggle only when app runs standalone (not in iframe)
- **Cross-iframe messaging**: Theme changes propagate from parent to all iframe apps
- High contrast ratios for accessibility
- Smooth theme transitions

## Technical Implementation Plan

### Phase 1: Foundation Layer

#### 1.1 Create Base Template (`templates/base.html`)
```jinja2
<!DOCTYPE html>
<html lang="fi" data-theme="auto">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ page_title | default('Salo.fyi') }}{% endblock %}</title>

    {% block extra_head %}{% endblock %}

    <style>
    /* Inline all CSS - Theme System */
    {% include 'static/css/theme.css' %}
    
    /* Inline all CSS - Components */
    {% include 'static/css/components.css' %}
    
    {% block styles %}{% endblock %}
    </style>
</head>
<body>
    <header class="app-header">
        {% block header %}
        <div class="container">
            <h1 class="app-title">{% block app_title %}{{ app_title | default('Salo.fyi') }}{% endblock %}</h1>
            {% block header_extra %}{% endblock %}
        </div>
        {% endblock %}
        
        {% from 'macros.html' import theme_toggle %}
        {{ theme_toggle() }}
    </header>

    <main class="app-main">
        {% block content %}{% endblock %}
    </main>

    <footer class="app-footer">
        {% block footer %}
        <div class="container">
            <p class="footer-updated">
                {% block footer_updated %}
                Päivitetty {{ updated_timestamp | default('tuntematon aika') }}
                {% endblock %}
            </p>
            {% block footer_extra %}{% endblock %}
        </div>
        {% endblock %}
    </footer>

    <script>
    /* Inline all JavaScript - Theme Manager */
    {% include 'static/js/theme-toggle.js' %}
    
    {% block scripts %}{% endblock %}
    </script>
</body>
</html>
```

#### 1.2 CSS Theme System (`templates/static/css/theme.css`)
**Note: This file will be inlined via `{% include %}` - no external CSS files in output**
```css
:root[data-theme="light"] {
  /* Typography */
  --font-family-base: Calibri, Arial, sans-serif;
  --font-size-base: 18px;
  --font-size-lg: 24px;
  --font-size-sm: 16px;
  --line-height-base: 1.5;

  /* Colors - Light Theme */
  --color-bg-primary: #f8f9fa;
  --color-bg-secondary: #ffffff;
  --color-bg-tertiary: #e9ecef;
  --color-text-primary: #212529;
  --color-text-secondary: #6c757d;
  --color-text-muted: #adb5bd;

  /* Accent Colors */
  --color-accent-primary: #007bff;
  --color-accent-success: #28a745;
  --color-accent-warning: #ffc107;
  --color-accent-danger: #dc3545;

  /* Interactive */
  --color-link: #007bff;
  --color-link-hover: #0056b3;

  /* Borders & Shadows */
  --border-color: #dee2e6;
  --shadow-sm: 0 2px 4px rgba(0,0,0,0.1);
  --shadow-md: 0 4px 8px rgba(0,0,0,0.15);

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
}

:root[data-theme="dark"] {
  /* Colors - Dark Theme */
  --color-bg-primary: #1a1a1a;
  --color-bg-secondary: #2d2d2d;
  --color-bg-tertiary: #404040;
  --color-text-primary: #ffffff;
  --color-text-secondary: #cccccc;
  --color-text-muted: #999999;

  /* Accent Colors (adjusted for dark) */
  --color-accent-primary: #4dabf7;
  --color-accent-success: #51cf66;
  --color-accent-warning: #ffd43b;
  --color-accent-danger: #ff6b6b;

  /* Interactive */
  --color-link: #4dabf7;
  --color-link-hover: #74c0fc;

  /* Borders & Shadows */
  --border-color: #555555;
  --shadow-sm: 0 2px 4px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 8px rgba(0,0,0,0.4);
}

/* Auto theme detection */
@media (prefers-color-scheme: dark) {
  :root[data-theme="auto"] {
    /* Copy dark theme variables */
  }
}
```

#### 1.3 Component Library (`templates/static/css/components.css`)
**Note: This file will be inlined via `{% include %}` - no external CSS files in output**
```css
/* Base Layout */
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* Header & Footer */
.app-header {
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: 1rem 0;
  position: relative;
}

.app-title {
  color: var(--color-text-primary);
  font-size: var(--font-size-lg);
  margin: 0;
  text-align: center;
  font-weight: 600;
}

.app-main {
  min-height: calc(100vh - 120px); /* Adjust based on header/footer height */
  padding: 1rem 0;
}

.app-footer {
  background: var(--color-bg-tertiary);
  border-top: 1px solid var(--border-color);
  padding: 0.75rem 0;
  margin-top: auto;
}

.footer-updated {
  color: var(--color-text-muted);
  font-size: 0.875rem;
  text-align: center;
  margin: 0;
}

/* Typography */
.text-center { text-align: center; }
.text-muted { color: var(--color-text-muted); }

/* Cards */
.card {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  padding: 1rem;
  margin-bottom: 1rem;
}

/* Buttons */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s ease;
}

.btn-primary {
  background: var(--color-accent-primary);
  color: white;
}
```

#### 1.4 Macro Library (`templates/macros.html`)
```jinja2
{% macro card(title=none, class="") %}
<div class="card {{ class }}">
  {% if title %}
    <h3 class="card-title">{{ title }}</h3>
  {% endif %}
  {{ caller() }}
</div>
{% endmacro %}

{% macro button(text, type="button", variant="primary", onclick="") %}
<button type="{{ type }}" class="btn btn-{{ variant }}" {% if onclick %}onclick="{{ onclick }}"{% endif %}>
  {{ text }}
</button>
{% endmacro %}
```

### Phase 2: Template Migration

#### 2.1 Swimmi Template (MINIMAL CHANGES)
**Strategy**: Keep existing complex CSS intact, only unify:
- Base colors via CSS variables (background, text)
- Font family standardization
- Add unified header/footer structure
- Override header/footer styles to maintain existing look

```jinja2
{% extends "base.html" %}

{% block title %}Mahtuuko tänään uimaan?{% endblock %}

{% block app_title %}Mahtuuko tänään uimaan?{% endblock %}

{% block footer_updated %}
Päivitetty {{ data.updated_stamp }} - <a href="https://salo.fi/vapaa-aika-ja-matkailu/liikunta/sisaliikuntapaikat/uimahalli/" target="_blank">Aukioloajat</a>
{% endblock %}

{% block styles %}
<style>
  /* Override base header/footer to match swimmi styling */
  .app-header {
    background: var(--color-bg-primary);
    border: none;
    padding: 0;
  }
  
  .app-title {
    font-size: var(--font-size-lg);
    margin: 0.75rem 0;
  }
  
  .app-main {
    padding: 0;
    min-height: auto;
  }
  
  .app-footer {
    background: var(--color-bg-primary);
    border: none;
  }
  
  /* Keep ALL existing swimmi CSS but replace hardcoded colors with variables */
  html {
    font-family: var(--font-family-base);
    font-size: var(--font-size-lg); /* Keep 24px for swimmi */
    background-color: var(--color-bg-primary);
    color: var(--color-text-primary);
    box-sizing: border-box;
  }
  /* ... rest of existing CSS with color variables substituted ... */
</style>
{% endblock %}

{% block content %}
  <!-- Existing swimmi content unchanged, but remove duplicate header/footer elements -->
{% endblock %}
```

#### 2.2 Other Templates (FULL REFACTOR)
Modernize auki, tori, and leffa templates to use:
- Base template inheritance with unified header/footer
- Component macros for consistent UI elements
- CSS variables for theming
- Standardized typography scale
- App-specific titles and updated timestamps

**Example - Auki Template Structure:**
```jinja2
{% extends "base.html" %}

{% block title %}Aukioloajat - Salo{% endblock %}

{% block app_title %}Aukioloajat{% endblock %}

{% block footer_updated %}
Päivitetty {{ data.updated_timestamp | default('tuntematon aika') }}
{% endblock %}

{% block content %}
<div class="container">
  {% for place in data.places %}
    {% call card(title=place.place_name) %}
      {{ place.place_data }}
    {% endcall %}
  {% endfor %}
</div>
{% endblock %}
```

**Template-Specific Variables to Pass:**
- `app_title`: Application display name
- `updated_timestamp`: Last data update time
- Content-specific data as before

### Phase 3: Dark Mode & Iframe Integration

#### 3.1 Smart Theme Manager (`templates/static/js/theme-toggle.js`)
**Note: This file will be inlined via `{% include %}` - no external JavaScript files in output**

```javascript
class ThemeManager {
  constructor() {
    this.isInIframe = window.self !== window.top;
    this.init();
  }

  init() {
    if (this.isInIframe) {
      // Listen for theme messages from parent dashboard
      window.addEventListener('message', (event) => {
        if (event.data?.type === 'THEME_CHANGE') {
          this.setTheme(event.data.theme, false); // Don't save to localStorage in iframe
        }
      });

      // Request current theme from parent
      window.parent.postMessage({ type: 'REQUEST_THEME' }, '*');
    } else {
      // Standalone mode - normal theme management
      const saved = localStorage.getItem('theme') || 'auto';
      this.setTheme(saved);
      this.showThemeToggle();
    }
  }

  setTheme(theme, saveToStorage = true) {
    document.documentElement.setAttribute('data-theme', theme);

    if (saveToStorage && !this.isInIframe) {
      localStorage.setItem('theme', theme);

      // Broadcast theme change to all iframes if this is the parent
      const iframes = document.querySelectorAll('iframe');
      iframes.forEach(iframe => {
        iframe.contentWindow?.postMessage({
          type: 'THEME_CHANGE',
          theme: theme
        }, '*');
      });
    }
  }

  toggleTheme() {
    if (this.isInIframe) return; // Only parent can toggle

    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'light' ? 'dark' : 'light';
    this.setTheme(next);
  }

  showThemeToggle() {
    // Only show toggle button when running standalone
    const toggleButton = document.querySelector('.theme-toggle');
    if (toggleButton) {
      toggleButton.style.display = 'block';
    }
  }
}

// Global instance
window.themeManager = new ThemeManager();
```

#### 3.2 Conditional Theme Toggle UI Component
```jinja2
{% macro theme_toggle() %}
<button class="theme-toggle"
        onclick="window.themeManager?.toggleTheme()"
        aria-label="Toggle theme"
        style="display: none;">
  <span class="theme-icon light-mode">🌙</span>
  <span class="theme-icon dark-mode">☀️</span>
</button>
<style>
  .theme-toggle {
    position: fixed;
    top: 1rem;
    right: 1rem;
    background: var(--color-bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 0.5rem;
    cursor: pointer;
    z-index: 1000;
    transition: all 0.2s ease;
  }

  .theme-toggle:hover {
    background: var(--color-bg-tertiary);
  }

  [data-theme="light"] .dark-mode,
  [data-theme="dark"] .light-mode {
    display: none;
  }
</style>
{% endmacro %}
```

#### 3.3 Parent Dashboard Integration
For the main salo.fyi dashboard (koje), add theme coordination:

```javascript
// koje dashboard theme coordinator
class DashboardThemeManager {
  constructor() {
    this.init();
  }

  init() {
    // Handle theme requests from iframes
    window.addEventListener('message', (event) => {
      if (event.data?.type === 'REQUEST_THEME') {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        event.source.postMessage({
          type: 'THEME_CHANGE',
          theme: currentTheme
        }, '*');
      }
    });

    // Initialize theme management
    const themeManager = new ThemeManager();
  }
}

new DashboardThemeManager();
```

## Migration Strategy & Constraints

### Iframe-First Design Considerations
- **Primary usage**: All apps embedded in main salo.fyi dashboard via iframes
- **Standalone fallback**: Apps must work independently when accessed directly
- **Theme coordination**: Single source of truth for theme state in parent dashboard
- **Message passing**: Secure cross-frame communication for theme synchronization

### Swimmi Constraints (Critical)
- **Preserve functionality**: All existing features must work identically
- **Minimal visual changes**: Only unify colors, fonts - keep all layout/sizing
- **Keep existing CSS**: Don't refactor the complex table/pool visualization logic

### Other Templates Migration
1. **auki**: Simple conversion to use cards and variables, test in iframe context
2. **tori**: Update to use component macros, keep existing interactions
3. **leffa**: Standardize movie card layout, preserve genre color coding

### File Structure
```
templates/
├── base.html (new - inlines all CSS/JS)
├── macros.html (new)
├── static/ (development only - inlined in production)
│   ├── css/
│   │   ├── theme.css (inlined via {% include %})
│   │   └── components.css (inlined via {% include %})
│   └── js/
│       └── theme-toggle.js (inlined via {% include %})
├── swimmi/
│   └── template.html (minimal changes)
├── auki/
│   └── template.html (full refactor)
├── tori/
│   └── template.html (full refactor)
└── leffa/
    └── template.html (full refactor)

Output Structure:
_out/
├── swimmi/
│   └── index.html (self-contained)
├── auki/
│   └── index.html (self-contained)  
├── tori/
│   └── index.html (self-contained)
└── leffa/
    └── index.html (self-contained)
```

## Future Component Library Foundation

### Component Patterns
Set up architecture for future MUI-style components:
- `{% call card(title="My Card") %}Content{% endcall %}`
- `{{ button("Click me", variant="primary") }}`
- `{{ link("External", url="...", external=true) }}`

### Macro Categories
- **Layout**: Container, Grid, Stack
- **Content**: Card, Box, Paper
- **Typography**: Heading, Text, Link
- **Interactive**: Button, Link, Toggle
- **Feedback**: Alert, Badge, Status

## Success Criteria

### Functional Requirements
- [ ] All existing functionality preserved (especially swimmi)
- [ ] Visual consistency across all applications
- [ ] Dark mode support with proper contrast ratios
- [ ] Responsive design maintained
- [ ] Fast loading times (no performance regression)

### Technical Requirements
- [ ] CSS variables for all colors and typography
- [ ] Jinja template inheritance implemented
- [ ] Component macro library foundation
- [ ] Theme persistence across page loads
- [ ] Accessible color contrasts (WCAG AA compliance)
- [ ] All CSS and JavaScript inlined in single index.html files (no external dependencies)
- [ ] Self-contained applications for easy deployment and iframe embedding

### Testing Requirements
- [ ] Manual testing on all applications
- [ ] Dark/light mode toggle testing
- [ ] Mobile responsive testing
- [ ] Cross-browser compatibility
- [ ] Performance regression testing

This specification provides a complete roadmap for modernizing the template architecture while respecting your constraint about minimal swimmi changes and setting up the foundation for your future component library vision.
