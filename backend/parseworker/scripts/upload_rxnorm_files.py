import os

import typer
from backend.common.storage.client import ModelStorageClient


def main(local_path: str):
    client = ModelStorageClient()
    file_set_name = os.path.basename(local_path)
    upload_location = f'rxnorm/data/{file_set_name}'

    for rel_path in os.listdir(f'{local_path}/rrf'):
        file_path = f'{local_path}/rrf/{rel_path}'
        client.write_object(f"{upload_location}/{rel_path}", file_path)

if __name__ == '__main__':
    typer.run(main)