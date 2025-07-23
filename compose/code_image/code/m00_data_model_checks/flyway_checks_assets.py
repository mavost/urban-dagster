from subprocess import run, CalledProcessError
import os
from pathlib import Path
from dotenv import load_dotenv
from dagster import asset, DynamicPartitionsDefinition, AssetExecutionContext

from dagster import RunRequest, sensor, AssetKey

# Load environment variables
load_dotenv(dotenv_path=Path(os.getenv("DAGSTER_HOME", ".")) / ".env")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLYWAY_CONF_DIR = os.path.join(BASE_DIR, "flyway_spotify_sink")

# Define dynamic environments — this allows per-env runs
flyway_env_partitions = DynamicPartitionsDefinition(name="flyway_envs")


@asset(partitions_def=flyway_env_partitions, tags={"module": "m00_data_model_checks"})
def flyway_current_state(context: AssetExecutionContext):
    env = context.partition_key
    context.log.info(f"Running Flyway INFO for: {env}")
    config_path = os.path.join(FLYWAY_CONF_DIR, f"flyway_{env}.conf")

    try:
        result = run(
            ["flyway", f"-configFiles={config_path}", "info", "-skipCheckForUpdate"],
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


@asset(partitions_def=flyway_env_partitions, deps=["flyway_current_state"], tags={"module": "m00_data_model_checks"})
def flyway_migrate(context: AssetExecutionContext):
    env = context.partition_key
    context.log.info(f"Running Flyway MIGRATE for: {env}")
    config_path = os.path.join(FLYWAY_CONF_DIR, f"flyway_{env}.conf")

    try:
        result = run(
            ["flyway", f"-configFiles={config_path}", "migrate", "-skipCheckForUpdate"],
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
