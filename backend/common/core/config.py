import os
from pathlib import Path
from dotenv import dotenv_values


envs_dir = Path(__file__).parent.joinpath("envs").resolve()
root_dir = envs_dir.joinpath("../../../..").resolve()

env_type = os.getenv("ENV_TYPE", "dev")

config = {
    **dotenv_values(envs_dir.joinpath(f"base.env")),
    **dotenv_values(envs_dir.joinpath(f"{env_type}.env")),
    **dotenv_values(root_dir.joinpath(".env")),
    **os.environ,
}
