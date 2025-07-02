-- log in as admin
CREATE DATABASE dagster_metadata;

CREATE USER dagster_user WITH PASSWORD <your_secure_password>;

GRANT CONNECT ON DATABASE dagster_metadata TO dagster_user;

--switch to dagster_metadata
--\c dagster_metadata
-- Allow use of the schema
GRANT USAGE ON SCHEMA public TO dagster_user;
-- Allow CREATE on the schema itself (for creating new tables, etc.)
GRANT CREATE ON SCHEMA public TO dagster_user;

-- Grant typical DML privileges on existing tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO dagster_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO dagster_user;
