# Flyway checks

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

## Create sink database

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

-- As spotify_user: Create a sink and etl_log tables
-- The user becomes owner, can maipulate data and can alter the tables using flyway
CREATE TABLE dev.staging_playback_data (
    event_time TIMESTAMPTZ,
    data_json TEXT,
    hash CHAR(64)
);

CREATE UNIQUE INDEX idx_hash_unique ON dev.staging_playback_data (hash);

CREATE TABLE dev.etl_log (
    run_time TIMESTAMPTZ,
    service_name VARCHAR(30),
    success BOOLEAN,
    inserted_rows INTEGER,
    max_event_time TIMESTAMPTZ
);

```
