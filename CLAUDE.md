# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup
```bash
pipenv install
pipenv shell
```

### Running the Application
```bash
# List all available runners
pipenv run python main.py runners

# Show configuration schema for a specific runner
pipenv run python main.py runners auki

# Execute a runner with configuration file
pipenv run python main.py runners auki _confs/auki.json

# Execute with custom output/cache directories
pipenv run python main.py runners auki _confs/auki.json --output-dir custom_out --cache-dir custom_cache

# Force refresh all data (ignore cache)
pipenv run python main.py runners auki _confs/auki.json --ignore-cache

# Preview generated static files
cat _out/auki/index.html
```

### Code Formatting
```bash
# Format all Python code (required before commits)
black --line-length=100 .
```

## Architecture

This is a Python ETL pipeline framework that generates static websites using Jinja2 templates. The system uses a **runner-based architecture** where pipelines are hardcoded in individual Python functions.

### Core ETL Pipeline
Each runner follows a standard 3-step ETL pattern:
- **Fetch**: Retrieve raw data from external sources
- **Transform**: Process raw data into renderable format
- **Render**: Output processed data to HTML files

### Module Structure
The codebase is organized into domain-specific modules:

- **swimmi/**: Swimming pool schedule processing
- **auki/**: Store front opening hours processing (libraries, shops, etc.)
- **tori/**: Event calendar processing (town square of events)
- **saa/**: Weather forecast processing (FMI API integration)
- **leffa/**: Movie schedule processing
- **koje/**: Dashboard PWA that embeds other services
- **utils/**: Shared utilities (caching, logging, dev server, base schemas)
- **api/**: External API integrations

### Runner System
- **Runners** are hardcoded Python functions that define complete ETL pipelines
- Each runner is registered using the `@register_runner` decorator in `config.py`
- Runners are located in `module/runners.py` files and imported in `main.py`
- JSON configs contain **only parameters**, no function selection logic
- Configuration files are expected in `_confs/` directory or can be specified with `--params`
- CLI supports custom output/cache directories and cache invalidation

### Key Components
- `config.py`: Runner registry system with decorator-based registration and global CLI context
- `main.py`: CLI entry point with runner management
- `module/runners.py`: Pipeline definitions for each module
- `utils/schema.py`: Base JSONModel with camelCase/snake_case conversion
- `utils/renderers.py`: Jinja2 template rendering and file output utilities
- `utils/cache.py`: HTTP request caching system
- `utils/logging.py`: Centralized logging utilities

### Runner Registration Pattern
Each module registers runners using the decorator pattern:
```python
from config import register_runner
from .config import ModuleConfig

@register_runner("runner_name", ModuleConfig, "Description")
def run_example(params: ModuleConfig):
    raw_data = fetch_function(params)
    processed_data = transform_function(raw_data, params)
    render_function(processed_data, params)
```

## Development Workflow

### Adding New Runners
1. Create runner function in appropriate `module/runners.py` file
2. Use `@register_runner("name", ConfigClass, "description")` decorator
3. Implement ETL pipeline calling existing fetch/transform/render functions
4. Create JSON parameter file in `_confs/` for testing
5. Test with `python main.py runners <name> <config_file>`

### Adding New Modules
1. Create module directory with standard files: `fetch.py`, `transform.py`, `config.py`, `runners.py`
2. Implement Pydantic config class in `config.py` extending `JSONModel` from `utils.schema`
3. Create `runners.py` file with `@register_runner` decorated functions
4. Create `__init__.py` that imports `runners.py` to ensure registration
5. Import the new module in `main.py` to activate runners
6. Create parameter JSON files in `_confs/` for testing

### Module File Structure
Each module follows this pattern:
- `config.py`: Pydantic configuration schema
- `fetch.py`: Data retrieval from external APIs
- `transform.py`: Data processing and transformation
- `runners.py`: ETL pipeline orchestration with @register_runner
- `schema.py`: (optional) Domain-specific data models
- `api.py`: (optional) API-specific integrations

### Output Structure
- Generated static files are placed in `_out/` subdirectories (configurable via CLI)
- Each module creates its own output subdirectory (e.g., `_out/swimmi/`, `_out/auki/`)
- HTML files use Jinja2 templates, always located in modlue-specific app/template.html file.
- Multiple pages can be generated per runner (e.g., swimmi generates daily pages)

### Caching and Data Management
- HTTP requests are cached in `_cache/` directory (configurable via CLI)
- Cache files are date-prefixed for automatic invalidation
- Use `--ignore-cache` flag to force fresh data retrieval
- Raw data is cached before transformation for faster development iteration

### Dependencies and External APIs
- Core: `requests`, `beautifulsoup4`, `jinja2`, `pydantic`
- Integrates with Finnish local services (swimming pools, libraries, events)
- `api/baserow.py` provides optional database integration for structured data

## Template & Component Standards

This project uses a **shared design system** for consistent UI across all apps. All new modules MUST follow these standards.

### Template Architecture

#### Base Template System
All app templates MUST extend the shared base template:

```jinja2
{% extends "base.html" %}
{% from 'macros.html' import card, badge, button, link %}

{% block title %}App Name - {{ data.title }}{% endblock %}
{% block app_title %}{{ data.title }}{% endblock %}

{% block footer_updated %}
Päivitetty {{ data.updated_time }} - <a href="source_url" target="_blank">Data Source</a>
{% endblock %}

{% block content %}
<div class="container">
  {% call card(title="Main Content Title") %}
    <!-- App-specific content here -->
  {% endcall %}
</div>
{% endblock %}

{% block styles %}
<style>
  /* App-specific CSS using design system variables */
</style>
{% endblock %}
```

#### Required Template Structure
- **MUST** extend `base.html`
- **MUST** import macros from `macros.html`
- **MUST** use `container` class for main content
- **MUST** use `card` macro for primary content sections
- **MUST** provide updated timestamp in footer
- **MUST** use design system CSS variables for styling

### Design System

#### CSS Variables (Theme-Aware)
The design system provides consistent variables for both light and dark themes:

**Typography:**
- `--font-family-base`: Calibri, Arial, sans-serif
- `--font-size-base`: 18px
- `--font-size-lg`: 24px
- `--font-size-sm`: 16px
- `--line-height-base`: 1.5

**Colors:**
- `--color-bg-primary`: Main background
- `--color-bg-secondary`: Card/container backgrounds
- `--color-bg-tertiary`: Hover states, headers
- `--color-text-primary`: Main text color
- `--color-text-secondary`: Secondary text
- `--color-text-muted`: Muted/disabled text

**Accent Colors:**
- `--color-accent-primary`: Blue (#007bff / #4dabf7)
- `--color-accent-success`: Green (#28a745 / #51cf66)
- `--color-accent-warning`: Yellow (#ffc107 / #ffd43b)
- `--color-accent-danger`: Red (#dc3545 / #ff6b6b)

**Layout:**
- `--border-color`: Consistent border color
- `--shadow-sm`: Small shadow (0 2px 4px)
- `--shadow-md`: Medium shadow (0 4px 8px)
- `--radius-sm`: 4px
- `--radius-md`: 8px
- `--radius-lg`: 12px

#### Available Macros

**Card Component:**
```jinja2
{% call card(title="Optional Title", class="optional-classes") %}
  Content goes here
{% endcall %}
```

**Button Component:**
```jinja2
{{ button("Click Me", type="button", variant="primary", onclick="", href="") }}
```

**Badge Component:**
```jinja2
{{ badge("Status", variant="success|danger|warning|info") }}
```

**Status Indicators:**
```jinja2
{{ status_badge(is_open, open_text="Auki", closed_text="Kiinni") }}
```

**Link Component:**
```jinja2
{{ link("Link Text", "url", external=true, class="") }}
```

#### Utility Classes
- `.container`: Max-width centered container
- `.text-center`: Center text alignment
- `.text-muted`: Muted text color
- `.card`: Card container with shadow and borders
- `.btn`: Button styling
- `.badge`: Small status badges

### Component Patterns

#### Data Tables
For tabular data, use this pattern:
```jinja2
<div class="table-container">
  <table class="data-table">
    <thead>
      <tr>
        <th>Column 1</th>
        <th>Column 2</th>
      </tr>
    </thead>
    <tbody>
      {% for item in data.items %}
      <tr class="data-row">
        <td>{{ item.field1 }}</td>
        <td>{{ item.field2 }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
```

#### Responsive Design
- Use CSS Grid/Flexbox for layouts
- Mobile-first approach with progressive enhancement
- Hide non-essential columns on small screens
- Ensure touch-friendly interactive elements

#### Color Coding
Use semantic color variables for consistent meaning:
- **Success/Open**: `--color-accent-success`
- **Warning/Caution**: `--color-accent-warning`
- **Danger/Closed**: `--color-accent-danger`
- **Info/Neutral**: `--color-accent-primary`

### Theme Integration

#### Automatic Theme Management
The base template includes:
- Theme toggle button (hidden in iframes)
- System preference detection
- Parent-child theme synchronization for dashboards
- Smooth transitions between themes

#### Theme-Aware JavaScript
```javascript
// Theme manager is available globally
window.themeManager.getEffectiveTheme() // Returns "light" or "dark"
window.themeManager.setTheme("light|dark") // Set theme
```

### Module Template Requirements

#### File Structure
```
module/
├── __init__.py          # Import runners for registration
├── config.py           # Pydantic config extending JSONModel
├── fetch.py            # Data retrieval functions
├── transform.py        # Data processing functions
├── runners.py          # @register_runner decorated functions
├── template.html       # MUST extend base.html
└── api.py             # (optional) API integrations
```

#### Template Location
Templates MUST be located at `module/template.html` or similar descriptive name.

#### Data Context
The `render_html()` function passes data as `data=context`, so all template variables must be accessed as `data.variable_name`.

### Testing Templates

#### Manual Testing
```bash
# Generate and view output
pipenv run python main.py runners module_name
open _out/module_name/index.html
```

#### Design System Compliance Checklist
- [ ] Extends `base.html`
- [ ] Uses `container` class
- [ ] Uses `card` macro for content sections
- [ ] Uses CSS variables instead of hardcoded colors
- [ ] Responsive design with mobile considerations
- [ ] Proper semantic color usage
- [ ] Theme toggle works (when standalone)
- [ ] Footer shows update time and source

## Code Standards

- All python code must be appropriately formatted with `black --line-length=100`.
- Keep things as DRY as possible
- ALL templates must follow the design system standards above
- All apps are displayed in an iframe of max-width: 600px, so all styles MUST be mobile first, even on desktop.
