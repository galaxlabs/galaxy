# 27 — Portal, Website, and Public Platform Layer

## 1. Purpose

Define the architecture for Galaxy's external-facing platform layer — portal interfaces for authenticated external users, website/public pages for anonymous visitors, and public API access. This layer is completely separate from the internal Desk/Studio system.

## 2. Three User Worlds

Galaxy distinguishes three distinct user worlds. Each has its own route namespace, API prefix, permission engine, and metadata model. They never mix.

| World | Type | Routes | Auth |
|-------|------|--------|------|
| **System** | Internal authenticated | `/desk/*`, `/studio/*`, `/bench/*`, `/api/resource/*`, `/api/core/*`, `/api/bench/*` | Session or API token |
| **Portal** | External authenticated | `/portal/*`, `/api/portal/*` | Portal session or portal token |
| **Website/Guest** | Anonymous or pre-auth | `/www/*`, `/public/*`, `/portal/login`, `/portal/signup` | None or guest session |

### 2.1 System User

Internal users who access Desk, Studio, Bench Manager, internal APIs, admin settings, app/module management, DocType Builder, migration center, reports, scripts, and internal operations. See Doc 28 §3.

### 2.2 Portal User

Authenticated external users who access portal dashboards, own profile, own linked records, portal pages, and public-facing workflows. See Doc 28 §4.

### 2.3 Website User / Guest

Anonymous or public visitor who accesses website pages and public interactions before login. See Doc 28 §5.

### 2.4 Separation Rules

- System routes never overlap with portal routes.
- Portal routes never overlap with website/public routes.
- System permissions never apply to portal routes automatically.
- Portal permissions never apply to internal APIs.
- Guest has no access to any authenticated route by default.
- Identity transitions require explicit action (see Doc 28 §12).

## 3. Platform Layer Architecture

```
Request → Router
           ├── Matches /desk/*, /studio/*, /bench/* → System Middleware → System Auth → System Handler
           ├── Matches /portal/*, /api/portal/*     → Portal Middleware → Portal Auth → Portal Handler
           ├── Matches /www/*, /public/*            → Guest Middleware → Guest Handler
           ├── Matches /api/resource/*               → System Middleware (internal CRUD API)
           ├── Matches /api/core/*                    → System Middleware (core services)
           ├── Matches /api/bench/*                  → System Middleware (bench operations)
           └── Root /                                → Guest Middleware (landing/public pages)
```

### 3.1 System Middleware

- Validates session or API token.
- Loads user, roles, permissions.
- Rejects non-system users.
- Applies CSRF protection.
- Applies rate limiting.

### 3.2 Portal Middleware

- Validates portal session or portal token.
- Loads portal user, portal roles, portal permissions.
- Rejects non-portal users.
- Applies rate limiting (separate from system limits).
- Does NOT load system roles or DocPerms.

### 3.3 Guest Middleware

- No authentication required.
- Tracks guest session for rate limiting and analytics.
- Enforces public-only access rules.
- Applies strict rate limiting.
- Optional captcha/anti-spam for public forms.

## 4. Route Architecture

| Prefix | World | Handler Module |
|--------|-------|----------------|
| `/desk/*` | System | `galaxy.desk.router` |
| `/studio/*` | System | `galaxy.studio.router` |
| `/bench/*` | System | `galaxy.bench.router` |
| `/api/resource/*` | System | `galaxy.core.crud` |
| `/api/core/*` | System | `galaxy.core.api` |
| `/api/bench/*` | System | `galaxy.bench.api` |
| `/portal/*` | Portal | `galaxy.portal.router` |
| `/api/portal/*` | Portal | `galaxy.portal.api` |
| `/www/*` | Guest | `galaxy.website.router` |
| `/public/*` | Guest | `galaxy.website.public` |
| `/` | Guest | `galaxy.website.landing` |

## 5. Portal Components

### 5.1 Portal User Model

Separate from System User. Portal users have their own identity table, authentication, and session management.

### 5.2 Portal Permission Model

Portal permissions are separate from DocPerm:

- Portal Role — roles scoped to portal access
- Portal Permission — CRUD + action permissions for portal users
- Portal Field Permission — field-level read/write for portal users

### 5.3 Portal Pages

Portal provides configurable pages:

- Dashboard — widgets showing user-specific data
- Profile — user profile management
- Resource list/forms — portal views of allowed DocTypes
- Actions — workflow actions available to portal users

### 5.4 Portal API

Portal API at `/api/portal/*` is separate from internal API. Portal endpoints:

- `GET /api/portal/resource/{doctype}` — list allowed records
- `GET /api/portal/resource/{doctype}/{name}` — get record
- `POST /api/portal/resource/{doctype}` — create record (if allowed)
- `PUT /api/portal/resource/{doctype}/{name}` — update record (if allowed)
- `DELETE /api/portal/resource/{doctype}/{name}` — delete record (if explicitly allowed)
- `POST /api/portal/action/{action}` — execute portal action

## 6. Website/Public Components

### 6.1 Public Pages

Static or dynamic pages served to anonymous visitors:

- Landing page
- Documentation
- Pricing
- Blog
- Public forms
- Login/signup pages

### 6.2 Public Actions

Actions that anonymous users can perform:

- Signup
- Submit public form
- Access token-based page
- View public DocType records (if exposed)

### 6.3 Public Access Rules

- Public page: no authentication
- Public form: optional captcha, rate-limited
- Public DocType view: must be explicitly enabled via `allow_web_view`
- Public API access: must be explicitly enabled via `allow_public_api`
- File upload: disabled for guests by default

## 7. Implementation Phases

### Phase 1
- Architecture docs (this document + Doc 28)
- Define three user worlds and route separation

### Phase 2
- Portal User metadata model and authentication
- Portal role/permission metadata
- Portal session management

### Phase 3
- Portal pages and portal CRUD API
- Portal dashboards and widgets

### Phase 4
- Website/public page routing
- Public form handling
- Public DocType view

### Phase 5
- Guest session and rate limiting
- Public access tokens
- Captcha/anti-spam integration

### Phase 6
- Portal activity logging
- Public form submission audit
- Cross-world security audit
