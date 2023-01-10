import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.joinpath("../../..").resolve()))

import asyncio

from backend.common.db.init import get_motor_db, init_db


async def ensure_indices():
    db = get_motor_db()
    # LinktaskLog
    expire_after_seconds = 30 * 86400  # 30 days
    await db.LinkTaskLog.create_index(
        "created_at", expireAfterSeconds=expire_after_seconds, background=True
    )

    expire_after_seconds = 10 * 86400  # 10 days
    await db.TaskLog.create_index(
        "created_at", expireAfterSeconds=expire_after_seconds, background=True
    )


async def execute():
    await init_db()
    await ensure_indices()


if __name__ == "__main__":
    asyncio.run(execute())
