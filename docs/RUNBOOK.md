# Runbook — how to run, deploy, and fix this

The "if Claude or any one person disappears, the company keeps going" document.
Keep it boringly literal. Update it whenever something changes.

## What you need on the master computer (one-time)
- [ ] Google Drive for Desktop (signed into `pauly@thecosmeticformulary.com`)
- [ ] Git, GitHub CLI (`gh`), and a code editor
- [ ] Python 3 (already present) + project dependencies
- [ ] Fly.io CLI (`flyctl`) for deploys
- [ ] Access to the company GitHub organization

*(None of these are installed on the laptops yet — that is what the master computer is for.)*

## Run it locally (placeholder — fill in as the backend is built)
```
# 1. get the code
git clone <org repo url>
cd the-cosmetic-formulary
# 2. install + run (commands added when the Python backend lands)
```

## View the current front-end mockups right now
Open `index.html`, `portal.html`, or `admin.html` in any browser. No install needed.

## Deploy (placeholder)
```
flyctl deploy        # production
flyctl deploy -a <staging-app>   # staging
```

## Backups — the safety net
- Live data exports to Google Drive: *TCF — Operations → Inventory System (Live Data)*.
  - `01 - Current Stock` = latest CSV. `02 - Daily Backups` = dated snapshots.
- If an app breaks, **the business still runs from those CSVs.** That is the point.

## If something is broken and no developer is available
1. Don't panic — customer/inventory data is safe in Drive as CSV.
2. The mockups (`*.html`) open in a browser with no server.
3. Call the on-call developer (see Company Foundation → Developer contract).
4. Worst case, operate from the Drive CSVs until it's fixed.

## Key facts
- Accounting/tax = **QuickBooks**, separate, untouched.
- Hosting = **Fly.io**. Code = **GitHub org**. Data backup = **Google Drive**.
