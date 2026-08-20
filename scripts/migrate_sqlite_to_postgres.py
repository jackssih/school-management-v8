#!/usr/bin/env python3
"""Copy the current V8 SQLite demo data into a fresh PostgreSQL database.

Run from the project root after the Render PostgreSQL database exists:
    DATABASE_URL='postgresql://...' python scripts/migrate_sqlite_to_postgres.py

The script never deletes target data. It expects an empty PostgreSQL database.
"""
import argparse
import os
import sqlite3

from sqlalchemy import create_engine, insert, inspect, text

from models import Base


def normalize_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="instance/school_management.db")
    parser.add_argument("--target", default=os.getenv("DATABASE_URL"))
    args = parser.parse_args()
    if not args.target:
        raise SystemExit("Set DATABASE_URL or pass --target with the Render PostgreSQL connection string.")
    if not os.path.exists(args.source):
        raise SystemExit(f"SQLite database not found: {args.source}")

    source = sqlite3.connect(args.source)
    source.row_factory = sqlite3.Row
    target = create_engine(normalize_url(args.target), pool_pre_ping=True)

    # Ensure the SQLAlchemy schema exists. In Render this is normally already
    # handled by `flask db upgrade`; create_all is harmless on an empty DB and
    # makes this script useful outside Render too.
    Base.metadata.create_all(target)

    target_inspector = inspect(target)
    source_tables = {
        row[0]
        for row in source.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }

    # SQLAlchemy's dependency ordering ensures parent rows exist before child
    # rows and puts association tables after both sides of their relationships.
    tables = [t for t in Base.metadata.sorted_tables if t.name in source_tables]

    with target.begin() as conn:
        # The schema itself is expected to exist; we only refuse if any app table
        # already contains data, avoiding accidental duplicate imports.
        for table in tables:
            if not target_inspector.has_table(table.name):
                continue
            count = conn.execute(text(f'SELECT COUNT(*) FROM "{table.name}"')).scalar_one()
            if count:
                raise SystemExit(
                    f'Target table "{table.name}" already contains {count} rows. '
                    'Use a fresh PostgreSQL database for the initial migration.'
                )

        for table in tables:
            columns = [c.name for c in table.columns]
            rows = source.execute(
                f'SELECT {", ".join(chr(34)+c+chr(34) for c in columns)} FROM "{table.name}"'
            ).fetchall()
            if not rows:
                continue
            payload = [dict(zip(columns, tuple(row))) for row in rows]
            conn.execute(insert(table), payload)
            print(f"Imported {len(payload):5d} rows into {table.name}")

        # Explicit IDs bypass PostgreSQL's identity sequences. Reset each simple
        # integer `id` sequence so the next application insert gets the right ID.
        for table in tables:
            pk = list(table.primary_key.columns)
            if len(pk) != 1 or pk[0].name != "id" or not str(pk[0].type).lower().startswith("integer"):
                continue
            max_id = conn.execute(text(f'SELECT MAX(id) FROM "{table.name}"')).scalar_one()
            if max_id is not None:
                conn.execute(text(
                    "SELECT setval(pg_get_serial_sequence(:table_name, 'id'), :max_id, true)"
                ), {"table_name": table.name, "max_id": max_id})

    source.close()
    target.dispose()
    print("\nMigration complete. PostgreSQL now contains the V8 SQLite data.")


if __name__ == "__main__":
    main()
