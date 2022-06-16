import os
from pathlib import Path
from dotenv import dotenv_values, load_dotenv as load_from_dotenv

envs_dir = Path(__file__).parent.joinpath("envs").resolve()
root_dir = envs_dir.joinpath("../../../..").resolve()

env_type = os.getenv("ENV_TYPE", "local")
is_local = env_type == "local"

config = {
    **dotenv_values(envs_dir.joinpath(f"base.env")),
    **dotenv_values(envs_dir.joinpath(f"{env_type}.env")),
    **dotenv_values(root_dir.joinpath(".env")),
    **os.environ,
}

config["env_type"] = env_type
config["is_local"] = env_type == "local"

def load_dotenv(env_type):
    load_from_dotenv(envs_dir.joinpath(f"base.env"))
    load_from_dotenv(envs_dir.joinpath(f"{env_type}.env"))
    load_from_dotenv(root_dir.joinpath(".env"))
