# 24 — UI Field Enhancement and Theme Rules

## 1. Purpose

Define the architecture for field-level visual styling, validation visual feedback, field layout strategies, and theme/flavor system for Galaxy Framework. Every field and component should be customizable through metadata-driven visual properties without modifying core templates.

## 2. Field-Level UI Properties

Each DocField supports an extended set of UI enhancement properties. These are stored as JSON in a `ui_config` column on DocField (and CustomField).

### UI Property Reference

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ui_variant` | Select | `standard` | standard / filled / flushed / bordered |
| `ui_size` | Select | `md` | xs / sm / md / lg / xl |
| `ui_tone` | Select | `neutral` | neutral / primary / success / warning / danger / info |
| `ui_width` | Data | `100%` | CSS width value |
| `ui_height` | Data | — | CSS height value (for textareas, code editors) |
| `ui_min_height` | Data | — | CSS min-height |
| `ui_max_height` | Data | — | CSS max-height |
| `ui_radius` | Data | — | Override field border-radius |
| `ui_shadow` | Data | — | CSS box-shadow value |
| `ui_background_color` | Data | — | Field background color (CSS value or var token) |
| `ui_text_color` | Data | — | Field text color |
| `ui_border_color` | Data | — | Field border color |
| `ui_focus_color` | Data | — | Field focus ring color |
| `ui_placeholder_color` | Data | — | Placeholder text color |
| `ui_icon` | Data | — | Icon name from icon provider |
| `ui_icon_position` | Select | `left` | left / right |
| `ui_help_text` | Text | — | Help text displayed below the field |
| `ui_tooltip` | Text | — | Tooltip shown on hover |
| `ui_prefix` | Data | — | Text/icon shown before the input |
| `ui_suffix` | Data | — | Text/icon shown after the input |
| `ui_badge` | Data | — | Badge label shown alongside the field |
| `ui_effect` | Select | `none` | none / shake / glow / fade / pulse |
| `ui_animation` | Data | — | Custom CSS animation name |
| `ui_density` | Select | `normal` | compact / normal / comfortable |
| `ui_column_span` | Int | 1 | Number of columns this field spans |
| `ui_card_group` | Data | — | Name of card group this field belongs to |
| `ui_section` | Data | — | Section name |
| `ui_tab` | Data | — | Tab name |
| `ui_order` | Int | 0 | Display order within section/tab |
| `ui_css_class` | Data | — | Additional CSS class names |
| `ui_style_tokens` | JSON | — | Arbitrary CSS property-value pairs |

### Field Variants

| Variant | Visual | Use Case |
|---------|--------|----------|
| `standard` | Bordered, white background, label above | Default form fields |
| `filled` | Light background, no border, subtle | Compact forms, inline editing |
| `flushed` | Bottom border only, transparent bg | Minimal forms, settings |
| `bordered` | Full border, rounded, shadow | Card-style fields, prominent inputs |

### UI Properties Resolution

```
1. Start with base DocField UI properties (or defaults)
2. Apply CustomField UI properties (if exists)
3. Apply Property Setter overrides for ui_* fields
4. Apply theme-level defaults (density, radius scale)
5. Apply validation state overrides (error/warning/success)
6. Final UI config is merged into RuntimeField
```

## 3. Validation Visual Effects

Validation rules should provide visual feedback on fields and forms.

### Visual Feedback States

| State | Border Color | Background | Icon | Helper Text |
|-------|-------------|------------|------|-------------|
| Error | `--galaxy-danger` | `--galaxy-danger-soft` | Alert circle | Red helper text |
| Warning | `--galaxy-warning` | `--galaxy-warning-soft` | Alert triangle | Amber helper text |
| Success | `--galaxy-success` | `--galaxy-success-soft` | Check circle | Green helper text |
| Info | `--galaxy-info` | `--galaxy-info-soft` | Info circle | Blue helper text |

### Validation UI Metadata

```json
{
  "error_border_color": "var(--galaxy-danger)",
  "warning_border_color": "var(--galaxy-warning)",
  "success_border_color": "var(--galaxy-success)",
  "error_background_color": "var(--galaxy-danger-soft)",
  "warning_background_color": "var(--galaxy-warning-soft)",
  "success_background_color": "var(--galaxy-success-soft)",
  "show_icon": true,
  "show_helper": true,
  "show_summary": false,
  "validation_effect": "border_highlight",
  "validation_position": "below_field"
}
```

### Validation Effect Types

| Effect | Behavior |
|--------|----------|
| `border_highlight` | Field border changes color |
| `background_tint` | Field background gets soft color |
| `icon_indicator` | Icon appears inside the field |
| `helper_text` | Helper text appears below |
| `shake` | Field shakes (only if theme allows) |
| `summary_panel` | Summary panel at top of form lists all errors |
| `toast` | Toast notification with error message |
| `side_accent` | Colored left border accent on the field |

### Validation Position

| Position | Behavior |
|----------|----------|
| `below_field` | Helper text directly below the field |
| `tooltip` | Error shown as tooltip on hover |
| `side` | Error shown to the right of the field |
| `summary_only` | Error only shown in summary panel |

## 4. Field Layout System

Fields can be arranged in multiple layout modes controlled by metadata.

### Layout Types

| Type | Description |
|------|-------------|
| `single_column` | Fields stacked vertically, one per row |
| `two_columns` | Two fields per row |
| `three_columns` | Three fields per row |
| `responsive` | Column count adjusts to viewport width |
| `sections` | Grouped into named sections with headings |
| `cards` | Each group rendered as a card |
| `tabs` | Groups rendered as tab panels |
| `accordion` | Collapsible sections |
| `drawers` | Fields in side drawers |
| `side_panel` | Main form + side panel with additional fields |
| `compact` | Dense single-column layout |
| `full_page` | Full-width fields with minimal chrome |
| `wizard` | Multi-step stepper form |
| `child_table_grid` | Inline editable table |

### Field Layout Metadata

| Property | Type | Description |
|----------|------|-------------|
| `layout_type` | Select | The layout mode |
| `column_count` | Int | Number of columns (1-4) |
| `column_span` | Int | How many columns a field spans |
| `row_span` | Int | How many rows a field spans |
| `card_name` | Data | Card group identifier |
| `section_name` | Data | Section name |
| `tab_name` | Data | Tab name |
| `group_name` | Data | Logical group name |
| `collapsible` | Check | Section is collapsible |
| `collapsed_by_default` | Check | Section starts collapsed |
| `sticky` | Check | Section header sticks on scroll |
| `full_width` | Check | Field takes full row width |
| `mobile_behavior` | Select | `stack` / `scroll` / `hide` |

## 5. Theme / Flavor System

Galaxy supports multiple UI themes (flavors) switchable from Desk without code changes.

### Galaxy Theme DocType (conceptual)

| Field | Type | Description |
|-------|------|-------------|
| `theme_name` | Data | Unique theme name |
| `version` | Int | Theme version |
| `mode` | Select | `light` / `dark` / `system` |
| `primary_color` | Data | CSS color value |
| `accent_color` | Data | CSS color value |
| `success_color` | Data | CSS color value |
| `warning_color` | Data | CSS color value |
| `danger_color` | Data | CSS color value |
| `info_color` | Data | CSS color value |
| `background_color` | Data | Page background |
| `surface_color` | Data | Card/surface background |
| `field_background_color` | Data | Input field background |
| `field_text_color` | Data | Input field text |
| `field_border_color` | Data | Input field border |
| `field_focus_color` | Data | Input focus ring |
| `validation_error_color` | Data | Validation error indicator |
| `validation_warning_color` | Data | Validation warning indicator |
| `validation_success_color` | Data | Validation success indicator |
| `border_radius` | Data | Base border-radius |
| `field_radius` | Data | Field border-radius |
| `card_radius` | Data | Card border-radius |
| `button_radius` | Data | Button border-radius |
| `density` | Select | `compact` / `normal` / `comfortable` |
| `font_family` | Data | Base font |
| `heading_font_family` | Data | Heading font |
| `mono_font_family` | Data | Monospace font |
| `direction` | Select | `ltr` / `rtl` / `auto` |
| `custom_css` | Code | Extra CSS rules |
| `enabled` | Check | Theme is available for use |
| `is_default` | Check | Default theme for new users |

### CSS Variable Mapping

Theme colors map to CSS variables as follows:

```
--galaxy-primary           → primary_color
--galaxy-accent            → accent_color
--galaxy-success           → success_color
--galaxy-warning           → warning_color
--galaxy-danger            → danger_color
--galaxy-info              → info_color
--galaxy-bg                → background_color
--galaxy-surface           → surface_color
--galaxy-field-bg          → field_background_color
--galaxy-field-text        → field_text_color
--galaxy-field-border      → field_border_color
--galaxy-field-focus       → field_focus_color
--galaxy-error             → validation_error_color
--galaxy-warning-soft      → warning_color at lower opacity
--galaxy-success-soft      → success_color at lower opacity
--galaxy-radius            → border_radius
--galaxy-field-radius      → field_radius
--galaxy-card-radius       → card_radius
--galaxy-density           → density (numeric scale factor)
--galaxy-font              → font_family
--galaxy-heading-font      → heading_font_family
--galaxy-mono-font         → mono_font_family
--galaxy-direction         → direction
```

### Theme Resolution Order

```
1. User preference (stored in User doctype: theme_name + mode)
2. Site default theme (from site_config.json: default_theme)
3. Fallback to "Galaxy Default" theme
4. Load theme metadata from DB or cache
5. Generate CSS variable string from theme colors
6. Inject into page <head> as <style> block
7. Apply mode overrides (dark/system)
```

## 6. Light Green Theme Example

A seed theme to demonstrate the flavor system.

```
Theme Name: Galaxy Light Green
Mode: Light
Primary: #16a34a
Accent: #059669
Success: #16a34a
Warning: #d97706
Danger: #dc2626
Info: #0284c7
Background: #f0fdf4
Surface: #ffffff
Field Background: #f7fef9
Field Border: #dcfce7
Field Focus: #16a34a
Border Radius: 0.5rem
Density: normal
Font: Inter, system-ui
Direction: ltr
```

Dark mode variant automatically derived by inverting background/surface and adjusting color saturation.

## 7. Tailwind Strategy

Galaxy uses Tailwind CSS as the utility framework for styling components.

### CSS Variable References in Tailwind

```css
/* tailwind.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --galaxy-primary: #2563eb;
    --galaxy-bg: #ffffff;
    /* ... all variables */
  }
}

@layer components {
  .galaxy-input {
    @apply border rounded px-3 py-2;
    border-color: var(--galaxy-field-border);
    background-color: var(--galaxy-field-bg);
    color: var(--galaxy-field-text);
  }
  .galaxy-input:focus {
    border-color: var(--galaxy-field-focus);
    box-shadow: 0 0 0 2px var(--galaxy-field-focus);
  }
}
```

### Tailwind Config

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: 'var(--galaxy-primary)',
        surface: 'var(--galaxy-surface)',
        muted: 'var(--galaxy-muted)',
      },
      borderRadius: {
        field: 'var(--galaxy-field-radius)',
        card: 'var(--galaxy-card-radius)',
      },
      fontFamily: {
        sans: ['var(--galaxy-font)'],
        mono: ['var(--galaxy-mono-font)'],
      },
    },
  },
}
```

### Class Conventions

- Component classes use `galaxy-` prefix: `galaxy-input`, `galaxy-btn`, `galaxy-card`
- Utility overrides via `class` parameter on macros
- Validation states via `is-error`, `is-warning`, `is-success` classes
- Density via `density-compact`, `density-normal`, `density-comfortable`

## 8. Vanilla JS Enhancement Strategy

Galaxy enhances form field behavior with vanilla JavaScript.

### Field Enhancement Hooks

| Hook | Trigger | Behavior |
|------|---------|----------|
| `initField(el)` | DOMContentLoaded + HTMX afterSwap | Initialize field UI, tooltips, icons |
| `validateField(el)` | On blur + on input | Run client-side validation, show feedback |
| `toggleField(el, show)` | Dependency change | Show/hide field with animation |
| `disableField(el, disabled)` | Dependency change | Enable/disable field |
| `setFieldValue(el, val)` | Expression result | Set computed field value |
| `refreshOptions(el)` | Dynamic source change | Reload select/autocomplete options |
| `applyMask(el)` | On render | Apply data mask to field value |
| `revealMask(el)` | User action | Temporarily show masked value |

### Client Script Field API

```javascript
// In a client script
galaxy.form.on("Customer", {
  refresh(form) {
    // Style a field
    form.field("email").ui({
      icon: "mail",
      variant: "filled",
      tone: "primary",
    });

    // Set validation visual
    form.field("phone").setValidation("error", "Phone is required");

    // Toggle field group
    form.group("address").toggle(customer_type === "Company");
  }
});
```

### Reactive Field State

```javascript
// galaxy.desk.js internal
class GalaxyField {
  constructor(el, options) {
    this.el = el;
    this.state = { value: null, error: null, visible: true, enabled: true };
    this.options = options;
    this.init();
  }

  setError(msg) {
    this.state.error = msg;
    this.el.classList.add("is-error");
    this.el.querySelector(".field-helper").textContent = msg;
  }

  clearError() {
    this.state.error = null;
    this.el.classList.remove("is-error", "is-warning", "is-success");
  }

  setValidation(tone, msg) {
    this.clearError();
    this.el.classList.add(`is-${tone}`);
    if (msg) this.el.querySelector(".field-helper").textContent = msg;
  }
}
```

## 9. Theme Switching Flow

```
Desk UI → User clicks theme switcher
  → galaxy.ui.themeSwitcher.toggleMode()
    → POST /api/theme/switch { theme_name, mode }
      → Server saves user preference
        → Returns updated CSS variable JSON
          → JS updates :root style properties
            → All components re-theme instantly
```

## 10. Theme Manager Page

Admin page at `/desk/settings/themes`:

- List all themes with preview thumbnails
- Create new theme (clone from existing)
- Edit theme colors with color pickers
- Set theme as default
- Assign theme to site / role / user (future)
- Export theme as JSON
- Import theme from JSON
- Live preview while editing

## 11. Implementation Phases

### Phase 1
- Define UI property metadata schema
- Create CSS variable theme system
- Build field variant rendering

### Phase 2
- Validation visual feedback engine
- Field layout system (sections, tabs, cards)
- Responsive column layouts

### Phase 3
- Theme DocType and CRUD
- Theme Manager admin page
- Theme resolution middleware

### Phase 4
- Light Green and other seed themes
- Theme import/export
- Theme assignment by site/role/user

### Phase 5
- Vanilla JS field enhancement hooks
- Client script field API
- Reactive field state system
