-- V2__add_errorcode_to_etl_log.sql

ALTER TABLE ${schema}.etl_log
ADD COLUMN errorcode TEXT;
