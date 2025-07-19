-- V2__add_errorcode_to_etl_log.sql

ALTER TABLE dev.etl_log
ADD COLUMN errorcode TEXT;
