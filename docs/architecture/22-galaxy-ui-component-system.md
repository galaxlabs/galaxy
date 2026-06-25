# 22 — Galaxy UI Component System

## 1. Purpose

Define the architecture for Galaxy Framework's server-rendered UI component system. This system powers Galaxy Desk and Galaxy Studio with modern, customizable, themeable components while keeping the core lightweight and dependency-free from heavy SPA frameworks.

## 2. Why Galaxy Needs Its Own UI Component System

Frappe's Desk UI is powerful but widely perceived as hard to customize. Common complaints:

- Colors and branding require deep CSS overrides or patching core files.
- Component styles are tightly coupled to Frappe's CSS framework (FRL, Bootstrap-based).
- Customizing form layouts, button styles, or table densities requires overriding large CSS blocks.
- No formal theme system — changing brand colors means editing multiple CSS files.
- Component variants (e.g., button size/tone) are inconsistent across Desk views.

Galaxy should solve this by building a **component system from day one** with:

- A formal theme/token system
- Consistent component variants
- Per-component styling via CSS variables
- Server-rendered macros (Jinja2) as the primary API
- Optional JS enhancements via vanilla JavaScript

## 3. Why Not Depend on React shadcn/ui for Core Desk

| Reason | Explanation |
|--------|-------------|
| **Server-rendered core** | Galaxy Desk is Jinja2/HTMX first. React would require a full SPA build pipeline for every Desk page. |
| **Bundle size** | React + shadcn/ui + dependencies adds ~150KB+ gzipped just for the framework. Galaxy Desk pages should load fast without a JS framework. |
| **SEO/SSR complexity** | Server-rendered pages are simpler to optimize, cache, and debug. |
| **CDN/offline simplicity** | No client-side routing, no hydration, no virtual DOM needed for admin CRUD interfaces. |
| **Gradual enhancement** | JS should enhance, not be required. A Desk form should work without JavaScript. |

**shadcn/ui philosophy** (which Galaxy adopts):

- Components are copy-owned, not dependency-managed.
- You control the source, not an opaque npm package.
- Styling via Tailwind classes + CSS variables.
- Themeable through token-based design.

## 4. shadcn-style Ideas Galaxy Will Borrow

| Idea | Galaxy Adaptation |
|------|-------------------|
| Copy-owned components | Components are Jinja2 macros in `galaxy/desk/components/`. Developers copy and customize. |
| Tailwind + CSS variables | Galaxy uses Tailwind classes + `--galaxy-*` CSS variables for theming. |
| Variant-based components | Each component supports `variant`, `tone`, `size` parameters. |
| Theme tokens | A set of CSS variables that cascade through all components. |
| Per-project customization | Developers override component macros or theme tokens per project. |
| Accessible by default | ARIA attributes, keyboard navigation, focus management built into macros. |
| No runtime CSS-in-JS | All styling is static CSS + variables. No runtime style computation. |

## 5. Core UI Stack

| Layer | Technology | Role |
|-------|------------|------|
| Templates | Jinja2 | Server-rendered HTML with component macros |
| HTTP enhancement | HTMX | Partial page updates, form submission, dynamic content |
| Styling | Tailwind CSS | Utility-first CSS framework |
| Design tokens | CSS variables | `--galaxy-primary`, `--galaxy-radius`, etc. |
| Interactivity | Vanilla JavaScript | Client scripts, toasts, modals, command palette |
| Complex widgets | Optional JS widgets | Rich text editor, date picker, file upload (no framework) |
| Build | Tailwind CLI | Generates `desk.css` from Tailwind config + theme tokens |

## 6. Component Registry Design

Components live in `galaxy/desk/components/` as Jinja2 macro files.

### Directory structure

```text
galaxy/desk/components/
├── __init__.py           ← component registry loader
├── button.html           ← macro: ui.button()
├── card.html
├── badge.html
├── alert.html
├── toast.html
├── modal.html
├── drawer.html
├── tabs.html
├── table.html
├── datagrid.html
├── form.html             ← form layout builder
├── form_field.html       ← single field with label/error
├── text_input.html
├── select.html
├── checkbox.html
├── date_input.html
├── file_upload.html
├── empty_state.html
├── confirm_dialog.html
├── command_palette.html
├── sidebar.html
├── topbar.html
├── breadcrumb.html
├── stepper.html
├── migration_preview.html
├── permission_matrix.html
└── theme_switcher.html
```

### Registry loader

```python
# galaxy/desk/components/__init__.py

import os
from jinja2 import Environment, FileSystemLoader

_component_env = None

def get_component_env():
    global _component_env
    if _component_env is None:
        path = os.path.join(os.path.dirname(__file__))
        _component_env = Environment(
            loader=FileSystemLoader(path),
            autoescape=True,
        )
    return _component_env

def render_component(name, **kwargs):
    env = get_component_env()
    template = env.get_template(f"{name}.html")
    return template.render(**kwargs)
```

### Template injection into Jinja2 globals

```python
# In server.py or desk/routes.py

from galaxy.desk.components import render_component

def ui():
    return {
        "button": lambda **kw: render_component("button", **kw),
        "card": lambda **kw: render_component("card", **kw),
        "badge": lambda **kw: render_component("badge", **kw),
        # ... etc
    }

templates.env.globals["ui"] = ui()
```

## 7. Theme System Design

### CSS Variables (Design Tokens)

```css
:root {
  /* Brand */
  --galaxy-primary: #2563eb;
  --galaxy-accent: #8b5cf6;
  --galaxy-success: #16a34a;
  --galaxy-warning: #d97706;
  --galaxy-danger: #dc2626;
  --galaxy-info: #0891b2;

  /* Backgrounds */
  --galaxy-bg: #ffffff;
  --galaxy-surface: #f8fafc;
  --galaxy-muted: #f1f5f9;

  /* Text */
  --galaxy-text: #0f172a;
  --galaxy-muted-text: #64748b;
  --galaxy-inverse-text: #ffffff;

  /* Borders */
  --galaxy-border: #e2e8f0;
  --galaxy-border-focus: var(--galaxy-primary);

  /* Radius */
  --galaxy-radius-sm: 0.25rem;
  --galaxy-radius: 0.375rem;
  --galaxy-radius-lg: 0.5rem;
  --galaxy-radius-xl: 0.75rem;

  /* Density (spacing multiplier) */
  --galaxy-density: 1;

  /* Shadows */
  --galaxy-shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --galaxy-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
  --galaxy-shadow-lg: 0 4px 6px -1px rgb(0 0 0 / 0.1);

  /* Font */
  --galaxy-font-family: 'Inter', system-ui, -apple-system, sans-serif;
  --galaxy-font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --galaxy-font-size-xs: 0.75rem;
  --galaxy-font-size-sm: 0.875rem;
  --galaxy-font-size: 1rem;
  --galaxy-font-size-lg: 1.125rem;
  --galaxy-font-size-xl: 1.25rem;

  /* Transitions */
  --galaxy-transition: 150ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

### Dark Mode Overrides

```css
.dark {
  --galaxy-bg: #0f172a;
  --galaxy-surface: #1e293b;
  --galaxy-muted: #334155;
  --galaxy-text: #f1f5f9;
  --galaxy-muted-text: #94a3b8;
  --galaxy-border: #334155;
  --galaxy-shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
  --galaxy-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.4);
}
```

### Theme Metadata (DocType concept)

```python
# Conceptual DocType: Galaxy Theme

GALAXY_THEME_FIELDS = {
    "theme_name": "Data",
    "is_active": "Check",
    "mode": "Select",          # Light / Dark / System
    "primary_color": "Data",
    "accent_color": "Data",
    "success_color": "Data",
    "warning_color": "Data",
    "danger_color": "Data",
    "info_color": "Data",
    "background_color": "Data",
    "surface_color": "Data",
    "text_color": "Data",
    "muted_text_color": "Data",
    "border_color": "Data",
    "radius_scale": "Float",
    "density": "Select",       # Compact / Normal / Comfortable
    "font_family": "Data",
    "sidebar_style": "Select", # Icons / Icons+Labels / Collapsible
    "topbar_style": "Select",  # Fixed / Static / Compact
    "button_style": "Select",  # Solid / Outline / Ghost
    "card_style": "Select",    # Bordered / Elevated / Flat
    "table_style": "Select",   # Bordered / Striped / Minimal
    "form_style": "Select",    # Stacked / Inline / Floating
    "custom_css": "Code",
    "version": "Int",
}
```

```python
# Conceptual DocType: Galaxy Component Style

GALAXY_COMPONENT_STYLE_FIELDS = {
    "component_name": "Data",  # button, card, badge, ...
    "variant": "Data",         # solid, outline, ghost, ...
    "tone": "Data",            # primary, success, danger, ...
    "class_tokens": "Code",     # Tailwind classes
    "css_variables": "Code",    # Custom CSS variable overrides
    "is_default": "Check",
    "theme_name": "Link",
}
```

## 8. Component Variants/Flavors

### Button

| Variant | Visual | Usage |
|---------|--------|-------|
| `solid` | Filled background | Primary actions |
| `outline` | Border + transparent bg | Secondary actions |
| `ghost` | No border, subtle hover | Tertiary, toolbar |
| `soft` | Light background | Subtle emphasis |
| `destructive` | Red solid | Delete, irreversible |
| `link` | Text only | Navigation, inline |

| Parameter | Values |
|-----------|--------|
| `tone` | primary, neutral, success, warning, danger, info |
| `size` | xs, sm, md, lg, xl |
| `radius` | none, sm, md, lg, full |
| `density` | compact, normal, comfortable |
| `icon` | icon name from icon set |
| `icon_position` | left, right |
| `loading` | boolean (shows spinner) |
| `disabled` | boolean |

### Card

| Variant | Visual |
|---------|--------|
| `bordered` | Border + white bg |
| `elevated` | Shadow + white bg |
| `flat` | No border, no shadow |
| `interactive` | Hover effect, cursor pointer |

### Badge

| Variant | Use |
|---------|-----|
| `solid` | Status indicators |
| `soft` | Count/tag labels |
| `outline` | Subtle labels |
| `dot` | Minimal online/offline |

### Modal

| Variant | Behavior |
|---------|----------|
| `dialog` | Center screen, backdrop |
| `drawer` | Slides from right |
| `fullscreen` | Full overlay |
| `sheet` | Bottom sheet (mobile) |

## 9. Per-Component Styling Rules

1. Every component macro accepts `class` parameter for additional Tailwind classes.
2. Components never hardcode color values — always use `var(--galaxy-*)`.
3. Components use `cva()`-style variant mapping internally (a Jinja2 macro function).
4. Dark mode handled automatically via `.dark` class on parent.
5. Density affects padding, gap, font-size via `calc(var(--galaxy-density) * ...)`.

### Variant Mapping Pattern (Jinja2)

```jinja
{% macro button(label, variant="solid", tone="primary", size="md", ...) %}
{% set classes = button_variants(variant, tone, size) %}
<button class="{{ classes }} {{ class }}" {{ attrs | safe }}>
  {% if loading %}<span class="spinner"></span>{% endif %}
  {{ label }}
</button>
{% endmacro %}
```

```python
# galaxy/desk/components/variants.py

BUTTON_VARIANTS = {
    "solid": {
        "primary": "bg-[var(--galaxy-primary)] text-white hover:brightness-110",
        "danger":  "bg-[var(--galaxy-danger)] text-white hover:brightness-110",
        "neutral": "bg-[var(--galaxy-surface)] text-[var(--galaxy-text)] hover:bg-[var(--galaxy-muted)]",
    },
    "outline": {
        "primary": "border-[var(--galaxy-primary)] text-[var(--galaxy-primary)]",
        "danger":  "border-[var(--galaxy-danger)] text-[var(--galaxy-danger)]",
    },
    "ghost": {
        "primary": "text-[var(--galaxy-primary)] hover:bg-[var(--galaxy-primary)]/10",
    },
}
```

## 10. Desk Theme Manager

Admin UI page at `/desk/settings/theme`:

### Page Layout

```text
┌─────────────────────────────────────────────────────────────┐
│ Theme Manager                                   [Save] [↻] │
├──────────────────────────────┬──────────────────────────────┤
│ ┌─ Active Theme ──────────┐  │ ┌─ Live Preview ──────────┐ │
│ │ Theme: [Galaxy Default] │  │ │                         │ │
│ │ Mode:  [Light ▼]        │  │ │  [Button] [Button]     │ │
│ │                         │  │ │  ┌─ Card ─────────────┐ │ │
│ ├─ Brand Colors ──────────┤  │ │  │ Preview content    │ │ │
│ │ Primary:    [■] #2563eb │  │ │  └────────────────────┘ │ │
│ │ Accent:     [■] #8b5cf6 │  │ │  Badge [● Active]      │ │
│ │ Success:    [■] #16a34a │  │ │                         │ │
│ │ Warning:    [■] #d97706 │  │ └──────────────────────────┘ │
│ │ Danger:     [■] #dc2626 │  │                              │
│ │ Info:       [■] #0891b2 │  │                              │
│ ├─ Layout ────────────────┤  │                              │
│ │ Radius:    [━━━━●────]   │  │                              │
│ │ Density:   [Compact ▼]  │  │                              │
│ │ Font:      [Inter    ▼]  │  │                              │
│ ├─ Sidebar ───────────────┤  │                              │
│ │ Style: [Icons+Labels ▼] │  │                              │
│ └──────────────────────────┘  │                              │
└──────────────────────────────┴──────────────────────────────┘
```

### Features

- Choose active theme from saved themes
- Switch light/dark/system mode
- Change brand/accent color with color picker
- Adjust radius/density with slider/select
- Live preview updates as settings change
- Save theme to `tabGalaxy Theme`
- Export theme as JSON
- Import theme from JSON
- Reset to defaults
- Assign theme by site/user/role (future)

## 11. Runtime Theme Loading

### Request Flow

```
User request → RequireSessionMiddleware
  → resolve user preferences (theme_name, mode)
    → fallback to site config (default_theme)
      → fallback to "Galaxy Default" theme
        → load theme metadata from DB or cache
          → generate CSS variable string
            → inject into base layout <style> block
              → render page with component macros
```

### Theme Resolution

```python
def resolve_theme(request, user=None):
    theme_name = None
    if user:
        theme_name = user.get("theme_name")
    if not theme_name:
        site_theme = load_site_config().get("default_theme")
        theme_name = site_theme or "Galaxy Default"

    theme = get_theme(theme_name)  # from DB or cache
    mode = resolve_mode(request, theme)  # Light / Dark / System

    return {
        "css_vars": theme_to_css_vars(theme, mode),
        "mode": mode,
        "theme_name": theme_name,
    }
```

### CSS Variable Injection

```jinja
{# base.html #}
<style>
  :root {
    {% for name, value in theme.css_vars.items() %}
    --galaxy-{{ name }}: {{ value }};
    {% endfor %}
  }
  {% if theme.mode == "dark" %}
  .dark { /* dark overrides */ }
  {% endif %}
</style>
```

## 12. Developer Usage Examples

### Jinja2 Macro Usage

```jinja
{{ ui.button("Save", variant="solid", tone="primary", size="md") }}

{{ ui.button("Delete", variant="destructive", tone="danger", size="sm") }}

{{ ui.badge("Active", variant="solid", tone="success") }}

{{ ui.card("Customer Details", variant="elevated") }}
  {% include "desk/templates/customer_form.html" %}
{{ ui.endcard() }}

{{ ui.modal("Confirm Delete", variant="dialog") }}
  <p>Are you sure?</p>
  {{ ui.button("Yes, Delete", variant="destructive", tone="danger") }}
{{ ui.endmodal() }}
```

### HTMX Integration

```jinja
{# Server-triggered partial update #}
{{ ui.button("Save",
    hx_post="/api/resource/Customer/CP001",
    hx_target="#form-result",
    hx_swap="innerHTML",
    variant="solid",
    tone="primary"
) }}

{# Inline edit #}
<td hx-get="/desk/Customer/CP001/edit-field/name"
    hx-target="this"
    hx-swap="innerHTML"
    class="cursor-pointer hover:bg-[var(--galaxy-muted)]">
  {{ record.name }}
</td>
```

### Client Script Usage

```javascript
// galaxy.desk.js

// Toast notification
galaxy.ui.toast("Saved successfully", { tone: "success" });
galaxy.ui.toast("Network error", { tone: "danger", duration: 5000 });

// Confirmation dialog
galaxy.ui.confirm("Apply migration?", {
  confirmText: "Apply",
  tone: "warning",
  onConfirm: async () => {
    const res = await fetch("/api/migration/apply", { method: "POST" });
    galaxy.ui.toast("Migration applied", { tone: "success" });
  }
});

// Modal
galaxy.ui.modal("customer-form", { size: "lg" }).open();

// Command palette
galaxy.ui.commandPalette.open();

// Theme switcher
galaxy.ui.themeSwitcher.toggleMode();
```

### Theme from Client Script

```javascript
galaxy.ui.setTheme({
  primary: "#7c3aed",
  accent: "#ec4899",
  radius: 0.75,
});
```

## 13. Client Script Integration

Galaxy Desk exposes a global `galaxy` object to client scripts:

```javascript
window.galaxy = {
  ui: {
    toast,
    confirm,
    modal,
    drawer,
    commandPalette,
    themeSwitcher,
    setTheme,
    loading,
    notify,
  },
  utils: {
    formatDate,
    formatNumber,
    formatCurrency,
    stripHtml,
    truncate,
    debounce,
    fetchJson,
  },
  desk: {
    refresh,
    navigate,
    getFormData,
    setFormData,
    currentDoctype,
    currentRecord,
  },
};
```

Client scripts written by developers can use these APIs to extend Desk behavior without touching core templates.

## 14. HTMX Integration

### Patterns

| Pattern | HTMX Attribute | Behavior |
|---------|----------------|----------|
| Form submit | `hx-post`, `hx-target` | Submit form, update result region |
| Inline edit | `hx-get` on cell, `hx-put` on blur | Click to edit, save on blur |
| Lazy load | `hx-get`, `hx-trigger="load"` | Load content after page render |
| Infinite scroll | `hx-get`, `hx-trigger="revealed"` | Load more on scroll |
| Search as-you-type | `hx-get`, `hx-trigger="keyup delay:300ms"` | Search results update in real-time |
| Tab switching | `hx-get`, `hx-target="#tab-content"` | Load tab content on click |
| Modal content | `hx-get`, `hx-target="#modal-body"` | Load modal content dynamically |

### Example

```jinja
<div id="customer-list" hx-get="/desk/Customer/list?page=1" hx-trigger="load">
  {{ ui.empty_state("Loading customers...", loading=True) }}
</div>

{{ ui.button("Load More",
    hx_get="/desk/Customer/list?page=2",
    hx_target="#customer-list",
    hx_swap="beforeend",
    variant="ghost"
) }}
```

## 15. Vanilla JS Integration

Galaxy Desk uses vanilla JavaScript (no framework) for interactive elements:

```javascript
// galaxy/desk/static/js/galaxy.js

// Component initialization
document.addEventListener("DOMContentLoaded", () => {
  galaxy.initModals();       // data-modal attributes
  galaxy.initTooltips();     // data-tooltip attributes
  galaxy.initTabs();         // data-tab-group attributes
  galaxy.initDropdowns();    // data-dropdown attributes
  galaxy.initCommandPalette();
  galaxy.initThemeSwitcher();
});

// HTMX after-swap handler
document.body.addEventListener("htmx:afterSwap", (e) => {
  galaxy.initModals(e.detail.target);
  galaxy.initTooltips(e.detail.target);
});

// Reactive pattern (lightweight)
// galaxy.reactive creates a simple state → DOM binding
const state = galaxy.reactive({ count: 0 });
state.watch("count", (val) => {
  document.getElementById("counter").textContent = val;
});
```

## 16. Future Vue/React Generated-App Support

### Principle

Core Desk stays server-rendered (Jinja2 + HTMX). 

Generated app targets (for end-user-facing apps built on Galaxy) may use modern SPA frameworks:

| Target | Framework | When |
|--------|-----------|------|
| Admin/Desk UI | Jinja2 + HTMX | Always (core) |
| Customer portal | Vue 3 | Optional generated output |
| Mobile app | React Native | Optional generated output |
| Public website | Next.js | Optional generated output |
| Embedded widgets | Svelte | Optional generated output |

### Theme Token Consumption

Generated apps should consume the same theme tokens via:

```json
// GET /api/theme/active.json
{
  "css_vars": {
    "--galaxy-primary": "#2563eb",
    "--galaxy-radius": "0.375rem"
  },
  "mode": "light",
  "components": {
    "button": {
      "solid": {
        "primary": "bg-blue-600 text-white hover:bg-blue-700"
      }
    }
  }
}
```

This allows generated Vue/React apps to mirror the same visual design as Galaxy Desk without duplicating theme configuration.

## 17. Implementation Phases

### Phase 1 — Token Foundation
- Define CSS variables in `desk/static/css/tokens.css`
- Create Tailwind config that references CSS variables
- Build dark mode toggle
- Create ThemeSwitcher component

### Phase 2 — Core Components
- Build Button, Card, Badge, Alert, Toast as Jinja2 macros
- Create variant mapping system
- Build EmptyState, Breadcrumb, Sidebar, Topbar

### Phase 3 — Form Components
- Build FormField, TextInput, Select, Checkbox, DateInput
- Build form layout macro
- Create form validation display

### Phase 4 — Interactive Components
- Build Modal, Drawer, Tabs, ConfirmDialog
- Add HTMX integration patterns
- Build CommandPalette, DataGrid

### Phase 5 — Theme Manager
- Create Galaxy Theme + Galaxy Component Style DocTypes
- Build `/desk/settings/theme` admin page
- Implement runtime theme resolution
- Build theme export/import

### Phase 6 — Specialized Components
- Build MigrationPreview, PermissionMatrix
- Build Stepper (setup wizard)
- Build FileUpload, DataGrid advanced features

### Phase 7 — Generated App Bridge
- Create `/api/theme/active.json` endpoint
- Document theme token consumption for Vue/React targets
- Build reference theme consumer (simple Vue example)

## 18. Risks and Boundaries

| Risk | Mitigation |
|------|------------|
| Component system grows unmaintainable | Start with 10 core components. Add only when needed. |
| Tailwind JIT compilation slow in dev | Use Tailwind CLI watch mode. Cache compiled CSS. |
| CSS variable approach limits advanced styling | Per-component style overrides via Galaxy Component Style DocType. Custom CSS field for advanced cases. |
| HTMX not powerful enough for complex UI | Enhance with vanilla JS widgets for rich text, file upload, kanban. HTMX handles 90% of CRUD interactions. |
| Theme system adds DB query per request | Cache theme in Redis or in-process dictionary. Invalidate on theme save. |
| Jinja2 macros become slow with many components | Lazy-load component macros. Pre-compile commonly used macros. |
| Galaxy becomes too Frappe-like visually | Design tokens make complete visual rebranding possible. Galaxy Default theme is modern but can be fully customized. |

## Summary

Galaxy UI component system provides:

- A **formal theme/token system** with CSS variables
- **Consistent component variants** (variant, tone, size, density)
- **Server-rendered Jinja2 macros** as the primary component API
- **HTMX for interactivity** without a JS framework
- **Vanilla JS enhancement** for complex widgets
- **Theme Manager** for visual customization without code
- **Generated app bridge** for future Vue/React targets
- **Frappe-like productivity** with **modern visual customization**

The system is designed to be easier to customize than Frappe Desk while maintaining the same metadata-driven productivity that Frapple developers expect.