import subprocess
import os
from pathlib import Path
from dotenv import load_dotenv
from dagster import job, op, Config

# Load environment from .env file (once at module import time)
load_dotenv(dotenv_path=Path(os.getenv("DAGSTER_HOME", ".")) / ".env")

class FlywayConfig(Config):
    env: str  # "dev", "test", or "prod"

def _config_path(env: str) -> str:
    return f"spotify-metadata-flyway/flyway_{env}.conf"

@op(config_schema=FlywayConfig.to_config_schema())
def flyway_current_state(context):
    env = context.op_config["env"]
    config_path = _config_path(env)
    context.log.info(f"Running Flyway INFO for: {env}")
    subprocess.run(["flyway", f"-configFiles={config_path}", "info"], check=True)

@op(config_schema=FlywayConfig.to_config_schema())
def flyway_migrate(context):
    env = context.op_config["env"]
    config_path = _config_path(env)
    context.log.info(f"Running Flyway MIGRATE for: {env}")
    subprocess.run(["flyway", f"-configFiles={config_path}", "migrate"], check=True)

@job
def flyway_spotify_sink():
    for env in ["dev"]:#, "test", "prod"]:
        verify = flyway_current_state.configured({"env": env})
        apply = flyway_migrate.configured({"env": env})
        verify >> apply
