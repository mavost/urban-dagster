# repo.py
from dagster import Definitions
from m00_data_model_checks.flyway_checks import m00_flyway_spotify_sink
from m10_interface_etls.initial_etl import m10_hello_job
from m10_interface_etls.spotify_etl import m10_spotify_usage_etl
from m10_interface_etls.spotify_logoutput import m10_spotify_logoutput_etl

#from etl.another_pipeline import another_job
#from 00_data_model_checks.flyway_checks import flyway_validation_job

all_jobs = [
    m00_flyway_spotify_sink,
    m10_hello_job,
    m10_spotify_usage_etl,
    m10_spotify_logoutput_etl,
#    another_job,
]

defs = Definitions(
    jobs=all_jobs,
    # Optionally add schedules, sensors, assets here
)