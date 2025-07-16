import os
import json
import hashlib
import requests
import pyodbc
from datetime import datetime, timezone
from dotenv import load_dotenv
from dagster import op, job, get_dagster_logger

# Load environment variables
load_dotenv()

# Credentials from env or hardcoded config
SQL_CREDS = {
    'PG_SERVER': os.getenv('PG_SERVER'),
    'PG_PORT': os.getenv('PG_PORT', '5432'),
    'PG_DB': os.getenv('PG_DB'),
    'PG_USER': os.getenv('PG_USER'),
    'PG_PWD': os.getenv('PG_PWD'),
    'PG_SCHEMA': os.getenv('PG_SCHEMA', 'public')
}

API_CREDS = {
    'ACCESS_TOKEN': os.getenv('SPOTIFY_ACCESS_TOKEN'),
    'REFRESH_TOKEN': os.getenv('SPOTIFY_REFRESH_TOKEN'),
    'CLIENT_ID': os.getenv('SPOTIFY_CLIENT_ID'),
    'CLIENT_SECRET': os.getenv('SPOTIFY_CLIENT_SECRET'),
    'OAUTH_URL': os.getenv('SPOTIFY_OAUTH_URL', 'https://accounts.spotify.com/api/token'),
    'REST_URL': os.getenv('SPOTIFY_REST_URL', 'https://api.spotify.com/v1')
}

BI_META = {
    'BI_STAGING_TABLE': os.getenv('BI_STAGING_TABLE', 'spotify_usage'),
    'BI_LOG_TABLE': os.getenv('BI_LOG_TABLE', 'etl_log'),
    'BI_SERVICE_NAME': os.getenv('BI_SERVICE_NAME', 'spotify_etl'),
    'BI_INGEST_TS': 'played_at'
}

# --- Ops ---

def refresh_access_token(refresh_token):
    logger = get_dagster_logger()
    logger.info("Refreshing Spotify token...")

    res = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        auth=(API_CREDS['CLIENT_ID'], API_CREDS['CLIENT_SECRET']),
    )

    if res.status_code != 200:
        raise Exception(f"Token refresh failed: {res.text}")

    access_token = res.json()["access_token"]
    return access_token

@op
def get_sql_conn():
    logger = get_dagster_logger()
    logger.info(f"Connecting to DB")
    return pyodbc.connect(
        f"DRIVER={{PostgreSQL Unicode}};"
        f"SERVER={SQL_CREDS['PG_SERVER']},{SQL_CREDS['PG_PORT']};"
        f"DATABASE={SQL_CREDS['PG_DB']};"
        f"UID={SQL_CREDS['PG_USER']};"
        f"PWD={SQL_CREDS['PG_PWD']}"
    )

@op
def get_latest_timestamp(conn):
    logger = get_dagster_logger()
    cursor = conn.cursor()
    cursor.execute(f"SELECT COALESCE(MAX(event_time), '2025-06-30') FROM {SQL_CREDS['PG_SCHEMA']}.{BI_META['BI_STAGING_TABLE']}")
    result = cursor.fetchone()
    return result[0] if result else datetime(2025, 6, 30)

@op
def get_recent_tracks():
    logger = get_dagster_logger()
    access_token = API_CREDS['ACCESS_TOKEN']
    refresh_token = API_CREDS['REFRESH_TOKEN']

    def fetch(token):
        return requests.get(
            "https://api.spotify.com/v1/me/player/recently-played?limit=5",
            headers={"Authorization": f"Bearer {token}"}
        )

    res = fetch(access_token)
    if res.status_code == 401 and res.json().get("error", {}).get("message") == "The access token expired":
        access_token = refresh_access_token(refresh_token)
        res = fetch(access_token)

    if res.status_code != 200:
        raise Exception(f"Spotify API Error: {res.status_code} - {res.text}")
    
    for i, item in enumerate(res.get("items", [])):
        track = item["track"]
        logger.info(f"{i+1}. {track['name']} – {track['artists'][0]['name']} @ {item['played_at']}")
        
    return access_token

@op
def fetch_usage_data(timestamp_ms: int, token: str):
    logger = get_dagster_logger()
    base_url = f"{API_CREDS['REST_URL']}/me/player/recently-played"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"after": timestamp_ms, "limit": 20}
    rows = []
    url = base_url
    counter = 1

    while url:
        logger.info(f"Page_{counter:02d}")
        resp = requests.get(url, headers=headers, params=params if counter == 1 else None)
        resp.raise_for_status()
        data = resp.json()
        rows.extend(data.get("items", []))
        url = data.get("next")
        params = None
        counter += 1

    return rows

@op
def sanitize_json(rows):
    for item in rows:
        track = item.get("track", {})
        track.pop("available_markets", None)
        album = track.get("album", {})
        album.pop("available_markets", None)
    return rows

@op
def hash_row(row):
    return hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()

@op
def insert_new_data(conn, rows):
    logger = get_dagster_logger()
    cursor = conn.cursor()
    inserted_count, duplicate_count = 0, 0
    max_tf_ts = datetime(2025, 6, 30, tzinfo=timezone.utc)

    for row in rows:
        tf_ts_str = row.get(BI_META['BI_INGEST_TS'])
        if not tf_ts_str:
            continue
        try:
            tf_ts = datetime.fromisoformat(tf_ts_str.replace("Z", "+00:00"))
        except ValueError:
            continue

        hash_val = hash_row(row)
        data_str = json.dumps(row)

        cursor.execute(f"SELECT 1 FROM {SQL_CREDS['PG_SCHEMA']}.{BI_META['BI_STAGING_TABLE']} WHERE hash = ?", (hash_val,))
        if cursor.fetchone():
            duplicate_count += 1
            continue

        cursor.execute(
            f"INSERT INTO {SQL_CREDS['PG_SCHEMA']}.{BI_META['BI_STAGING_TABLE']} (event_time, data_json, hash) VALUES (?, ?, ?)",
            (tf_ts, data_str, hash_val)
        )
        inserted_count += 1
        if not max_tf_ts or tf_ts > max_tf_ts:
            max_tf_ts = tf_ts

    conn.commit()
    logger.info(f"{inserted_count} inserted, {duplicate_count} duplicates")
    return inserted_count, max_tf_ts

@op
def log_etl_result(conn, success: bool, inserted_rows: int, max_ts):
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT INTO {SQL_CREDS['PG_SCHEMA']}.{BI_META['BI_LOG_TABLE']} (run_time, service_name, success, inserted_rows, max_event_time) VALUES (?, ?, ?, ?, ?)",
        (datetime.now(timezone.utc), BI_META['BI_SERVICE_NAME'], success, inserted_rows, max_ts)
    )
    conn.commit()

@job
def spotify_usage_etl():
    conn = get_sql_conn()
    latest_ts = get_latest_timestamp(conn)
    token = get_recent_tracks()
    raw_data = fetch_usage_data(int(latest_ts.timestamp() * 1000), token)
    cleaned = sanitize_json(raw_data)
    inserted, max_ts = insert_new_data(conn, cleaned)
    log_etl_result(conn, True, inserted, max_ts)
