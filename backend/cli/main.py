import sys
from pathlib import Path

import asyncclick as click

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from backend.cli.date_parser import date_parser
from backend.cli.lineage import lineage
from backend.cli.par import par
from backend.cli.text_parser import text_parser


@click.group()
@click.pass_context
async def cli(ctx):
    pass


cli.add_command(lineage)
cli.add_command(date_parser)
cli.add_command(text_parser)
cli.add_command(par)

if __name__ == "__main__":
    cli(_anyio_backend="asyncio")
