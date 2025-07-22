-- V1__baseline_init.sql
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
