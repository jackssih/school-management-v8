# V8 PostgreSQL migration

V8 is PostgreSQL-ready but keeps SQLite as the local fallback. Render should provide `DATABASE_URL` from its PostgreSQL service.

## Deploy on Render

Use the included `render.yaml` (Blueprint) or set the web service commands manually:

- Build: `pip install -r requirements.txt && flask --app app db upgrade`
- Start: `gunicorn --workers 2 --timeout 120 app:app`
- Health check: `/health`

## Move the existing demo data

Create the Render PostgreSQL database first. Then, from the V8 project root on a machine with the V8 requirements installed:

```bash
DATABASE_URL='YOUR_RENDER_POSTGRES_CONNECTION_STRING' \
python scripts/migrate_sqlite_to_postgres.py
```

The script reads `instance/school_management.db`, creates any missing schema from the V8 models, copies all application tables in foreign-key order, and resets PostgreSQL integer ID sequences. It refuses to import into a database that already contains application rows.

For a Render-hosted migration, you can also run the same command in a temporary shell/job environment that has the repository and the SQLite file. Do not commit the PostgreSQL password into GitHub.

## After migration

Keep `DATABASE_URL` pointing at the Render PostgreSQL database. Do not set it back to SQLite in Render.
