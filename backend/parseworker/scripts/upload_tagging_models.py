import os
import pathlib

import typer

from backend.common.storage.client import ModelStorageClient


def main(output_folder: pathlib.Path = typer.Argument(None)):
    client = ModelStorageClient()
    for root, _, files in os.walk(output_folder):
        for file in files:
            print(f"{root}/{file}", f"{root}/{file}")
            client.write_object(f"{root}/{file}", f"{root}/{file}")


if __name__ == "__main__":
    typer.run(main)
