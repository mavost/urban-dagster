# Introduction to Flyway: data model consistency checking and migration management

Flyway is a java/maven based lightweight dat model management tool. As time progresses in any data engineering project,
interface definitions and requirements change. The tool can help to ensure the integrity of source and sink data structures
to clear the path for ETL/ELT loading processes.

*Date:* 2025-07-02  
*Author:* MvS  
*keywords:* etl/elt orchestration, flyway, data modelling, consistency checking

## Project layout

dagster_app_root/
├── m00_data_model_checks/
│   ├──flyway_checks.py            # contains the Dagster job + ops
│   └── spotify-metadata-flyway/
│       ├── flyway_dev.conf
│       ├── flyway_test.conf
│       ├── flyway_prod.conf
│       └── sql/
│           ├── V1__baseline.sql
│           └── V2__add_errorcode.sql
└── repo.py                        # Dagster entrypoint

repository_root/
├── docker-compose.yaml
├── source2sink_envs
│   └── .env                       # holds API and DB creds, metadata
└── .env                           # holds Dagster creds

## Database setup

1. Create database shell, user and permissions

2. Ensure that the relevant schemas are in place as this is requires extended permissions and 
usually handled by an admin user, e.g.: `CREATE SCHEMA IF NOT EXISTS dev;`

3. An example script is provided below based on Postgres DB syntax:

```sql
-- As admin: Create a dedicated metadata database for REST API ingestion
CREATE DATABASE spotify_metadata;

-- Create a user account for the sink system (e.g. ingestion pipeline)
CREATE USER spotify_user WITH PASSWORD 'FFtrwmo4---fgd&645';

-- Grant basic connection privileges
GRANT CONNECT ON DATABASE spotify_metadata TO spotify_user;

-- 🆕 Switch to the spotify_metadata DB, then create schema first
-- Run this after connecting to spotify_metadata
DO $$
DECLARE
  schema_name TEXT;
  schemas TEXT[] := ARRAY['dev', 'prod', 'test'];
BEGIN
  FOREACH schema_name IN ARRAY schemas LOOP
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I;', schema_name);
    EXECUTE format('GRANT USAGE ON SCHEMA %I TO spotify_user;', schema_name);
    EXECUTE format('GRANT CREATE ON SCHEMA %I TO spotify_user;', schema_name);
    EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA %I GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO spotify_user;', schema_name);
  END LOOP;
END
$$;

-- Grant access to the 'dev' schema
GRANT USAGE ON SCHEMA dev TO spotify_user;
GRANT CREATE ON SCHEMA dev TO spotify_user;

-- Grant schema-wide DML permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA dev TO spotify_user;

-- Ensure future tables also grant DML access to spotify_user
ALTER DEFAULT PRIVILEGES IN SCHEMA dev
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO spotify_user;
```

## Data sink setup andd migration design

1. Flyway can handle all structural changes in databases like designing and altering views, tables
and features like indexing. It is *not* used for user administration.

2. Note that flyway through orchestration can be extended to manage several environments simultaneously. Each `*.conf` files in a flyway project
configures a specific environment, URLs, credentials, etc. We assume that different schemas along the development CI/CD sequence
are used with the orchestrator and form dependencies, e.g., `dev` &rightarrow; `test` &rightarrow; `prod`.
The placeholder `${schema}` has been reserved to be pointing to database instances within a migration file.
The connection is made via the setting `flyway.placeholders.schema=<SCHEMANAME>` in each `*.conf` file.

3. Create the first migration file as the starting tables and views you need for your data sink, e.g.:

```sql
-- V1__create_etl_sink_schema.sql
-- As spotify_user: Create a sink and etl_log tables
-- The user becomes owner, can manipulate data, and can alter the tables using flyway

CREATE TABLE ${schema}.staging_playback_data (
    event_time TIMESTAMPTZ,
    data_json TEXT,
    hash CHAR(64)
);

CREATE UNIQUE INDEX idx_hash_unique ON ${schema}.staging_playback_data (hash);

CREATE TABLE ${schema}.etl_log (
    run_time TIMESTAMPTZ,
    service_name VARCHAR(30),
    success BOOLEAN,
    inserted_rows INTEGER,
    max_event_time TIMESTAMPTZ
);
```

## Initialize baseline

1. Run the flyway initialization for each environment once *before* scheduling regular checks and migrations via Dagster.
Note: pre-existing databases need to be synced using the `flyway baseline` command. In case the first set migrations contains
the full initial data model use `flyway migrate` instead.

2. Outside of the container `cd` to the flyway project directory and execute

```bash
.\run_flyway_baseline.sh
```
