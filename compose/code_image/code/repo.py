# repo.py
from dagster import Definitions
from m00_data_model_checks.flyway_checks import flyway_spotify_sink
from m10_interface_etls.spotify_etl import spotify_usage_etl, spotify_logoutput
#from etl.another_pipeline import another_job
#from 00_data_model_checks.flyway_checks import flyway_validation_job

all_jobs = [
    spotify_usage_etl,
    spotify_logoutput,
#    another_job,
    flyway_checks,
]

defs = Definitions(
    jobs=all_jobs,
    # Optionally add schedules, sensors, assets here
)