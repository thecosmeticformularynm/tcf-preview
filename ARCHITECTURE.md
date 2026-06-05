# Architecture

Plain-English first, technical second. Written so a new developer — or future Pauly —
can understand the whole system in 10 minutes.

## The big picture
One platform, three front doors, one shared brain:

```
        PUBLIC                    LOGGED-IN CLIENTS              YOUR TEAM
   ┌──────────────┐            ┌────────────────────┐      ┌──────────────────┐
   │  Storefront  │            │   Client Portal    │      │   Back Office    │
   │  index.html  │            │   portal.html      │      │   admin.html     │
   │  marketing   │            │  (only THEIR brand)│      │  (everything)    │
   └──────┬───────┘            └─────────┬──────────┘      └────────┬─────────┘
          │                              │                          │
          └──────────────┬──────────────┴────────────┬─────────────┘
                         ▼                            ▼
                 ┌───────────────┐          ┌──────────────────────┐
                 │  Login + roles│          │  Database (one)       │
                 │  who are you, │          │  brands, products,    │
                 │  what brand,  │          │  inventory/lots,      │
                 │  what you see │          │  orders, batches      │
                 └───────────────┘          └──────────┬───────────┘
                                                       ▼
                                          Nightly CSV export → Google Drive
                                          (the backup / insurance policy)
```

## Multi-tenant rule (the important one)
Every record is stamped with a **brand**. A client login can only ever read/write rows
for their own brand. Daily Rou cannot see Halo42, and vice-versa. The back office sees all.
This is enforced on the **server**, not the page — a client can never "peek" by editing the browser.

## Tech direction (pragmatic, boring on purpose)
- **Front-end:** the existing HTML/CSS design system (Fraunces + Inter). Keep it.
- **Back-end:** small Python web app (Flask/FastAPI) — Python is already on the Macs and a
  prototype (`Daily Rou — Client Portal/app.py`) already exists to fold in.
- **Database:** start SQLite → move to Postgres (Fly Postgres) as it grows.
- **Hosting:** Fly.io (already used for `formulary-os.fly.dev`). Production + staging.
- **Auth:** email + password (hashed) or magic-link; every account has a **role** and a **brand**.
- **Backups:** nightly job writes CSVs to the Drive "Inventory System (Live Data)" folders.

## How the existing pieces map in
- `tcf-preview` mockups (storefront/portal/back office) → become the real screens.
- `Formulary-Inventory-Prototype.html` → becomes the **Inventory** module of the back office.
- `Daily Rou — Client Portal/app.py` → folded in as the **first real client tenant**, not a separate app.

## What is NOT in this platform
- **Accounting / taxes → stays in QuickBooks.** We integrate/report against it; we do not replace it.
