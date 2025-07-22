-- V3__remove_errorcode_from_etl_log.sql

ALTER TABLE ${schema}.etl_log
DROP COLUMN errorcode;
