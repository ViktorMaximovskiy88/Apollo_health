import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.joinpath("../../..").resolve()))
import logging
from pathlib import Path

from beanie.migrations.database import DBHandler
from beanie.migrations.models import RunningDirections, RunningMode
from beanie.migrations.runner import MigrationNode

from backend.common.db.init import get_motor_client, get_motor_db, init_db


async def confirm_migration_quality() -> bool:
    """Check migration log for expected structure."""
    db = get_motor_db()
    migrations = db.migrations_log
    all_current = await migrations.find({"is_current": True}).to_list(length=2)
    if not all_current:
        # This is bad, but let beanie handle
        return True
    elif len(all_current) > 1:
        logging.warn("More than one migration has is_current set to true")
        return False

    current = all_current.pop()
    migration_dir = Path(__file__).parent.joinpath("migrations").resolve()
    for modulepath in migration_dir.glob("*.py"):
        if modulepath.name == current["name"]:
            return True
    logging.warn("The current migration was not found in the directory")
    return False


async def run_migrations():
    logging.basicConfig(format="%(levelname)s:\t%(message)s", level=logging.INFO)
    DBHandler.client = get_motor_client()
    DBHandler.database = get_motor_db()
    migration_dir = Path(__file__).parent.joinpath("migrations").resolve()
    root = await MigrationNode.build(migration_dir)
    mode = RunningMode(direction=RunningDirections.FORWARD, distance=0)
    await root.run(mode, False)


if __name__ == "__main__":

    async def migrate():
        await init_db()
        await run_migrations()

    asyncio.run(migrate())
