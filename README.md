# SQL Training: Connect and Run Queries

This repository is a simple starter for running SQL queries against a shared Supabase database.

You can use either setup path below. Both are fully supported.

## What is included

- A Codespaces setup that installs SQLTools + PostgreSQL driver
- A prefilled SQLTools connection template in Codespaces
- A `.env.example` file you can copy and fill in
- A sample query in `queries/01_verify_connection.sql`

## Option A: GitHub Codespaces (no install required)

1. Open this repository on GitHub.
2. Click **Code** -> **Codespaces** -> **Create codespace on main**.
3. In the Codespace, create your `.env` file:
   - Copy `.env.example` to `.env`
   - Fill in the credentials shared by your instructor
4. Open SQLTools in the left sidebar.
5. Use the connection named **Shared Supabase (from .env)**.
6. Open `queries/01_verify_connection.sql` and run it.
7. If you get database/user/time results, you are connected.

## Option B: Local VS Code

1. Clone this repository.
2. Open it in VS Code.
3. Install these extensions:
   - `SQLTools` (`mtxr.sqltools`)
   - `SQLTools PostgreSQL/Cockroach Driver` (`mtxr.sqltools-driver-pg`)
4. Create your `.env` file:
   - Copy `.env.example` to `.env`
   - Fill in the credentials shared by your instructor
5. In SQLTools, add a new PostgreSQL connection.
6. Copy values from `.env` into the connection fields:
   - Server = `DB_HOST`
   - Port = `DB_PORT`
   - Database = `DB_NAME`
   - Username = `DB_USER`
   - Password = `DB_PASSWORD`
7. Open `queries/01_verify_connection.sql` and run it.
8. If you get database/user/time results, you are connected.

## Environment variables

Your `.env` should include:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

## Notes

- `.env` is ignored by Git so credentials are not committed.
- If SQLTools does not show the connection right away in Codespaces, reload the VS Code window.
