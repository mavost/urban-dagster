-- V1__baseline_init.sql

CREATE SCHEMA IF NOT EXISTS ${schema};

GRANT USAGE ON SCHEMA ${schema} TO spotify_user;
GRANT CREATE ON SCHEMA ${schema} TO spotify_user;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ${schema} TO spotify_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA ${schema}
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO spotify_user;

CREATE TABLE ${schema}.staging_playback_data (
    event_time TIMESTAMPTZ,
    data_json TEXT,
    hash CHAR(64)
);

CREATE UNIQUE INDEX idx_hash_unique ON ${schema}.staging_playback_data (hash);

CREATE TABLE ${schema}.etl_log (
    run_time TIMESTAMP,
    service_name VARCHAR(30),
    success BOOLEAN,
    inserted_rows INTEGER,
    max_event_time TIMESTAMP
);
