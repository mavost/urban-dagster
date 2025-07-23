from dagster import Definitions

from m00_data_model_checks import flyway_checks_assets
from m10_interface_etls.initial_etl import hello_job
from m10_interface_etls.spotify_etl import spotify_usage_etl
from m10_interface_etls.spotify_logoutput import spotify_logoutput_etl


all_jobs = [
    hello_job,
    spotify_usage_etl,
    spotify_logoutput_etl,
]

defs = Definitions(
    assets=[flyway_checks_assets.flyway_current_state, flyway_checks_assets.flyway_migrate],
    sensors=[flyway_checks_assets.promote_flyway_partitions],
    jobs=all_jobs,
)
