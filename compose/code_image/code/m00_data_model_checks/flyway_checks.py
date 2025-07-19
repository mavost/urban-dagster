from subprocess import run, CalledProcessError
import os
from pathlib import Path
from dotenv import load_dotenv
from dagster import job, graph, op, Config, DynamicOut, DynamicOutput

# Load environment from .env file (once at module import time)
load_dotenv(dotenv_path=Path(os.getenv("DAGSTER_HOME", ".")) / ".env")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLYWAY_CONF_DIR = os.path.join(BASE_DIR, "spotify-metadata-flyway")

class FlywayConfig(Config):
    env: str  # "dev", "test", or "prod"

# Return dynamic envs as Dagster DynamicOutput
@op(out=DynamicOut(str))
def list_envs():
    for env in ["dev"]: # , "test", "prod"
        yield DynamicOutput(env, mapping_key=env)

@op
def flyway_current_state(context, env: str):
    context.log.info(f"Running Flyway INFO for: {env}")
    config_path = os.path.join(FLYWAY_CONF_DIR, f"flyway_{env}.conf")
    try:
        result = run(
            ["flyway", f"-configFiles={config_path}", "info"],
            capture_output=True,
            text=True,
            check=True
        )
        context.log.info(f"Flyway stdout:\n{result.stdout}")
        if result.stderr:
            context.log.warning(f"Flyway stderr:\n{result.stderr}")
    except CalledProcessError as e:
        context.log.error(f"Flyway command failed with exit code {e.returncode}")
        context.log.error(f"Command: {e.cmd}")
        context.log.error(f"stdout:\n{e.stdout}")
        context.log.error(f"stderr:\n{e.stderr}")
        raise
    return env  # Pass to next op

@op
def flyway_migrate(context, env: str):
    context.log.info(f"Running Flyway MIGRATE for: {env}")
    config_path = os.path.join(FLYWAY_CONF_DIR, f"flyway_{env}.conf")
    try:
        result = run(
            ["flyway", f"-configFiles={config_path}", "-X", "migrate"],
            capture_output=True,
            text=True,
            check=True
        )
        context.log.info(f"Flyway stdout:\n{result.stdout}")
        if result.stderr:
            context.log.warning(f"Flyway stderr:\n{result.stderr}")
    except CalledProcessError as e:
        context.log.error(f"Flyway command failed with exit code {e.returncode}")
        context.log.error(f"Command: {e.cmd}")
        context.log.error(f"stdout:\n{e.stdout}")
        context.log.error(f"stderr:\n{e.stderr}")
        raise

@graph
def run_flyway_ops(env: str):
    flyway_migrate(flyway_current_state(env))

@graph
def flyway_for_env():
    list_envs().map(run_flyway_ops)

@job
def flyway_spotify_sink():
    flyway_for_env()
