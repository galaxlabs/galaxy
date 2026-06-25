# 17 — Modern Desk UX Specification

## Product Identity

| Property    | Value                          |
|-------------|--------------------------------|
| Product     | Galaxy Framework               |
| Company     | Galaxy Labs                    |
| CLI         | `galaxy`                       |
| Admin UI    | Galaxy Desk                    |
| Builder UI  | Galaxy Studio                  |
| Cloud UI    | Galaxy Cloud / Bench Manager   |

## Design Principles

1. **Metadata-first** — Every UI element should be driven by DocType metadata where possible.
2. **Operations-focused** — Default UI is an operations dashboard, not a workspace.
3. **Accessible** — WCAG 2.1 AA minimum, keyboard-navigable, screen-reader friendly.
4. **Responsive** — Desktop-first but functional on tablet/mobile.
5. **Progressive enhancement** — Core functionality works without JavaScript; JS enhances experience.
6. **Consistent** — Component library ensures visual and behavioral consistency.
7. **Safe** — Every destructive action requires confirmation; undo where possible.

## Default Navigation

### Galaxy Desk

```
┌─────────────────────────────────────────────────────────┐
│ [☰] Galaxy Desk              [🔍] [⚡] [🔔] [👤]      │
├──────────────┬──────────────────────────────────────────┤
│ Home         │  [Main content area]                     │
│ Operations   │                                          │
│ Builder      │                                          │
│ Records      │                                          │
│ Reports      │                                          │
│ Automations  │                                          │
│ Files        │                                          │
│ Users & Roles│                                          │
│ Settings     │                                          │
│ Developer    │                                          │
│ Bench Manager│                                          │
└──────────────┴──────────────────────────────────────────┘
```

### Galaxy Studio (Builder)

```
┌─────────────────────────────────────────────────────────┐
│ [☰] Galaxy Studio           [🔍] [⚡] [🔔] [👤]       │
├──────────────┬──────────────────────────────────────────┤
│ Apps         │  [Main content area]                     │
│ Modules      │                                          │
│ DocTypes     │                                          │
│ Fields       │                                          │
│ Permissions  │                                          │
│ Migration    │                                          │
│ Feature Packs│                                          │
│ API Preview  │                                          │
│ UI Preview   │                                          │
└──────────────┴──────────────────────────────────────────┘
```

## Component Library

All components live in `galaxy/desk/components/` and use Jinja2 macros + vanilla JS + CSS.

### Core Components

| Component        | Purpose                              | States                                    |
|------------------|--------------------------------------|-------------------------------------------|
| Button           | Primary, secondary, danger, ghost     | Default, hover, active, disabled, loading |
| Card             | Content container                     | Default, hover, selected, skeleton        |
| Badge            | Status/label indicator                | Info, success, warning, danger, neutral   |
| Modal            | Dialog overlay                        | Open, closing, nested                     |
| Drawer           | Side panel                            | Open, closing, fullscreen                 |
| Tabs             | Tabbed content                        | Active, inactive, badge, count            |
| Table            | Data table                            | Sortable, filterable, paginated, empty    |
| DataList         | List view for records                 | Loading, empty, selected, bulk action     |
| FormField        | Single form input with label/errors   | Default, focused, error, disabled, help   |
| Select           | Dropdown selector                     | Options, searchable, multi-select         |
| Checkbox         | Boolean input                         | Checked, unchecked, indeterminate         |
| DateInput        | Date picker                           | Date range, time, datetime                |
| Toast            | Notification popup                    | Success, error, info, warning             |
| Alert            | Inline banner message                 | Success, error, info, warning             |
| EmptyState       | No-data placeholder                   | Icon, message, action button              |
| ConfirmDialog    | Destructive action confirmation       | Text input verification, cancel button    |
| CommandPalette   | Keyboard command search               | Open, searching, selected                 |
| Sidebar          | Left navigation                       | Collapsed, expanded, active item          |
| Topbar           | Header bar                            | Breadcrumbs, search, actions, profile     |
| Breadcrumb       | Current location path                 | Clickable segments                        |
| Stepper          | Multi-step process indicator          | Complete, active, pending, error          |
| SetupWizard      | Guided first-run experience           | Step-by-step, skip, validate              |
| MigrationPreview | Schema change review                  | Added/removed/changed rows, confirm       |
| PermissionMatrix | Role-permission grid editor           | Checkboxes, bulk set, inherit             |

## Page Types

### Dashboard Page

```
┌─────────────────────────────────────────────────────────┐
│ Home                                      [Last 24h] [↻]│
├─────────────────────────────────────────────────────────┤
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                    │
│ │Users │ │Docs  │ │Today │ │Alerts│                    │
│ │  42  │ │ 1,230│ │  17  │ │   3  │                    │
│ └──────┘ └──────┘ └──────┘ └──────┘                    │
│                                                         │
│ ┌──────────────────────────────────────────────────┐   │
│ │ Recent Activity                    [View all →]   │   │
│ │ • User X created Invoice-0012       2m ago        │   │
│ │ • DocType Customer was updated      15m ago       │   │
│ │ • Backup completed                   1h ago        │   │
│ └──────────────────────────────────────────────────┘   │
│                                                         │
│ ┌──────────────────────────────────────────────────┐   │
│ │ Migration Queue                      [Review →]   │   │
│ │ 3 pending migrations                 1 critical   │   │
│ └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### List View

```
┌─────────────────────────────────────────────────────────┐
│ Customers                          [+ New] [⚙] [🔍]   │
├──────────┬──────────┬────────────┬──────────────────────┤
│ [☐] Name │ City     │ Status     │ Created              │
├──────────┼──────────┼────────────┼──────────────────────┤
│ [☐] Acme │ New York │ Active     │ 2026-06-01           │
│ [☐] Beta │ Chicago  │ Active     │ 2026-06-02           │
│ [☐] Gamma│ Boston   │ Disabled   │ 2026-05-15           │
├──────────┴──────────┴────────────┴──────────────────────┤
│ [← Prev]  1 - 3 of 12  [Next →]  [□ Select all]        │
└─────────────────────────────────────────────────────────┘
```

### Form View

```
┌─────────────────────────────────────────────────────────┐
│ Customer: Acme Corp                   [Save] [✕ Cancel] │
├─────────────────────────────────────────────────────────┤
│ ┌─ General ───────────────────────────────────────────┐ │
│ │ Name:     [Acme Corp                     ]          │ │
│ │ City:     [New York                      ]          │ │
│ │ Status:   [Active ▼]                               │ │
│ │ Email:    [contact@acme.com              ]          │ │
│ └──────────────────────────────────────────────────────┘ │
│ ┌─ Address ───────────────────────────────────────────┐ │
│ │ Street:   [123 Main St                    ]          │ │
│ │ Zip:      [10001                          ]          │ │
│ └──────────────────────────────────────────────────────┘ │
│ ┌─ Contacts ──────────────────────────────────────────┐ │
│ │ [+ Add Row]                                         │ │
│ │ Name            │ Email               │ Phone        │ │
│ │ John            │ john@acme.com       │ +1-555-0100  │ │
│ └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## UX Patterns

| Pattern              | Behavior                                                    |
|----------------------|-------------------------------------------------------------|
| **Command palette**  | `Ctrl+K` opens quick search for pages, records, actions     |
| **Global search**    | Search across all DocTypes, returns results grouped by type |
| **Bulk actions**     | Select rows → action bar appears (delete, export, assign)   |
| **Inline editing**   | Click cell in list view → inline edit, Enter to save        |
| **Quick create**     | `Ctrl+N` opens quick create form for current DocType        |
| **Side panel**       | Drawer for related records, activity log, metadata          |
| **Toast confirm**    | Action triggers toast: "Saved" / "Deleted" / "Error: ..."   |
| **Loading skeleton** | Content loads with skeleton placeholders, not spinners      |
| **Empty state**      | No records → illustration + "Create your first [doctype]"   |
| **Dirty form**       | Unsaved changes → prompt before navigate away               |
| **Auto-save**        | Form auto-saves after 3s of inactivity (configurable)       |
| **Dark mode**        | Toggle via settings or `Ctrl+Shift+D`                       |

## Implementation Approach

### Phase 1 — Static Shell (Current)
- Jinja2 templates, basic CSS, vanilla JS.
- Login, desk shell, list/form views, builder.

### Phase 2 — Component Library
- Build component macros in `galaxy/desk/components/`.
- Style guide page for development reference.

### Phase 3 — HTMX Integration
- Replace full-page reloads with HTMX for partial updates.
- Form validation via HTMX + server-side validation.

### Phase 4 — Enhanced UX
- Command palette with JavaScript.
- Drawer panels for related data.
- Toast notifications via server-sent events.
- Skeleton loading states.

### Phase 5 — Optional SPA
- Separate React/Vue target for Galaxy-generated apps.
- Core Desk remains Jinja2/HTMX.