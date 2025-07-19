-- V1__baseline_init.sql

CREATE SCHEMA IF NOT EXISTS dev;

GRANT USAGE ON SCHEMA dev TO spotify_user;
GRANT CREATE ON SCHEMA dev TO spotify_user;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA dev TO spotify_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA dev
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO spotify_user;

CREATE TABLE dev.staging_playback_data (
    event_time TIMESTAMPTZ,
    data_json TEXT,
    hash CHAR(64)
);

CREATE UNIQUE INDEX idx_hash_unique ON dev.staging_playback_data (hash);

CREATE TABLE dev.etl_log (
    run_time TIMESTAMP,
    service_name VARCHAR(30),
    success BOOLEAN,
    inserted_rows INTEGER,
    max_event_time TIMESTAMP
);
