# Running the site: backups, crash reports and a test copy

Everything here works on free tiers. Nothing needs a paid plan.

## Where the data lives

All accounts, projects, saved models and uploaded files are in **one PostgreSQL database** (the `DATABASE_URL` setting). The web service itself keeps nothing on disk, so it can be rebuilt at any time. Losing the database is the only way to lose data, so that is what to back up.

## Back up the database

Run this on your own computer, which needs the PostgreSQL client tools (`pg_dump`). Use the connection string from your database provider:

```powershell
pg_dump --format=custom --no-owner --file="fis-backup-$(Get-Date -Format yyyy-MM-dd).dump" "<your DATABASE_URL>"
```

- Do it **weekly**, and before every upgrade that changes the database (a new file in `backend/migrations/versions`).
- The dump includes uploaded files, so it can be large. Keep the last four and delete older ones.
- Store dumps somewhere other than the computer that made them (a cloud drive is fine). They contain personal data, so keep them private.
- Neon's free tier also keeps a short history you can restore from in its console. Treat that as a second line of defence, not the only one: its window is short.

## Rehearse a restore (once, before you need it)

A backup you have never restored is a hope, not a backup. Make an empty second database (a free Neon branch or project works) and run:

```powershell
pg_restore --no-owner --clean --if-exists --dbname="<the empty database's URL>" fis-backup-2026-01-01.dump
```

Then point a local copy of the app at it (`DATABASE_URL=...` in `backend/.env`), sign in, and open a saved model. If that works, the backup is good.

To restore for real: restore into the production database the same way, then redeploy so the service reconnects. Run `uv run alembic upgrade head` from `backend` if the dump is older than the code.

## Crash reports

If a page fails while drawing, the visitor sees a calm message and the browser sends a short note to the server (`POST /api/client-errors`): the error text, the page path with no query string, a short stack and the version. No account details are sent, nothing is stored in the database, and each address may send ten an hour.

Read them in the service log (Render: your service, then **Logs**). Search for `fis.client`. Each line looks like:

```
ERROR fis.client Browser error on /dcf (v0.14.0): TypeError: x is undefined | at Dcf ...
```

Feedback sent with the in-app button is separate: `python -m app.tools.show_feedback` lists it.

## A test copy before changes go live ("staging")

Do this by hand so nothing extra is created by accident when the Blueprint is applied:

1. In Render choose **New, Web Service**, pick this repository and the branch you are testing (for example `staging`), and use the same Dockerfile.
2. Give it its **own database**: a second free Neon project. Never point a test copy at the real database.
3. Set `FIS_ENV=production`, `FIS_ALLOW_REGISTRATION=true` and the new `DATABASE_URL`. Leave payment and AI keys blank.
4. Push the change to that branch, try it, and merge to `main` only when it looks right.

The GitHub checks (tests, browser tests, audits) already run on every push; the test copy is for looking at it with your own eyes.

## Checklist after each release

- `GET /api/health` returns the new version number.
- Sign in, open a saved model, and download **Settings, Export saved models (Excel)**.
- The service log has no new `fis.client` errors an hour later.
