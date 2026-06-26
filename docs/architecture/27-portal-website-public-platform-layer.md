# 27 — Portal, Website, and Public Platform Layer

## 1. Purpose

Define the complete architecture for Galaxy Framework's external-facing platform layer — the Portal engine (authenticated external users), the Website layer (public/anonymous visitors), and the public asset system. This layer is a first-class citizen alongside Desk and Studio, with its own folder structure, route namespace, permission engine, theme system, dashboard builder, page builder, and public interaction model. It is designed to support not only business applications but also marketplaces, queue systems, chat platforms, workflow platforms, social/community platforms, AI-assisted portals, and future blockchain/dapp integration — all through metadata, without writing custom code.

## 2. Desk vs Studio vs Portal vs Website

Galaxy has four core UIs. Each targets a different user world with its own routes, permissions, and rendering pipeline.

| UI | World | Purpose | Routes |
|----|-------|---------|--------|
| **Desk** | System User | Internal admin/operator interface | `/desk/*` |
| **Studio** | System User | Builder/designer interface for metadata | `/studio/*` |
| **Portal** | External Authenticated | Customer/member/community/participant UI | `/portal/*` |
| **Website** | Guest/Public | Public landing, docs, signup, public forms | `/`, `/www/*`, `/public/*` |

- **Desk** handles CRUD, reports, scripts, settings, and system administration.
- **Studio** handles DocType Builder, app/module management, migration center.
- **Portal** handles external user dashboards, profile, owned records, actions, widgets, marketplace listings, queue tickets, chat conversations, workflow tasks.
- **Website** handles public pages, public forms, SEO, and pre-login shell.

## 3. Folder structure: portal, website, www, public

```
galaxy/
├── portal/                    ← Portal engine (external authenticated users)
│   ├── __init__.py
│   ├── routes.py              ← /portal/* route definitions
│   ├── auth.py                ← Portal login, signup, session management
│   ├── profile.py             ← Portal profile and account settings
│   ├── dashboard.py           ← Dashboard layout and widget rendering
│   ├── widgets.py             ← Widget types and data source resolution
│   ├── permissions.py         ← Portal permission engine
│   ├── page_builder.py        ← Portal page builder service
│   ├── theme.py               ← Portal theme resolution and CSS generation
│   ├── notifications.py       ← Portal notification delivery
│   ├── public_actions.py      ← Public action/form handler
│   ├── resource.py            ← Portal CRUD over DocTypes
│   ├── marketplace.py         ← Marketplace support (future)
│   ├── queue.py               ← Queue management support (future)
│   ├── chat.py                ← Chat platform support (future)
│   ├── workflow.py            ← Workflow task view support (future)
│   ├── social.py              ← Social/community support (future)
│   ├── ai_assist.py           ← AI-assisted portal features (future)
│   ├── blockchain.py          ← Blockchain/dapp/wallet integration (future)
│   ├── templates/             ← Portal Jinja2 templates
│   │   ├── dashboard.html
│   │   ├── profile.html
│   │   ├── resource_list.html
│   │   ├── resource_form.html
│   │   ├── page.html
│   │   └── widgets/
│   └── static/                ← Portal-specific CSS/JS
│       ├── css/
│       │   ├── portal.css
│       │   ├── theme.css
│       │   └── components/
│       └── js/
│           ├── portal.js
│           ├── dashboard.js
│           └── components/
│
├── website/                   ← Public website engine
│   ├── __init__.py
│   ├── routes.py              ← /www/* and / route definitions
│   ├── renderer.py            ← Page rendering with SEO metadata
│   ├── seo.py                 ← SEO metadata, sitemap, Open Graph
│   ├── sitemap.py             ← Sitemap generation
│   ├── public_forms.py        ← Public form handler
│   ├── templates/             ← Website Jinja2 templates
│   │   ├── landing.html
│   │   ├── page.html
│   │   ├── docs.html
│   │   └── components/
│   └── static/
│
├── www/                       ← Public HTML entry pages (shell pages)
│   ├── index.html             ← Landing page entry
│   ├── login.html             ← Shell login page
│   ├── signup.html            ← Shell signup page
│   ├── portal.html            ← Portal entry point
│   ├── not_found.html         ← 404 fallback
│   └── error.html             ← 500 fallback
│
├── public/                    ← Public static assets served by framework
│   ├── assets/                ← Generated and compiled assets
│   ├── icons/                 ← Icon sets (Lucide SVGs, etc.)
│   ├── images/                ← Public images and media
│   ├── fonts/                 ← Font files (Noto Nastaliq Urdu, etc.)
│   ├── uploads/               ← User-uploaded public files
│   ├── portal/                ← Portal-specific static assets
│   ├── desk/                  ← Desk-specific static assets
│   ├── studio/                ← Studio-specific static assets
│   └── themes/                ← Generated theme CSS files
```

### 3.1 `www/` — Public Entry Pages

Static or server-rendered shell pages served before login:
- `index.html` — Landing/home page for the Galaxy instance
- `login.html` — Login page shell (loaded before portal or desk login)
- `signup.html` — Self-registration shell
- `portal.html` — Portal SPA entry point
- `not_found.html` — 404 fallback
- `error.html` — 500/error fallback

These are thin shell pages. Dynamic content is loaded via APIs or template rendering through the `website/` engine.

### 3.2 `public/` — Static Assets

Assets served directly by the framework without authentication:
- **`assets/`** — Compiled/generated CSS and JS bundles
- **`icons/`** — SVG icon sets from icon providers
- **`images/`** — Public images (logos, backgrounds, illustrations)
- **`fonts/`** — Font files for multilingual support
- **`uploads/`** — User-uploaded files that are publicly accessible
- **`portal/`** — Portal-specific static assets
- **`desk/`** — Desk-specific static assets
- **`studio/`** — Studio-specific static assets
- **`themes/`** — Generated theme CSS files for portal and desk

## 4. Portal user model

The Portal User is a first-class identity separate from System User.

### Portal User fields

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | Data | Unique identifier |
| `email` | Data | Email address (used for login) |
| `phone` | Data | Phone number |
| `display_name` | Data | Public display name |
| `username` | Data | Unique username for vanity URLs |
| `avatar` | Attach Image | Profile avatar |
| `language` | Link (Language) | Preferred language |
| `timezone` | Data | IANA timezone |
| `portal_role` | Link (Portal Role) | Primary portal role |
| `linked_doctype` | Data | DocType this user is linked to |
| `linked_docname` | Data | Document this user is linked to |
| `account_status` | Select | `active`, `suspended`, `disabled`, `pending_verification` |
| `email_verified` | Check | Email verified |
| `phone_verified` | Check | Phone verified |
| `two_factor_enabled` | Check | 2FA enabled (future) |
| `last_login` | Datetime | Last login timestamp |
| `created_at` | Datetime | Account creation timestamp |

### Portal account types

The system supports multiple portal account types through metadata:

| Type | Description |
|------|-------------|
| Internal User | System User who also has portal access |
| Portal User | Pure external user with no system access |
| Guest User | Anonymous session holder |
| Verified Member | Portal user with verified email/phone |
| Subscriber | Portal user with active subscription/plan |
| Customer/Member Profile | Profile linked to a customer/member DocType |
| Public Profile | Public-facing profile page |
| Organization Profile | Multi-user organization account |
| Team Profile | Team within an organization |

### Portal profile features

- View own profile
- Edit profile fields (configurable per role)
- Upload avatar
- Manage contact details (email, phone)
- Change password
- Language preference
- Notification preferences
- Privacy settings (profile visibility, activity visibility)
- Connected accounts (future — OAuth, SSO)
- Wallet connection (future — blockchain wallet address)
- API tokens (future — if allowed by role)

## 5. Portal permission engine

Portal users need their own permission layer completely separate from the System DocPerm engine.

### Permission dimensions

| Dimension | Description |
|-----------|-------------|
| Portal role | Role assigned to the portal user |
| Linked profile | Document record linked to the portal user's profile |
| Ownership | Records where `owner` matches the portal user |
| Linked document | Records linked via `PortalProfileLink` |
| Organization/team | Records belonging to the user's organization |
| Subscription/plan | Records accessible based on subscription level |
| Record status | Workflow status-based access |
| Document visibility | `public`, `protected`, `private` visibility levels |
| Action type | Specific action being performed |
| Field permission | Field-level read/write/mask rules |
| Dashboard widget permission | Widget-level visibility |
| Page permission | Portal page access |
| Time window | Time-based access restrictions (future) |
| IP/device context | Location/device-based restrictions (future) |

### Portal permission types

| Permission | Default | Description |
|------------|---------|-------------|
| `read` | Configurable | Read records |
| `create` | Configurable | Create new records |
| `update` | Configurable | Update existing records |
| `delete` | **Denied** | Delete records (must be explicitly granted) |
| `submit/request` | Configurable | Submit workflow requests |
| `cancel` | Configurable | Cancel own requests |
| `comment` | Configurable | Comment on records |
| `mention` | Configurable | @mention other users |
| `upload` | Configurable | Upload files |
| `download` | Configurable | Download files |
| `share` | Configurable | Share records with other users |
| `export` | Configurable | Export data |
| `print` | Configurable | Print records |
| `run_action` | Configurable | Execute portal actions |
| `view_dashboard` | Configurable | Access dashboard |
| `manage_profile` | **Allowed** | Edit own profile |
| `change_password` | **Allowed** | Change own password |
| `connect_wallet` | Configurable | Connect blockchain wallet (future) |
| `create_listing` | Configurable | Create marketplace listing (future) |
| `manage_listing` | Configurable | Manage own listings (future) |
| `participate_chat` | Configurable | Join chat conversations (future) |
| `join_queue` | Configurable | Join service queue (future) |

### Default permission rules

| Action | Default | Rationale |
|--------|---------|-----------|
| Read own records | Allowed if enabled | Must be explicitly turned on per DocType |
| Create own profile | **Allowed** | Self-registration requires this |
| Edit own profile | **Allowed** | Core portal functionality |
| Change own password | **Allowed** | Standard security practice |
| Delete own account | **Denied** | Must be explicitly allowed by app |
| Delete own records | **Denied** | Deletion is dangerous; must be explicitly granted per DocType |

**Deletion control**: Deletion is always denied by default for portal users. It must be explicitly enabled per DocType through `PortalPermission.can_delete`. This applies even to "own" records. Ownership does not imply deletion rights.

## 6. Portal DocType and record access

### Portal DocType Permission metadata

| Field | Type | Description |
|-------|------|-------------|
| `doctype` | Link | Target DocType |
| `portal_role` | Link | Portal role this applies to |
| `linked_profile_doctype` | Link | DocType used for profile linking |
| `ownership_rule` | Select | `none`, `owner_field`, `profile_link`, `organization`, `public` |
| `can_read` | Check | Allow read |
| `can_create` | Check | Allow create |
| `can_update` | Check | Allow update |
| `can_delete` | Check | Allow delete (default: false) |
| `can_comment` | Check | Allow comment |
| `can_upload` | Check | Allow file upload |
| `can_download` | Check | Allow file download |
| `can_export` | Check | Allow data export |
| `can_run_action` | Check | Allow action execution |
| `condition` | Code | Additional condition expression |
| `field_permissions` | JSON | Per-field read/write configuration |
| `mask_rules` | JSON | Field-level masking configuration |
| `enabled` | Check | Enable this rule |

### Record access examples

- User sees records linked to their profile (via `PortalProfileLink`)
- User sees records where `owner` = current portal user
- User sees records shared with their organization
- User sees records explicitly shared with them
- User sees public records (visibility = `public`)
- User can update only allowed fields
- User cannot delete unless `can_delete` is explicitly enabled
- User cannot see hidden/masked fields
- User can only read records matching their assigned `condition`

## 7. Portal dashboard builder

Portal dashboards are configurable through metadata. They display widgets, cards, stats, and actions scoped to the portal user's permissions.

### Portal Dashboard metadata

| Field | Type | Description |
|-------|------|-------------|
| `dashboard_name` | Data | Dashboard name |
| `portal` | Link (Portal) | Portal this belongs to |
| `owner_user` | Link (Portal User) | Dashboard owner |
| `role` | Link (Portal Role) | Role visibility |
| `layout_json` | JSON | Grid layout definition |
| `theme` | Link (Portal Theme) | Dashboard-specific theme |
| `is_default` | Check | Default dashboard for this role |
| `enabled` | Check | Enable dashboard |

### Portal Dashboard Widget metadata

| Field | Type | Description |
|-------|------|-------------|
| `widget_name` | Data | Widget name |
| `widget_type` | Select | Type: `stat`, `chart`, `list`, `card`, `action`, `shortcut`, `notification`, `embed`, `feed`, `timeline` |
| `data_source_type` | Select | Source: `doctype_count`, `doctype_list`, `report`, `query`, `action`, `script`, `api` |
| `doctype` | Link | Source DocType |
| `report` | Link | Source report |
| `query` | Code | Custom query |
| `action` | Link | Portal action |
| `chart_type` | Select | `bar`, `line`, `pie`, `doughnut`, `area`, `number` |
| `permission_rule` | Code | Permission condition |
| `refresh_interval` | Int | Auto-refresh in seconds |
| `cache_ttl` | Int | Cache TTL in seconds |
| `layout_position` | JSON | Position in grid |
| `color_token` | Data | CSS variable token for accent color |
| `icon_provider` | Data | Icon provider name |
| `icon_name` | Data | Icon name |
| `enabled` | Check | Enable widget |

### Dashboard examples (framework-generic)

- Subscriber sees own stats and recent activity
- Member sees own documents and pending actions
- Queue participant sees current token status and estimated wait time
- Marketplace seller sees listing stats, inquiries, and orders
- Chat participant sees open conversations and unread count
- Workflow participant sees pending tasks and approval queue
- Community member sees feed, notifications, and connections

## 8. Portal widgets/cards/stats

### Widget types

| Widget | Purpose | Data source |
|--------|---------|-------------|
| **Stat** | Single number with label and trend | Doctype count, query result |
| **Chart** | Visual chart (bar, line, pie, doughnut, area) | Report, query, aggregation |
| **List** | Recent records list | DocType list with filters |
| **Card** | Rich card with title, description, image, action | DocType record, static content |
| **Action** | Action button with icon | Portal Action definition |
| **Shortcut** | Quick link to a page or resource | Route or URL |
| **Notification** | Recent notifications feed | Portal Notification |
| **Embed** | External content in iframe | External URL |
| **Feed** | Activity feed | Activity Log |
| **Timeline** | Chronological event timeline | Document version history |
| **Queue Status** | Queue position and estimated time | Queue system (future) |
| **Chat Preview** | Recent conversations | Chat system (future) |
| **Marketplace Stats** | Listing views, inquiries | Marketplace system (future) |
| **Wallet Status** | Connected wallet balance (future) | Blockchain provider (future) |

## 9. Portal theme and color customization

Portal UI is themeable independently from Desk. Themes are defined as metadata and applied through CSS variables.

### Portal Theme metadata

| Field | Type | Description |
|-------|------|-------------|
| `theme_name` | Data | Theme name |
| `portal` | Link (Portal) | Portal this theme belongs to |
| `mode` | Select | `light`, `dark`, `system` |
| `primary_color` | Data | Primary brand color |
| `accent_color` | Data | Accent color |
| `background_color` | Data | Page background |
| `surface_color` | Data | Card/surface background |
| `text_color` | Data | Primary text color |
| `muted_text_color` | Data | Muted/secondary text color |
| `border_color` | Data | Border color |
| `card_color` | Data | Card background |
| `field_background_color` | Data | Form field background |
| `field_text_color` | Data | Form field text |
| `field_border_color` | Data | Form field border |
| `button_style` | Select | `rounded`, `pill`, `square`, `sharp` |
| `card_style` | Select | `bordered`, `elevated`, `flat`, `filled` |
| `dashboard_style` | Select | `grid`, `masonry`, `list` |
| `font_family` | Data | Font family |
| `direction` | Select | `ltr`, `rtl`, `auto` |
| `radius` | Data | Base border-radius |
| `density` | Select | `compact`, `normal`, `comfortable` |
| `custom_css` | Code | Custom CSS overrides |
| `enabled` | Check | Enable this theme |

### Portal CSS variables

```css
:root {
  --portal-primary: #4f46e5;
  --portal-accent: #06b6d4;
  --portal-bg: #f8fafc;
  --portal-surface: #ffffff;
  --portal-text: #0f172a;
  --portal-muted: #64748b;
  --portal-border: #e2e8f0;
  --portal-card: #ffffff;
  --portal-field-bg: #ffffff;
  --portal-field-text: #0f172a;
  --portal-field-border: #cbd5e1;
  --portal-radius: 8px;
  --portal-density: 1;
  --portal-font: 'Inter', system-ui, sans-serif;
}
```

### Theme resolution order

Portal theme is resolved by checking (in order):

1. User-specific theme preference (stored in Portal User profile)
2. Role-specific theme (stored in Portal Role)
3. Portal-specific theme (stored in Portal metadata)
4. Page-specific theme override (stored in Portal Page)
5. System default portal theme
6. Light mode fallback

## 10. Portal profile and account settings

### Profile page features

| Feature | Default | Configurable |
|---------|---------|--------------|
| View profile | Allowed | Per role |
| Edit display name | Allowed | Per role |
| Edit email | Allowed | Per role (may require re-verification) |
| Edit phone | Allowed | Per role |
| Upload avatar | Allowed | Per role |
| Change password | Allowed | Per role |
| Language preference | Allowed | Always |
| Notification preferences | Allowed | Always |
| Privacy settings | Configurable | Per role |
| Connected accounts | Future | Future |
| Wallet connection | Future | Future |
| API token management | Future | Future (if role allows) |
| Account deletion | Configurable | Per role (disabled by default) |
| Activity log view | Configurable | Per role |

### Profile API endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/portal/profile` | GET | Get own profile |
| `/api/portal/profile` | PUT | Update own profile |
| `/api/portal/profile/avatar` | POST | Upload avatar |
| `/api/portal/profile/password` | PUT | Change password |
| `/api/portal/profile/language` | PUT | Set language preference |
| `/api/portal/profile/notifications` | PUT | Update notification preferences |
| `/api/portal/profile/privacy` | PUT | Update privacy settings |
| `/api/portal/profile/delete` | POST | Request account deletion (if allowed) |

## 11. Portal public interaction model

### Public Action metadata

| Field | Type | Description |
|-------|------|-------------|
| `action_name` | Data | Action name |
| `route` | Data | Public route for this action |
| `method` | Select | `GET`, `POST` |
| `input_schema` | JSON | Input field schema |
| `target_doctype` | Link | DocType to create/update |
| `create_record` | Check | Create a new record on submission |
| `update_record` | Check | Update an existing record |
| `require_login` | Check | Require portal login |
| `require_token` | Check | Require valid access token |
| `captcha_required` | Check | Require captcha |
| `rate_limit` | Int | Max requests per minute per IP |
| `approval_required` | Check | Submission requires admin approval |
| `audit_required` | Check | Log all submissions |
| `enabled` | Check | Enable this action |

### Public interaction use cases

| Use case | Requires login | Creates record | Captcha |
|----------|---------------|----------------|---------|
| Contact form | No | Yes | Optional |
| Service request | Yes | Yes | No |
| Queue join | Optional | Yes | No |
| Booking request | Yes | Yes | No |
| Marketplace inquiry | Optional | Yes | Optional |
| Chat start request | Yes | Yes | No |
| Workflow submission | Yes | Yes | No |
| Community signup | No | Yes | Optional |
| Waitlist signup | No | Yes | Optional |
| Feedback form | No | Yes | Optional |
| Report issue | Optional | Yes | Optional |

## 12. Portal page builder

Portal pages are configurable through metadata. Pages are composed of sections and components.

### Portal Page metadata

| Field | Type | Description |
|-------|------|-------------|
| `page_name` | Data | Page name |
| `route` | Data | URL route under `/portal/page/{route}` |
| `title` | Data | Page title |
| `visibility` | Select | `public`, `login_required`, `role_based`, `token_based` |
| `roles` | JSON | Allowed roles (for `role_based` visibility) |
| `layout_type` | Select | `single`, `sidebar`, `grid`, `tabs` |
| `theme` | Link (Portal Theme) | Page-specific theme override |
| `sections` | JSON | Page section definitions |
| `components` | JSON | Component placement in sections |
| `seo_title` | Data | SEO title |
| `seo_description` | Text | SEO description |
| `cache_ttl` | Int | Page cache TTL |
| `enabled` | Check | Enable this page |

### Portal page component types

| Component | Description |
|-----------|-------------|
| Hero | Full-width hero section with title, subtitle, CTA |
| Card | Rich card with icon, title, description, action |
| Data List | Sortable, filterable list from DocType |
| Form | Dynamic form from DocType fields |
| Public Form | Anonymous submission form |
| Dashboard Card | Embedded dashboard widget |
| Chart | Data visualization chart |
| Timeline | Chronological event feed |
| Comment Box | Document comment thread |
| Chat Box | Live chat widget (future) |
| Queue Status | Queue position display (future) |
| Workflow Task List | Pending tasks list (future) |
| Marketplace Listing | Product/service listing (future) |
| Profile Card | User profile card |
| File Upload | File upload dropzone |
| Notification List | Recent notifications |
| Wallet Connect | Blockchain wallet connection button (future) |
| External Embed | iframe embed of external content |

## 13. Portal marketplace support

Galaxy's architecture supports marketplace-style portals through metadata. No marketplace module is implemented at this stage.

### Marketplace concepts (architecture only)

| Concept | Description |
|---------|-------------|
| Listing | Product/service listing with metadata, images, price |
| Seller Profile | Profile linked to a seller DocType |
| Buyer Profile | Profile linked to a buyer DocType |
| Inquiry | Buyer inquiry on a listing |
| Offer | Price offer on a listing |
| Order/Request | Purchase or service request |
| Review/Rating | Post-transaction feedback |
| Dispute Workflow | Issue resolution workflow |
| Public Listing Page | SEO-optimized listing page |
| Seller Dashboard | Analytics and management dashboard |
| Buyer Dashboard | Purchase history and favorites |
| Moderation Queue | Admin review queue for listings |

All marketplace concepts are built on top of core DocTypes, Portal Pages, and Portal Permissions — no custom code required.

## 14. Portal queue/chat/workflow platform support

### Queue management (architecture only)

| Concept | Description |
|---------|-------------|
| Queue | Service queue definition |
| Token | Queue position token |
| Counter/Agent | Service agent |
| Service Type | Queue category |
| Status | Queue/token status |
| Estimated Time | Wait time calculation |
| Public Status Page | Real-time queue status |
| Portal Ticket Dashboard | User's queue tickets |
| Notifications | Status change alerts |
| Kiosk/Display | Public queue display (future) |

### Chat management (architecture only)

| Concept | Description |
|---------|-------------|
| Conversation | Chat thread |
| Participant | Conversation participant |
| Message | Chat message with attachments |
| Assignment | Agent assignment |
| Channel | Chat channel (public, private, support) |
| Status | Conversation status |
| Canned Response | Pre-defined responses |
| Portal Chat Widget | Embeddable chat widget |
| Internal Operator Console | Desk-based chat management |
| AI Assistant | Chat summarization, suggestions (future) |

### Workflow management (architecture only)

| Concept | Description |
|---------|-------------|
| Workflow Task | Task assigned to portal user |
| Participant | Task participant |
| Approval | Approve action |
| Rejection | Reject action |
| Escalation | Auto-escalate on timeout |
| Comments | Task comments |
| Attachments | Task files |
| Public/Portal Task View | User's task dashboard |
| Notifications | Task assignment/update alerts |

## 15. Portal social/community support

### Social/community concepts (architecture only)

| Concept | Description |
|---------|-------------|
| Member Profile | Public community profile |
| Feed | Activity feed |
| Post | Community post with comments |
| Comment | Post comment thread |
| Like/Reaction | Content reaction |
| Follow | Follow member or topic |
| Group | Community group |
| Event | Community event |
| Message | Direct message |
| Moderation | Content moderation queue |
| Reputation/Badges | Gamification (future) |

## 16. AI-assisted portal support

Galaxy's architecture supports AI assistance at the portal layer. AI must never bypass permissions.

### AI use cases (architecture only)

| Use case | Description |
|----------|-------------|
| App generation | Generate portal pages from natural language |
| Field suggestions | Suggest portal form fields |
| Dashboard suggestions | Suggest relevant widgets |
| Workflow suggestions | Suggest workflow steps |
| Chat summarization | Summarize chat conversations |
| Moderation | Auto-moderate public content |
| Smart search | Natural language search over portal records |
| Document extraction | Extract data from uploaded documents |
| Permission explanation | Explain why a resource is (not) accessible |
| Migration explanation | Explain schema changes in plain language |
| Content generation | Generate page content, descriptions, help text |

## 17. Blockchain/dapp/wallet integration support

Galaxy's architecture can support blockchain-connected portals in the future. No blockchain runtime is implemented.

### Blockchain concepts (architecture only)

| Concept | Description |
|---------|-------------|
| Wallet Identity Provider | Connect external wallet (WalletConnect, etc.) |
| Wallet Connection Metadata | Store connected wallet address per user |
| Chain/Provider Registry | Supported blockchain networks |
| Transaction Reference | Reference to on-chain transaction |
| Smart Contract Action | Metadata-defined contract interaction |
| Signed Message Verification | Server-side signature verification |
| Token-Gated Access | Restrict access based on token ownership |
| Dapp Portal Page | Portal page connected to dapp |
| NFT Gallery | Display owned NFTs |
| On-chain Data Display | Display data from smart contracts |

### Security rules for blockchain

- Never store private keys on the server
- Never ask users for seed phrases
- Use WalletConnect-style signature-based authentication (future)
- Server verifies cryptographic signatures where needed
- Blockchain actions require explicit user confirmation
- All blockchain actions are audited
- Chain integrations are disabled by default
- Token-gated access is evaluated server-side

## 18. Security and privacy rules

### Portal security rules

1. **Portal user cannot access Desk** by default — returns 404 or login redirect.
2. **Portal API is separate from internal API** — no shared endpoints.
3. **Portal permissions are checked server-side** — client-side checks are UI convenience only.
4. **Every portal action must check permission** — no action is trusted from client alone.
5. **Field masking applies in portal views** — sensitive fields masked per role.
6. **Public forms must have rate limiting** — per-IP and per-endpoint.
7. **Guest submissions must have anti-spam/captcha option** — configurable per form.
8. **File uploads must be validated** — type, size, content scanning.
9. **Portal theme custom CSS must be sanitized** — no script injection via CSS.
10. **All sensitive actions audited** — login, profile change, password change, data export, delete.
11. **Error messages must be safe** — no stack traces, no internal details.
12. **Portal session tokens must be rotated** — on login, password change, privilege change.
13. **Session binding to IP is optional** — configurable per portal security policy.
14. **Portal data export must respect field permissions** — masked fields stay masked in export.
15. **Portal user cannot bypass system permissions** — portal access is a subset of system access.

### Guest/public security rules

1. **Guest has no CRUD access** by default — only explicitly public resources.
2. **Guest file upload is disabled by default** — must be explicitly enabled per form.
3. **Guest delete/update is never allowed** — not even with tokens.
4. **Public API access must be explicitly enabled** — per endpoint.
5. **Guest sessions are lightweight** — no persistent storage of sensitive data.
6. **Public forms must have captcha option** — anti-bot protection.

## 19. Runtime metadata needed

### Portal metadata objects

| Object | Table | Purpose |
|--------|-------|---------|
| Portal | `tabPortal` | Portal instance configuration |
| Portal Theme | `tabPortalTheme` | Portal theme definition |
| Portal Page | `tabPortalPage` | Page with sections and components |
| Portal Page Section | `tabPortalPageSection` | Page section layout |
| Portal Component | `tabPortalComponent` | Reusable component instance |
| Portal Menu Item | `tabPortalMenuItem` | Navigation menu item |
| Portal Role | `tabPortalRole` | Portal role definition |
| Portal User | `tabPortalUser` | Portal user identity |
| Portal Profile Link | `tabPortalProfileLink` | User-to-record ownership link |
| Portal Permission | `tabPortalPermission` | CRUD + action per DocType per role |
| Portal Field Permission | `tabPortalFieldPermission` | Field-level read/write per role |
| Portal Dashboard | `tabPortalDashboard` | Dashboard layout and config |
| Portal Dashboard Widget | `tabPortalDashboardWidget` | Widget instance on a dashboard |
| Portal Public Action | `tabPortalPublicAction` | Public action/ form definition |
| Portal Notification | `tabPortalNotification` | Notification record |
| Portal Share Link | `tabPortalShareLink` | Shareable record link |
| Portal Access Token | `tabPortalAccessToken` | Time-limited access token |
| Portal Activity Log | `tabPortalActivityLog` | Audit log for portal actions |

### Website/public metadata objects

| Object | Table | Purpose |
|--------|-------|---------|
| Website Page | `tabWebsitePage` | Public page content |
| Website Route | `tabWebsiteRoute` | Custom route mapping |
| Website Theme | `tabWebsiteTheme` | Website theme (subset of portal theme) |
| Website Menu | `tabWebsiteMenu` | Public navigation menu |
| Public Form | `tabPublicForm` | Public form configuration |
| Public Action | `tabPublicAction` | Public action definition |
| SEO Settings | `tabSEOSettings` | Global SEO configuration |
| Redirect Rule | `tabRedirectRule` | URL redirect rules |

## 20. Implementation phases

### Phase 1 (Current)
- Architecture document (this document)
- Folder structure created: `portal/`, `website/`, `www/`, `public/`
- Update Doc 18 (package folder map)
- Update Doc 23 (exposure targeting — Desk, Studio, Portal, Website)
- Update Doc 24 (portal theme support)
- Update Doc 26 (portal i18n/RTL/icons)

### Phase 2 — Portal foundation
- `PortalUser` metadata model and table
- `PortalRole` and `PortalPermission` metadata
- Portal login/signup/auth flow
- Portal session management
- Portal route registration (`/portal/*`)
- Portal API prefix (`/api/portal/*`)
- Tests: portal auth, portal permissions

### Phase 3 — Portal data access
- `PortalProfileLink` metadata — ownership linking
- Portal CRUD API — `/api/portal/resource/{doctype}`
- Portal field permission evaluation
- Portal record access filtering (ownership, links, visibility)
- `PortalDocTypePermission` evaluation engine
- Tests: portal CRUD, field permissions, ownership filtering

### Phase 4 — Portal dashboard and widgets
- `PortalDashboard` metadata
- `PortalDashboardWidget` metadata
- Widget types: stat, chart, list, card, action, shortcut, notification, embed
- Dashboard layout and grid system
- Widget data source resolution
- Tests: dashboard CRUD, widget rendering

### Phase 5 — Portal theme system
- `PortalTheme` metadata and CRUD
- CSS variable generation from theme
- Theme resolution per user/role/portal/page
- Portal theme customization UI
- Dark mode support
- Tests: theme resolution, CSS generation, dark mode

### Phase 6 — Portal pages and page builder
- `PortalPage` metadata
- Page section and component model
- Page rendering pipeline
- Component types: hero, card, data list, form, chart, timeline
- Page visibility and permissions
- SEO metadata for portal pages
- Tests: page CRUD, rendering, visibility

### Phase 7 — Portal profile and account
- Profile view/edit endpoints
- Avatar upload
- Password change
- Language and notification preferences
- Privacy settings
- Account deletion (if allowed)
- Tests: profile CRUD, password change, preferences

### Phase 8 — Public interaction layer
- `PublicForm` metadata
- `PublicAction` metadata
- Public form submission handler
- Public action execution
- Captcha/anti-spam integration
- Rate limiting for public endpoints
- `PublicViewRule` for DocType public exposure
- `PublicAccessToken` for token-gated access
- Tests: public forms, public actions, rate limiting, tokens

### Phase 9 — Notification system
- `PortalNotification` metadata
- Notification delivery (in-app, email)
- Notification preferences per user
- Notification list widget
- Tests: notification creation, delivery, preferences

### Phase 10 — Portal marketplace support
- Listing and seller/buyer metadata
- Marketplace dashboard widgets
- Public listing page
- Inquiry/offer flow (tbd)

### Phase 11 — Portal queue/chat/workflow support
- Queue token and status metadata
- Chat conversation and message metadata
- Workflow task view metadata
- Portal widgets for each system

### Phase 12 — Portal social/community support
- Feed, post, comment, reaction metadata
- Community group and membership
- Moderation queue
- Reputation/badges (future)

### Phase 13 — AI-assisted portal
- AI suggestion endpoints (permission-aware)
- Natural language portal content generation
- Smart search integration
- Chat summarization

### Phase 14 — Blockchain/dapp integration
- Wallet connection metadata (future)
- Signature verification service (future)
- Token-gated access middleware (future)
- Portal dapp page type (future)

## 21. Risks and boundaries

| Risk | Mitigation |
|------|------------|
| Portal permission complexity | Use metadata-driven permission rules with clear defaults (deny-first) |
| Cross-world data leakage | Separate route/API/permission stacks; verify world membership per request |
| Theme CSS injection | Sanitize all custom CSS; strip script tags and url() injections |
| Public form spam | Rate limiting + optional captcha + moderation queue |
| Portal session hijacking | Rotate session ID on login; optional IP binding; short expiry for sensitive actions |
| File upload abuse | Validate type, size, content; scan for malware (future); per-role upload limits |
| Blockchain integration risk | Never store private keys; never ask for seed phrases; all actions require confirmation |
| AI permission bypass | AI operates within existing permission boundaries; no special AI elevation |
| Performance under heavy widget loads | Widget-level caching; configurable refresh intervals; lazy loading |
| Portal marketplace fraud | Moderation queue; verification badges; dispute workflow; audit trail |
