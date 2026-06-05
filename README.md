# The Cosmetic Formulary — Platform

The single software platform that runs The Cosmetic Formulary (TCF): a contract
cosmetic manufacturer. One codebase, three layers, one login system with roles.

> **Status:** Foundation stage. Front-end built as working mockups; real backend
> (logins, database, roles) to be built on the master computer with developer support.
> **Do NOT cancel inFlow or any paid tool until its replacement is proven on real data.**

## The three layers
| Layer | File(s) today | Who uses it | Replaces |
|---|---|---|---|
| **Storefront** (public) | `index.html` | Anyone / prospective clients | — |
| **Client Portal** (login) | `portal.html` | Brand clients (Daily Rou, Halo42, Salt Spa…) | client emails/spreadsheets |
| **Back Office** (login) | `admin.html` | Pauly + lab/warehouse staff | inFlow ($250/mo), scattered sheets |

Each client sees **only their own brand** (multi-tenant). See `ARCHITECTURE.md`.

## First real modules (build order)
1. **Inventory** — lot # + location + on-hand (the inFlow killer). Phase 1 prototype exists.
2. **Client Portal** — Daily Rou / Meredith is Client #1, folded in from the standalone prototype.
3. Purchase orders → 4. Fulfillment → 5. BOM / batch manufacturing.

## Where things live
- **Code:** this repo → migrating to GitHub **organization** (company-owned).
- **Live data + backups:** Google Drive → *The Cosmetic Formulary — Operations → Inventory System (Live Data)*.
- **How to run / deploy / fix:** `docs/RUNBOOK.md`.
- **Who can access what:** `docs/ACCESS-AND-ROLES.md`.

## Golden rules
1. No passwords/keys in code, ever. Secrets live in environment variables. (See ACCESS-AND-ROLES.)
2. Data is exported to plain CSV on Drive continuously — the company survives even if every app dies.
3. Boring, standard, documented tech only. Anyone competent can pick it up in an afternoon.
