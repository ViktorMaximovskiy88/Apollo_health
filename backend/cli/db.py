import logging
import sys
from pathlib import Path

import asyncclick as click

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))

from beanie.migrations.database import DBHandler
from beanie.migrations.models import RunningDirections, RunningMode
from beanie.migrations.runner import MigrationNode

from backend.common.db.init import get_motor_client, get_motor_db, init_db

log = logging.getLogger(__name__)
migration_dir = Path(__file__).parent.parent.joinpath("common", "db", "migrations").resolve()


@click.group()
@click.pass_context
async def db(ctx):
    DBHandler.client = get_motor_client()
    DBHandler.database = get_motor_db()
    await init_db()


@db.command()
@click.pass_context
@click.option(
    "--direction",
    help="FORWARD or BACKWARD migration",
    default=RunningDirections.FORWARD,
    type=RunningDirections,
)
@click.option("--distance", help="Number of migrations to process", default=0, type=int)
async def migrate(
    ctx,
    direction: RunningDirections,
    distance: int,
):
    runner = await MigrationNode.build(migration_dir)
    mode = RunningMode(direction=direction, distance=distance)
    await runner.run(mode, False)


@db.command()
@click.pass_context
async def run_latest(ctx):
    runner = await MigrationNode.build(migration_dir)
    mode = RunningMode(direction=RunningDirections.FORWARD, distance=1)
    await runner.run(mode, False)


@db.command()
@click.pass_context
async def reset_latest(ctx):
    runner = await MigrationNode.build(migration_dir)
    mode = RunningMode(direction=RunningDirections.BACKWARD, distance=1)
    await runner.run(mode, False)
