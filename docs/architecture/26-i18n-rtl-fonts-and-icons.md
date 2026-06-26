# 26 — Internationalization, RTL, Fonts, and Icons

## 1. Purpose

Define the architecture for multilingual UI support, right-to-left layout, font management, and the icon provider system in Galaxy Framework. These features must work from day one and support English, Urdu, Arabic, and future languages.

## 2. Internationalization Architecture

### Translation Model

Translations are stored in key-value pairs with language scope.

```
tabTranslation:
  name             Data (PK)
  source_text      Text (the original text in the base language)
  translated_text  Text (the translated text)
  language         Data (e.g. "ur", "ar", "fr")
  doctype          Data (optional — scope to a specific DocType)
  fieldname        Data (optional — scope to a specific field)
  context          Data (optional — disambiguation context)
  updated_at       Datetime
  updated_by       Link (User)
```

### Language Model

```
tabLanguage:
  name             Data (PK) — e.g. "ur", "ar", "en"
  language_name    Data — e.g. "Urdu", "Arabic"
  native_name      Data — e.g. "اردو", "العربية"
  direction        Select — "ltr" / "rtl"
  fallback_language Data — e.g. "en"
  is_active        Check
  is_default       Check
  date_format      Data — e.g. "dd/mm/yyyy"
  time_format      Data — e.g. "HH:mm"
  number_format    Data — e.g. "#,##0.00"
  currency_format  Data — e.g. "¤#,##0.00"
  first_day_of_week Int — 0=Sunday, 1=Monday
  font_family      Data — preferred font for this language
  enabled          Check
```

### Translation Resolution

```
1. Check user's preferred language (from User doctype)
2. Fallback to site default language (site_config.json: default_language)
3. Fallback to "en" (English)
4. For each translatable string:
   a. Look up translation by (source_text, language, doctype, fieldname)
   b. If not found, look up by (source_text, language)
   c. If not found, fallback to source_text (untranslated)
   d. If source_text is also empty, show fieldname as last resort
```

### Translatable Content

All user-facing strings should support translation:

- DocType labels and descriptions
- Field labels, help text, placeholder text
- Validation error messages
- Button labels, menu items, action labels
- Report names and column labels
- System messages and notifications
- Email templates
- DocType Web View content
- Custom translations via Translation DocType

### Translation Workflow

```
1. Developer/Admin adds translations via Desk UI or CSV import
2. Translation records are stored in tabTranslation
3. Translations are cached per language (in-memory dict, TTL configurable)
4. Cache invalidated when translations are added/updated
5. Missing translations are logged for admin review
6. Export untranslated strings for external translation tools
```

## 3. RTL Support

### Direction Control

- Each language has a `direction` property (ltr / rtl).
- The `<html>` element gets `dir="rtl"` when an RTL language is active.
- A `.rtl` CSS class is added to `<body>` for RTL-specific overrides.

### CSS Strategy

Use logical CSS properties where possible:

```css
/* Instead of: */
margin-left: 8px;
padding-right: 12px;
border-left: 1px solid;

/* Use: */
margin-inline-start: 8px;
padding-inline-end: 12px;
border-inline-start: 1px solid;
```

For properties where logical equivalents are not available, use the `.rtl` class:

```css
.rtl .sidebar { right: 0; left: auto; }
.rtl .topbar-title { text-align: right; }
.rtl .galaxy-table th { text-align: right; }
```

### RTL Checklist

| Component | RTL Behavior |
|-----------|-------------|
| Sidebar | Switches to right side, icons mirror |
| Topbar | Title right-aligned, actions reversed |
| Form labels | Right-aligned, colon on left side |
| Data tables | Columns reversed, text right-aligned |
| Modals | Close button on left side |
| Drawers | Slide from left instead of right |
| Command palette | Text right-aligned |
| Dropdown menus | Open direction reversed |
| Pagination | Previous/next buttons reversed |
| Buttons with icons | Icon on right side of text |
| Breadcrumbs | Separator direction reversed |
| Toast notifications | Slide in from left |
| Tree/accordion | Expand indicator on left |

### Icons in RTL

Icons that imply direction should be mirrored in RTL mode:

- Arrow icons: `arrow-left` ↔ `arrow-right`
- Chevron icons: `chevron-left` ↔ `chevron-right`
- Caret icons: `caret-left` ↔ `caret-right`
- Back/forward navigation icons
- Previous/next pagination icons

Mirroring is handled via CSS transform:

```css
.rtl .icon-directional {
  transform: scaleX(-1);
}
```

Icons that should NOT be mirrored: logos, status icons, warning icons, social media icons.

## 4. Urdu / Arabic Support

### Urdu-Specific Requirements

- Primary font: Noto Nastaliq Urdu (Google Fonts, open source)
- Fallback font: Noto Naskh Arabic
- Urdu uses the Nastaliq script (different from Naskh used for Arabic)
- Numbers in Urdu are in Eastern Arabic-Indic digits (۰۱۲۳۴۵۶۷۸۹)
- Date formatting follows Urdu conventions: `DD MMMM YYYY` (e.g. ۲۵ جون ۲۰۲۶)
- RTL layout required
- @mentions must work with Urdu names (space-separated, RTL text)

### Arabic-Specific Requirements

- Primary font: Noto Naskh Arabic (Google Fonts, open source)
- Alternative fonts: Cairo, Tajawal, Amiri (all open source)
- Arabic uses the Naskh script
- Numbers can be either Eastern or Western digits (configurable)
- Date formatting follows Arabic conventions
- RTL layout required
- @mentions must work with Arabic names

### Font Loading Strategy

```
1. Each language has a preferred font_family in the Language model
2. On language switch:
   a. Check if font is already loaded (cached)
   b. If not loaded, fetch from CDN or local asset
   c. Inject @font-face or <link> into page <head>
   d. Update --galaxy-font and --galaxy-heading-font CSS variables
3. Fonts are cached in the browser for subsequent page loads
4. Custom fonts can be uploaded via Desk UI (stored in files directory)
```

## 5. Font Management

### Font Metadata (Galaxy Font DocType)

| Field | Type | Description |
|-------|------|-------------|
| `font_name` | Data | Display name (e.g. "Inter", "Noto Nastaliq Urdu") |
| `language` | Link | Target language (empty = all languages) |
| `font_family` | Data | CSS font-family value (e.g. "Inter", system-ui) |
| `source_type` | Select | `system` / `local_asset` / `cdn` |
| `source_url` | Data | URL to font file or CDN stylesheet |
| `font_weights` | JSON | Available weights (e.g. ["300", "400", "500", "600", "700"]) |
| `is_default` | Check | Default font for its language |
| `enabled` | Check | Font is available for use |

### Recommended Font Families

| Language | Primary Font | Fallback | License |
|----------|-------------|----------|---------|
| English | Inter | system-ui, -apple-system, sans-serif | OFL (open source) |
| English | Source Sans 3 | system-ui, sans-serif | OFL |
| English | Roboto | system-ui, sans-serif | Apache 2.0 |
| Urdu | Noto Nastaliq Urdu | Noto Naskh Arabic, sans-serif | OFL |
| Arabic | Noto Naskh Arabic | Tajawal, sans-serif | OFL |
| Arabic | Cairo | sans-serif | OFL |
| Arabic | Tajawal | sans-serif | OFL |
| Arabic | Amiri | serif | OFL |
| Any | system-ui | — | Built-in to OS |

### Font Loading Rules

- Do NOT ship proprietary fonts without a license.
- All fonts listed above are open source (SIL OFL, Apache 2.0, or similar).
- Fonts can be loaded from Google Fonts CDN or self-hosted.
- Custom font upload/configuration is supported via Desk UI.
- Font loading must not block page rendering (use `font-display: swap`).

## 6. Icon Provider System

### Architecture

Galaxy supports multiple icon providers through an adapter layer. Icons are never hardcoded to a single library.

```
Client Script / Template
        │
        ▼
   Icon Adapter Layer
        │
        ├──→ Lucide Icons Provider
        ├──→ Heroicons Provider
        ├──→ Tabler Icons Provider
        ├──→ Material Icons Provider
        ├──→ Phosphor Icons Provider
        └──→ Remix Icons Provider
```

### Icon Metadata

```json
{
  "icon_provider": "lucide",
  "icon_name": "user",
  "icon_variant": "outline",
  "icon_size": 20,
  "icon_color_token": "--galaxy-text",
  "icon_position": "left"
}
```

### Icon Provider Interface

```python
# galaxy/icons/providers/base.py

class IconProvider:
    provider_name: str

    def render(self, name: str, variant: str = "outline",
               size: int = 20, color: str = "currentColor") -> str:
        """Return HTML string for the icon."""
        raise NotImplementedError

    def available_icons(self) -> list[str]:
        """Return list of available icon names."""
        raise NotImplementedError

    def supports_variant(self, name: str, variant: str) -> bool:
        """Check if a variant is available for this icon."""
        raise NotImplementedError
```

### Provider Registration

```python
# galaxy/icons/registry.py

_icon_providers: dict[str, type[IconProvider]] = {}

def register_provider(provider: type[IconProvider]):
    _icon_providers[provider.provider_name] = provider

def get_provider(name: str) -> IconProvider:
    provider_cls = _icon_providers.get(name)
    if not provider_cls:
        raise ValueError(f"Icon provider '{name}' not registered")
    return provider_cls()

def render_icon(icon_meta: dict) -> str:
    provider = get_provider(icon_meta["icon_provider"])
    return provider.render(
        name=icon_meta["icon_name"],
        variant=icon_meta.get("icon_variant", "outline"),
        size=icon_meta.get("icon_size", 20),
        color=icon_meta.get("icon_color", "currentColor"),
    )
```

### Jinja2 Integration

```jinja
{{ ui.icon("user", provider="lucide", size=16) }}
{{ ui.icon("document-text", provider="heroicons", variant="solid") }}
{{ ui.icon("dashboard", provider="material", size=24) }}

{# From field metadata #}
{{ ui.field_icon(field) }}

{# With color token #}
{{ ui.icon("settings", color="var(--galaxy-primary)") }}
```

### Supported Icon Libraries

| Provider | Icons | License | Default Variant |
|----------|-------|---------|-----------------|
| Lucide | ~1400 | ISC | outline |
| Heroicons | ~800 | MIT | outline / solid |
| Tabler | ~5000 | MIT | outline / filled |
| Material Symbols | ~3000 | Apache 2.0 | outlined / rounded / sharp |
| Phosphor | ~9000 | MIT | regular / bold / fill |
| Remix | ~2900 | Apache 2.0 | line / fill |

### Icon Selection Rules

- The adapter layer allows switching providers without changing template code.
- Each DocField `ui_icon` property stores an icon name (provider-agnostic) when possible.
- Provider-agnostic icons use a universal name that maps to each provider's equivalent.
- Example mappings: `"user"` → Lucide `user`, Heroicons `user`, Material `person`, Tabler `user`.
- If a provider-agnostic name is not found, fall back to displaying by field type or first letter of label.
- NEVER use emoji, random unicode symbols, or plain letters as icons.
- The Desk UI defaults to Lucide icons (lightweight, consistent, MIT-licensed).
- Icon preference is configurable per site.

### Universal Icon Name Mapping (Partial)

| Universal Name | Lucide | Heroicons | Material | Tabler |
|--------------|--------|-----------|----------|--------|
| user | user | user | person | user |
| settings | settings | cog | settings | settings |
| dashboard | layout-dashboard | rectangle-stack | dashboard | dashboard |
| document | file-text | document-text | description | file-text |
| save | save | arrow-down-tray | save | device-floppy |
| delete | trash-2 | trash | delete | trash |
| add | plus | plus | add | plus |
| search | search | magnifying-glass | search | search |
| close | x | x-mark | close | x |
| menu | menu | bars | menu | menu-2 |

## 7. No Symbol/Emoji Icons Rule

Galaxy Desk must NEVER use:
- Plain letters inside circles as icon placeholders (e.g. "A" in user avatar)
- Emoji as icons (e.g. "🔍" for search, "⚙️" for settings)
- Random unicode symbols for UI controls

Instead, always use:
- An icon from a registered provider via the icon adapter
- For user avatars, generate initials with proper styling (background, text, no icon)
- For empty states, use a relevant icon from the provider
- For loading states, use a CSS spinner (not an emoji hourglass)

Exception: User avatars may show initials as text (e.g. "AQ" for Abdul Quddos) because initials are meaningful content, not a placeholder icon.

## 8. Icon in Components

Every component that displays an icon should accept icon metadata:

```jinja
{# Button with icon #}
{{ ui.button("Save",
    icon={"provider": "lucide", "name": "save", "size": 16},
    icon_position="left",
    variant="solid",
    tone="primary"
) }}

{# Empty state with icon #}
{{ ui.empty_state(
    "No customers found",
    icon={"provider": "lucide", "name": "users"},
    action={"label": "Add Customer", "url": "/desk/resource/Customer/new"}
) }}

{# Badge with icon #}
{{ ui.badge("Active",
    icon={"provider": "lucide", "name": "check-circle", "size": 12},
    variant="solid",
    tone="success"
) }}
```

## 9. Portal Language, RTL, and Icons

Portal UI has its own i18n, RTL, and icon strategy, separate from Desk.

### Portal language switching

Portal users can set their language preference independent of the system language. The portal resolves language in this order:

1. Portal user's `language` field on `tabPortalUser`
2. Portal default language (set in Portal metadata)
3. Browser `Accept-Language` header
4. System default language

Portal translations use the same `tabTranslation` table as Desk, scoped by context. Portal-specific translation keys use the `portal` context prefix.

### Portal RTL layout

Portal supports RTL layout independent from Desk. When the user's language is RTL (Urdu, Arabic, etc.):

- The `<html>` `dir` attribute is set to `rtl`
- `--portal-*` CSS variables adjust spacing and alignment directionally
- Portal components use logical CSS properties (`margin-inline-start`, `padding-inline-end`)
- Portal navigation reverses order (sidebar on the right)
- Portal form fields mirror layout
- Portal dashboard grid reverses

The portal RTL system is a subset of the Desk RTL system (see §5–6) but applied to `--portal-*` CSS variables and portal components.

### Portal icon strategy

Portal reuses the same icon provider system as Desk (see §4). The default portal icon provider is also Lucide. Portal components accept icon metadata in the same format:

```jinja
{{ portal.icon("user", size=20) }}
{{ portal.button("Profile", icon={"provider": "lucide", "name": "user"}) }}
```

Portal can optionally use a different icon provider than Desk (e.g., Desk uses Lucide, Portal uses Heroicons). This is configured per Portal metadata.

The same universal icon name mapping (see §6.3) applies to portal icons.

## 10. Accessibility Rules

| Rule | Description |
|------|-------------|
| Icons have aria-hidden | Decorative icons use `aria-hidden="true"` |
| Meaningful icons have labels | Icons that convey meaning have `aria-label` |
| Font sizes respect user preference | Use relative units (rem), not fixed px for text |
| RTL does not break keyboard navigation | Arrow keys reverse in RTL mode |
| Color is not the only indicator | Validation uses icon + text + color |
| Focus indicators respect theme | Focus ring uses theme focus color |
| Language switch persists | User language preference is stored and respected across sessions |
| Font loading has fallback | `font-display: swap` and system font fallback |

## 10. Implementation Phases

### Phase 1
- Translation model and storage
- Language model
- Basic translation resolution (key-value lookup)
- Language switcher UI

### Phase 2
- RTL CSS strategy (logical properties)
- RTL layout adjustments for all core components
- Direction-aware icons

### Phase 3
- Font metadata and font loading
- Urdu and Arabic font configuration
- Language-specific date/number formatting

### Phase 4
- Icon provider interface and registry
- Lucide provider implementation
- Universal icon name mapping
- Update all components to use icon adapter

### Phase 5
- Additional icon providers (Heroicons, Tabler, Material, Phosphor, Remix)
- Icon management UI
- Translation import/export
- Automated translation coverage reports
- RTL testing infrastructure
