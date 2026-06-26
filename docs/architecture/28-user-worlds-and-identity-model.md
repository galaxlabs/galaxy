# 28 — User Worlds and Identity Model

## 1. Purpose

Define the three distinct user worlds in Galaxy Framework — System User, Portal User, and Website User/Guest — and the identity model that governs authentication, authorization, route access, permission evaluation, and identity transitions across all three worlds. The three worlds must never mix.

## 2. Why three user worlds are needed

Frappe conflates all users into a single `tabUser` table with optional `portal` flag, leading to confused permission boundaries and security risks. Galaxy separates them by design:

- **System User** — trusted internal operator with full Desk/Studio/API access
- **Portal User** — external authenticated user with scoped portal access
- **Website User/Guest** — anonymous visitor with public-only access

Each world has its own:
- Identity table and authentication
- Route namespace and API prefix
- Permission engine and metadata model
- Session management and rate limiting
- Audit trail

## 3. System User

### 3.1 Purpose

Internal users who access Desk, Studio, Bench Manager, internal APIs, admin settings, app/module management, DocType Builder, migration center, reports, scripts, and internal operations.

### 3.2 Route namespace

| Prefix | Description |
|--------|-------------|
| `/desk/*` | Desk UI — forms, lists, reports, dashboards |
| `/studio/*` | Studio — DocType Builder, app/module manager |
| `/bench/*` | Bench Manager — sites, backups, migrations, logs |
| `/api/resource/*` | Internal CRUD API |
| `/api/core/*` | Core services — scripts, reports, actions |
| `/api/bench/*` | Bench operations — install, backup, migrate |
| `/api/migration/*` | Migration preview/apply |

### 3.3 Examples

Administrator, System Manager, App Builder, Developer, Support Agent, Platform Admin, Internal Operator

### 3.4 Permission engine

System User permissions are evaluated through:

1. **DocPerm** — role-level CRUD per DocType
2. **FieldPermission** — field-level read/write per role
3. **PermissionRule** — multi-dimensional conditions (role + user + context)
4. **DataMaskRule** — field-level masking
5. **Report permissions** — report-level access
6. **Script permissions** — server/client script execution
7. **Migration permissions** — migration apply access
8. **Bench permissions** — site/app/platform management

### 3.5 System User metadata objects

| Object | Table | Purpose |
|--------|-------|---------|
| User | `tabUser` | System user identity |
| Role | `tabRole` | System role |
| Has Role | `tabHasRole` | User-role assignment |
| DocPerm | `tabDocPerm` | DocType-level CRUD per role |
| FieldPermission | `tabFieldPermission` | Field-level read/write |
| PermissionRule | `tabPermissionRule` | Multi-dimensional permission conditions |
| DataMaskRule | `tabDataMaskRule` | Field-level privacy masking |

### 3.6 Session

System users authenticate via session cookie or API token. Sessions are stored in `tabSession` with expiry, user agent tracking, and IP logging.

## 4. Portal User

### 4.1 Purpose

Authenticated external users who access portal dashboards, own profile, own linked records, portal pages, portal actions, public-facing workflows, and allowed dashboard widgets. Portal users are **not** System Users.

### 4.2 Route namespace

| Prefix | Description |
|--------|-------------|
| `/portal` | Portal landing/dashboard |
| `/portal/login` | Portal login |
| `/portal/signup` | Portal registration |
| `/portal/profile` | Portal user profile |
| `/portal/settings` | Portal user settings |
| `/portal/dashboard` | Portal dashboard widgets |
| `/portal/resource/{doctype}` | Portal DocType list view |
| `/portal/resource/{doctype}/{name}` | Portal DocType detail view |
| `/portal/action/{action}` | Portal action execution |
| `/api/portal/*` | Portal API |

### 4.3 Examples

Customer, Member, Subscriber, Seller, Buyer, Community Participant, Queue Participant, Chat Participant, Workflow Participant, Public App User

### 4.4 Permission engine

Portal permissions are separate from System permissions. They are evaluated through:

1. **PortalRole** — roles scoped to portal access
2. **PortalPermission** — CRUD + action permissions for portal resources
3. **PortalFieldPermission** — field-level read/write for portal access
4. **PortalProfileLink** — ownership linking between portal user and records

### 4.5 Portal permission rules

| Rule | Default | Description |
|------|---------|-------------|
| Read own linked records | Allowed | Portal user reads records linked to their profile |
| Create allowed records | Configurable | Portal user creates new records (if enabled) |
| Update allowed fields | Configurable | Portal user updates specific fields |
| Delete records | Denied | Cannot delete unless explicitly allowed |
| Comment | Configurable | Comment on owned records |
| Mention | Configurable | @mention other portal users |
| Upload/download | Configurable | File operations |
| Run portal actions | Configurable | Execute portal workflow actions |
| View dashboard widgets | Configurable | See dashboard cards |
| View portal pages | Configurable | Access portal page routes |

### 4.6 Portal User metadata objects

| Object | Table | Purpose |
|--------|-------|---------|
| Portal User | `tabPortalUser` | Portal user identity (separate from System User) |
| Portal Role | `tabPortalRole` | Portal role |
| Portal Permission | `tabPortalPermission` | Portal-level CRUD per role |
| Portal Field Permission | `tabPortalFieldPermission` | Portal field-level read/write |
| Portal Profile Link | `tabPortalProfileLink` | Links portal user to owned records |
| Portal Dashboard | `tabPortalDashboard` | Portal dashboard widget config |
| Portal Page | `tabPortalPage` | Portal page route and content |
| Portal Activity Log | `tabPortalActivityLog` | Portal user action audit |

### 4.7 Portal Session

Portal users authenticate via portal login (separate from system login). Portal sessions are stored in `tabPortalSession` with separate expiry, tracking, and rate limiting.

### 4.8 Important restrictions

- Portal user **cannot access Desk** by default.
- Portal permissions are checked **server-side** only.
- Portal user **cannot bypass** System User permissions.
- Portal APIs are **separate** from internal APIs.
- Portal user **cannot delete** owned records by default unless a rule explicitly allows it.
- Portal user **can edit own profile** and change password by default.
- Portal user can **only see records linked** through ownership, profile links, sharing rules, or public exposure.

## 5. Website User / Guest

### 5.1 Purpose

Anonymous or public visitor who accesses website pages and public interactions before login. Once a Website User logs in, they become a Portal User or System User depending on account type.

### 5.2 Route namespace

| Prefix | Description |
|--------|-------------|
| `/` | Landing page |
| `/www/*` | Website pages |
| `/public/*` | Public resources |
| `/assets/*` | Public assets |
| `/website/*` | Website content pages |
| `/portal/login` | Login page (public) |
| `/portal/signup` | Signup page (public) |

### 5.3 Examples

Visitor, Anonymous Reader, Public Form Submitter, Public Signup User, Token-Link User, Read-Only Public Viewer

### 5.4 Permission model

Guest users can only access explicitly public resources:

| Permission | Default | Description |
|------------|---------|-------------|
| Read public pages | Allowed | Access to public page routes |
| Read public DocType records | Configurable | Only if `allow_web_view` is enabled on DocType |
| Submit public forms | Configurable | Only if public form is enabled |
| Access token-based pages | Configurable | Valid token required |
| Update records | Denied | Never allowed for guests |
| Delete records | Denied | Never allowed for guests |
| Internal API access | Denied | Never allowed for guests |
| Desk access | Denied | Never allowed for guests |
| File upload | Denied | Disabled by default |

### 5.5 Guest metadata objects

| Object | Table | Purpose |
|--------|-------|---------|
| Guest Session | `tabGuestSession` | Anonymous session tracking |
| Website Page | `tabWebsitePage` | Public page content and routing |
| Public Action | `tabPublicAction` | Public-facing action definition |
| Public Form | `tabPublicForm` | Public form configuration |
| Public View Rule | `tabPublicViewRule` | Conditions for public DocType access |
| Public Access Token | `tabPublicAccessToken` | Token-based access for limited resources |
| Rate Limit Rule | `tabRateLimitRule` | Per-route or per-IP rate limit config |

### 5.6 Guest session

Guests receive a lightweight session for rate limiting, analytics, and tracking. No authentication is required. Optional captcha/anti-spam for form submissions.

## 6. Route separation

Routes are separated by prefix and never overlap:

```
System:   /desk/*        /studio/*        /bench/*        /api/resource/*  /api/core/*  /api/bench/*
Portal:   /portal/*      /api/portal/*
Guest:    /              /www/*           /public/*        /assets/*
```

Each prefix maps to a dedicated middleware and handler module.

## 7. API separation

### 7.1 Internal API (`/api/resource/*`, `/api/core/*`, `/api/bench/*`)

- System authentication required
- Full CRUD access (subject to DocPerm)
- Script execution
- Report execution
- Migration operations
- Bench operations

### 7.2 Portal API (`/api/portal/*`)

- Portal authentication required
- Scoped CRUD (subject to PortalPermission)
- Portal action execution
- Profile management
- No script execution
- No migration operations

### 7.3 Public API (`/api/public/*`)

- No authentication required
- Read-only or submit-only
- Explicitly enabled per endpoint
- Strict rate limiting
- No update or delete

## 8. Permission engine separation

Each world has its own permission engine:

```python
# System permissions
system_permissions = SystemPermissionEngine(user, roles)
system_permissions.can_read("Customer", doc)
system_permissions.can_write("Customer", doc, "email")
system_permissions.can_execute_script("my_script")

# Portal permissions
portal_permissions = PortalPermissionEngine(portal_user, portal_roles)
portal_permissions.can_read("Customer", doc)  # checks PortalPermission + profile link
portal_permissions.can_write("Customer", doc, "email")
portal_permissions.can_execute_action("submit_order")

# Guest permissions
guest_permissions = GuestPermissionEngine(guest_session)
guest_permissions.can_view_page("/www/pricing")
guest_permissions.can_submit_form("contact_us")
guest_permissions.can_view_record("Customer", doc)  # checks PublicViewRule
```

## 9. Profile and account rules

| Rule | System User | Portal User | Guest |
|------|-------------|-------------|-------|
| Can edit own profile | Yes | Yes | N/A |
| Can change password | Yes | Yes | N/A |
| Can update email | Configurable | Configurable | N/A |
| Can delete own account | Configurable | Configurable | N/A |
| Can view own activity | Configurable | Yes | N/A |
| Must verify email | Configurable | Recommended | N/A |
| 2FA supported | Yes | Optional | N/A |
| Session timeout | Configurable | Configurable | N/A |

## 10. Ownership and linked-record rules

Portal users see records linked through:

1. **PortalProfileLink** — explicit link between portal user and record via a `user` or `profile` field
2. **Ownership** — records created by the portal user (`owner` field matches)
3. **Sharing rules** — records explicitly shared with the portal user or their role
4. **Public exposure** — DocTypes with `allow_web_view` enabled

### PortalProfileLink metadata

| Field | Type | Description |
|-------|------|-------------|
| `portal_user` | Link | Portal User |
| `doctype` | Link | Target DocType |
| `docname` | Data | Target document name |
| `link_field` | Data | Field name on the document that contains the user identifier |
| `relationship` | Select | `owner`, `member`, `assigned`, `custom` |
| `expires_on` | Date | Optional link expiry |

## 11. Guest/public access rules

### 11.1 Public page access

Public pages are accessible at `/www/*` and `/public/*`. They render template content with no authentication.

### 11.2 Public DocType view

A DocType can be exposed for public read access by enabling `allow_web_view` in DocType settings. Public view rules further restrict which fields and records are visible.

### 11.3 Public form submission

Public forms allow anonymous users to submit data. Each public form configuration specifies:

- Which DocType to create
- Which fields are visible/submittable
- Optional captcha
- Rate limit per IP
- Notification on submission

### 11.4 Token-based access

Public Access Tokens allow time-limited, capability-limited access to specific resources without full authentication. Used for:

- Password reset links
- Document sharing links
- Download links

## 12. Identity transition rules

### 12.1 Transition paths

```
Guest
  │
  ├── signup/login ──────────► Portal User
  │                              │
  │                              ├── admin grants internal role ──► System User
  │                              └── (cannot self-promote)
  │
  └── admin creates account ──► System User (directly)
```

### 12.2 Transition rules

| Transition | Allowed | Required Action |
|------------|---------|-----------------|
| Guest → Portal User | Yes | User completes signup |
| Guest → System User | Yes (admin only) | Admin creates system account |
| Portal User → System User | Yes (admin only) | Admin grants a system role to the portal user |
| System User → Portal User | No | Account types are separate |
| Self-promotion (Portal → System) | **Never** | Requires admin action |

### 12.3 Promotion guard

Portal User promotion to System User must:

1. Require explicit admin action
2. Create a separate System User record linked to the Portal User
3. Not carry over portal permissions to system context
4. Not carry over system permissions to portal context
5. Be logged in audit trail

## 13. Security rules

1. **Guest cannot access Desk** — returns 404 or redirect to login.
2. **Portal User cannot access Desk** unless explicitly promoted to System User.
3. **System User permissions must not automatically apply** to Portal routes.
4. **Portal permissions must not automatically apply** to internal APIs.
5. **Public forms must be rate-limited** — per-IP and per-endpoint limits.
6. **Guest uploads disabled by default** — must be explicitly enabled per public form.
7. **Delete disabled for Portal and Guest by default** — delete requires explicit rule.
8. **Public view must be explicitly enabled** per DocType via `allow_web_view`.
9. **Sensitive fields must be masked** for Portal/Guest by default unless a rule allows unmasked access.
10. **All login, profile change, password change, account delete, data export, and sensitive actions must be audited** across all three worlds.
11. **Portal session hijacking countermeasures** — rotate session ID on login, bind to IP optional, expire on logout.
12. **Cross-world data leakage prevented** — API handlers must validate world membership before serving data.

## 14. Metadata objects needed

### 14.1 System side

| Object | Purpose |
|--------|---------|
| User | System user identity, auth, profile |
| Role | System role definition |
| Has Role | User-role assignment |
| DocPerm | DocType-level CRUD per role |
| FieldPermission | Field-level read/write access |
| PermissionRule | Multi-dimensional conditions |
| DataMaskRule | Field-level masking |

### 14.2 Portal side

| Object | Purpose |
|--------|---------|
| Portal User | Portal user identity (separate table) |
| Portal Role | Portal role definition |
| Portal Permission | Portal CRUD + action per role |
| Portal Field Permission | Portal field-level read/write |
| Portal Profile Link | Ownership linking |
| Portal Dashboard | Dashboard widget config |
| Portal Page | Portal page route/content |
| Portal Activity Log | Portal action audit |

### 14.3 Website/public side

| Object | Purpose |
|--------|---------|
| Guest Session | Anonymous session tracking |
| Website Page | Public page content/routing |
| Public Action | Public action definition |
| Public Form | Public form configuration |
| Public View Rule | Conditions for public DocType access |
| Public Access Token | Token-based resource access |
| Rate Limit Rule | Per-route/IP rate limit config |

## 15. Implementation phases

### Phase 1 (Current)
- Architecture document (this document + Doc 27)
- Update Doc 23 with exposure targeting references

### Phase 2 — Identity type enum and route separation
- Add `UserWorld` enum to core types: `system`, `portal`, `guest`
- Route registration with world prefix
- Middleware separation framework
- Tests: route dispatch by world

### Phase 3 — Portal User metadata
- Portal User metadata model and table
- Portal Role and Portal Permission metadata
- Portal session management
- Portal profile and account endpoints
- Tests: portal auth, portal permissions

### Phase 4 — Portal data access
- PortalProfileLink metadata
- Portal CRUD API (`/api/portal/resource/*`)
- Portal field permission evaluation
- Ownership and linked-record resolution
- Tests: portal CRUD, field permissions, ownership filtering

### Phase 5 — Guest/public access
- Guest session tracking
- Website page routing
- Public View Rule metadata
- Public form handling
- Public Access Token management
- Tests: guest access, public forms, token access

### Phase 6 — Security hardening
- Rate limiting per world
- Cross-world audit logging
- Captcha/anti-spam for public forms
- Portal promotion guard
- Security tests for all three worlds

### Phase 7 — Portal dashboards and pages
- Portal Dashboard widget system
- Portal Page builder
- Portal action execution
- Activity logging
- Tests: dashboards, pages, actions, audit
