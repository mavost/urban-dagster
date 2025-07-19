# repo.py
from dagster import Definitions
from m10_interface_etls.spotify_etl import spotify_usage_etl
#from etl.another_pipeline import another_job
#from 00_data_model_checks.flyway_checks import flyway_validation_job

all_jobs = [
    spotify_usage_etl,
#    another_job,
    #flyway_validation_job,
]

defs = Definitions(
    jobs=all_jobs,
    # Optionally add schedules, sensors, assets here
)