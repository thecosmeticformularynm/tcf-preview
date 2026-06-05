# Access & Roles — "let people in without handing over the company"

This is the document that answers Pauly's requirement directly: a developer (or staff, or
client) can log in and do their job, and **nothing more**. Least privilege, by design.

## App roles (who sees what inside the platform)
| Role | Can see / do | Cannot |
|---|---|---|
| **Owner** (Pauly) | Everything: all brands, all data, billing, user management | — |
| **Staff — Office** | Back office: orders, clients, inventory, batches | Billing, deleting users, secrets |
| **Staff — Lab/Warehouse** | Inventory + batch records only (phone-friendly) | Client pricing, finances, other brands' contracts |
| **Client** (per brand) | Their portal only: their products, orders, batch status, docs | Any other brand; any back-office data |
| **Developer** | Code + staging environment; deploy via pipeline | Production database, real customer data, secrets, billing |

## Code/infrastructure access (GitHub + hosting)
The fix for the exposed-token problem. Nobody gets a personal key in a file again.

1. **Company GitHub Organization** (owned by `pauly@thecosmeticformulary.com`), not a personal account.
   - Repos live in the org. Pauly is **Owner**.
   - A developer is added to a **`developers` team** with *write to code repos only* — not org-admin,
     not billing, removable in one click when an engagement ends.
2. **Secrets** (API keys, DB passwords) live in **environment variables / a secrets manager** on the
   host — *never* in the repo. A developer can deploy without ever seeing production secrets.
3. **Two environments:** `staging` (safe to break, fake data) and `production` (real). Developers
   work in staging; promotion to production is gated.
4. **Audit:** every login and admin action is logged.

## Onboarding a developer = 4 clicks, zero risk
1. Invite their GitHub account to the org `developers` team.
2. Give them the staging URL + a staging test login.
3. They read `README.md` → `ARCHITECTURE.md` → `RUNBOOK.md`.
4. Done. No passwords shared. Remove them anytime by removing them from the team.

## Immediate to-do (security)
- [ ] **Revoke the exposed personal access token `ghp_oXS0…`** on the `thecosmeticformularynm` account.
- [ ] Create the company GitHub **Organization**; move the repo into it.
- [ ] Re-connect the repo with a credential helper (no token in any file).
