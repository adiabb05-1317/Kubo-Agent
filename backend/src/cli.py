from __future__ import annotations

import asyncio

import click

from .db import init_models


@click.group()
def cli() -> None:  # pragma: no cover - small utility
    pass


@cli.command("init-db")
def init_db_cmd() -> None:
    asyncio.run(init_models())
    click.echo("DB initialized.")


if __name__ == "__main__":  # pragma: no cover
    cli()


