# 25 — Boilerplate and Code Generation Architecture

## 1. Purpose

Define the architecture for generating boilerplate code from Galaxy metadata. Generated code is optional, reviewable, and must never overwrite user customizations. The generation system supports app scaffolding, DocType generation, API generation, UI boilerplate, integration stubs, test skeletons, and future framework targets (React, Vue, Next.js, Svelte).

## 2. Core Principles

- Metadata drives generation, but generated code is NOT the source of truth.
- All generated code is disabled by default until explicitly reviewed and enabled.
- Generated files contain protected regions that survive regeneration.
- Generation must show a diff before writing files.
- Regeneration must never overwrite user changes in unprotected regions.
- The generator tracks file hashes to detect modifications.

## 3. Generated File Lifecycle

```
1. Metadata is created/saved (DocType, fields, permissions, etc.)
2. Generation is triggered (manual or via CLI)
3. Generator reads metadata + template
4. Generator produces output
5. Diff is shown to the developer (preview mode)
6. Developer reviews and approves
7. Files are written with protected region markers
8. Hash is stored in CodeGenerationBlock
9. On regeneration:
   a. Check if file exists
   b. If file modified (hash mismatch) → warn, show diff, ask confirmation
   c. Preserve protected regions
   d. Regenerate non-protected sections
   e. Update hash
```

## 4. Boilerplate Categories

### 4.1 App Boilerplate

Generated when a new app is created via `galaxy create-app`:

```
apps/{app_name}/
├── __init__.py
├── app.json
├── hooks.py
├── modules/
│   └── {module_name}/
│       ├── __init__.py
│       ├── module.json
│       └── doctype/
├── permissions.py
├── routes.py
├── tests/
│   ├── __init__.py
│   └── test_app.py
├── fixtures/
│   └── seed.json
├── README.md
└── CHANGELOG.md
```

### 4.2 DocType Boilerplate

Generated when a new DocType is created:

```
apps/{app_name}/modules/{module}/doctype/{doctype}/
├── {doctype}.json          (DocType metadata export)
├── {doctype}.py            (controller file)
├── client_scripts/
│   └── {doctype}.js        (client script starter)
├── server_scripts/
│   └── {doctype}_hooks.py  (generated hook templates)
├── permissions/
│   └── {doctype}_perms.json
├── tests/
│   ├── test_{doctype}.py   (CRUD test skeleton)
│   └── fixtures/
│       └── {doctype}.json
└── migration_preview.md    (migration SQL preview)
```

### 4.3 API Boilerplate

Generated from DocType Action and Integration metadata:

```
apps/{app_name}/api/
├── {doctype}/
│   ├── routes.py              (REST route definitions)
│   ├── schemas.py             (request/response schemas)
│   ├── handlers.py            (handler implementations)
│   ├── permissions.py         (permission wrappers)
│   ├── validators.py          (request validation)
│   ├── audit.py               (audit logging wrapper)
│   └── tests/
│       ├── test_routes.py
│       └── test_handlers.py
```

### 4.4 UI Boilerplate

Generated from DocType field and layout metadata:

```
apps/{app_name}/ui/
├── {doctype}/
│   ├── list_view.json         (list view config)
│   ├── form_view.json         (form view config)
│   ├── dashboard.json         (dashboard cards)
│   ├── actions.json           (action button config)
│   ├── scripts/
│   │   └── {doctype}.js       (client script starter)
│   └── tests/
│       └── test_ui.py
```

### 4.5 Integration Boilerplate

Generated from DocType Integration metadata:

```
apps/{app_name}/integrations/
├── {integration_name}/
│   ├── webhook_handler.py     (incoming webhook)
│   ├── api_client.py          (outgoing API wrapper)
│   ├── retry.py               (retry policy)
│   ├── secrets.py             (secret reference config)
│   └── tests/
│       ├── test_webhook.py
│       └── test_api_client.py
```

### 4.6 Package Boilerplate

Generated for pip-installable distribution:

```
{pkg_name}/
├── pyproject.toml
├── setup.py (or setup.cfg)
├── MANIFEST.in
├── {pkg_name}/
│   ├── __init__.py
│   ├── version.py
│   └── ...
├── tests/
├── CHANGELOG.md
└── LICENSE
```

### 4.7 Generated App Targets

For future SPA generation targets:

```
# React
apps/{app_name}/frontend/react/
├── src/
│   ├── components/
│   │   └── {Doctype}/
│   │       ├── List.tsx
│   │       ├── Form.tsx
│   │       └── types.ts
│   ├── api/
│   │   └── {doctype}.ts
│   └── App.tsx

# Vue
apps/{app_name}/frontend/vue/
├── src/
│   ├── components/
│   │   └── {Doctype}/
│   │       ├── List.vue
│   │       ├── Form.vue
│   │       └── types.ts
│   ├── composables/
│   │   └── use{Doctype}.ts
│   └── App.vue

# Next.js
apps/{app_name}/frontend/nextjs/
├── app/
│   └── {doctype}/
│       ├── page.tsx
│       ├── [id]/page.tsx
│       └── new/page.tsx
├── components/
│   └── {Doctype}Form.tsx
└── lib/
    └── api.ts

# Svelte
apps/{app_name}/frontend/svelte/
├── src/
│   ├── routes/
│   │   └── {doctype}/
│   ├── lib/
│   │   └── components/
│   └── app.html
```

## 5. Code Generation Block Metadata

### CodeGenerationBlock Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType (or empty for framework-level) |
| `target_type` | Select | app / module / doctype / api / ui / integration / test / package |
| `language` | Select | python / javascript / typescript / go / yaml / vue / jsx / tsx / svelte |
| `template_engine` | Select | jinja2 / handlebars / mustache / ejs |
| `template_path` | Data | Path to the template file |
| `output_path` | Data | Relative path for generated output (can include {{doctype}}, {{app}} placeholders) |
| `overwrite_policy` | Select | always / never / ask / diff_before_write |
| `generated_hash` | Data | SHA256 hash of last generated content |
| `protected_regions` | JSON | List of region identifiers with their stored content |
| `enabled` | Check | Whether this block is active |
| `requires_review` | Check | Generated code requires manual review before use |
| `last_generated_at` | Datetime | Timestamp of last generation |
| `generated_by` | Link | User who triggered generation |
| `source_app` | Data | Which app defined this block |

### Template Path Placeholders

| Placeholder | Replaced With |
|-------------|---------------|
| `{{app}}` | App name |
| `{{module}}` | Module name |
| `{{doctype}}` | DocType name (snake_case) |
| `{{Doctype}}` | DocType name (PascalCase) |
| `{{doctype_label}}` | DocType label |
| `{{fields}}` | Field list (iterable in template) |
| `{{permissions}}` | Permission list |
| `{{version}}` | Current framework version |

## 6. Protected Code Regions

Generated files contain markers that protect user-written code during regeneration.

### Python Protected Regions

```python
# galaxy:keep:start custom_validation
def custom_validate(doc):
    """User-added validation logic"""
    pass
# galaxy:keep:end
```

### JavaScript Protected Regions

```javascript
// galaxy:keep:start form_handlers
function onCustomerTypeChange(value) {
    // user code here
}
// galaxy:keep:end
```

### Template Protected Regions

```jinja
{% # galaxy:keep:start extra_fields %}
{{ ui.field("custom_field") }}
{% # galaxy:keep:end %}
```

### Protected Region Rules

- Regions are identified by name (after `galaxy:keep:start`).
- During regeneration, the generator parses existing content for all `galaxy:keep:start...galaxy:keep:end` blocks.
- These blocks are preserved verbatim in the regenerated output.
- If a protected region is not found in the template anymore, it is preserved at the end of the file.
- If the entire file was deleted by the user, the generator asks before recreating it.
- Developers can add new protected regions manually.

## 7. Diff and Preview

Before writing generated files, the system shows a diff.

### Diff Flow

```
1. Check if output file exists
2. If exists:
   a. Read current content
   b. Extract protected regions
   c. Run template with metadata → generate new content
   d. Re-insert protected regions into new content
   e. Generate unified diff between current and new
   f. Show diff to user (CLI or Desk UI)
   g. User approves or rejects
3. If new file:
   a. Generate content
   b. Show preview to user
   c. User approves or rejects
4. On approval:
   a. Write file
   b. Compute hash
   c. Store hash in CodeGenerationBlock
```

### CLI Diff Display

```
> galaxy generate doctype Customer

Preview: apps/customer/doctype/Customer/Customer.py
─────────────────────────────────────────────────
--- existing
+++ generated
@@ -5,6 +5,8 @@
 class Customer(Document):
     def before_insert(self):
         pass
+        # galaxy:keep:start hooks
+        # (preserved from previous generation)
+        # galaxy:keep:end

Accept changes? [Y/n/diff]: diff
... (detailed diff displayed)
Accept? [Y/n]:
```

## 8. Review Before Enable

Generated server scripts and client scripts require explicit activation.

### Review Flow

```
1. Code is generated → saved to disk
2. CodeGenerationBlock.requires_review = true
3. Developer navigates to /desk/code-generation/review
4. Review page shows:
   a. Generated file path
   b. Diff from template (if template changed)
   c. Security analysis (dangerous imports, SQL, etc.)
   d. Test results (if test file was generated)
5. Developer can:
   a. Approve → enabled = true, code is now active
   b. Edit → opens file in editor
   c. Regenerate → re-run generation
   d. Reject → delete generated file, mark as rejected
```

## 9. Security Rules

| Rule | Description |
|------|-------------|
| Generated code is disabled by default | All generated server/client scripts require review before activation |
| Protected regions never overwritten | User code in galaxy:keep blocks is sacred |
| Templates are sandboxed | Template rendering does not execute generated code |
| Generation is permissioned | Only users with "Code Generation" permission can generate |
| Audit trail | Every generation event is logged (who, when, what, diff) |
| No destructive overwrites | overwrite_policy=never for user-modified files |
| Hash tracking | Hash mismatch triggers confirmation prompt |

## 10. Implementation Phases

### Phase 1
- CodeGenerationBlock metadata schema
- Template engine integration (Jinja2)
- Basic file generation with protected regions

### Phase 2
- App and DocType boilerplate generation
- Diff preview (CLI)
- Review/enable workflow

### Phase 3
- API and UI boilerplate generation
- Integration boilerplate
- Test skeleton generation

### Phase 4
- Package boilerplate generation
- Generated app targets (React, Vue, Next.js, Svelte)
- Framework-level templates

### Phase 5
- Desk UI for code generation management
- In-browser diff viewer
- One-click generation from DocType Builder
