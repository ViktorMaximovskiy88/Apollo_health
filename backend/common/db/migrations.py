from backend.common.db.init import get_motor_db, get_motor_client
from backend.common.db.settings import settings
from beanie.migrations.database import DBHandler
from beanie.migrations.runner import MigrationNode
from beanie.migrations.models import RunningMode, RunningDirections
from pathlib import Path
import logging


async def run_migrations():
    logging.basicConfig(format="%(levelname)s:\t%(message)s", level=logging.INFO)
    DBHandler.client = get_motor_client()
    DBHandler.database = get_motor_db()
    migration_dir = Path(__file__).parent.joinpath("migrations").resolve()
    root = await MigrationNode.build(migration_dir)
    mode = RunningMode(direction=RunningDirections.FORWARD, distance=0)
    await root.run(mode, False)
