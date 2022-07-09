import asyncio
import csv
import sys
from pathlib import Path

this_folder = Path(__file__).parent
sys.path.append(str(this_folder.joinpath("../../..").resolve()))
from backend.common.db.init import init_db
from backend.common.models.indication import Indication

async def create_indications():
    if await Indication.count():
        print('Indications are already loaded')
        return

    indications: dict[int, Indication] = {}
    csv_path = this_folder.joinpath('default_indications_and_terms.csv')
    with open(csv_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            indication_number = int(row['IndicationId'])
            name = row['Name']
            term = row['Term']
            indication = indications.setdefault(
                indication_number,
                Indication(
                    name=name.strip(),
                    terms=[term],
                    indication_number=indication_number
                )
            )
            indication.terms.append(term)

    for indication in indications.values():
        indication.terms = list(set(indication.terms))
        await indication.save()

async def execute():
    await init_db()
    await create_indications()


if __name__ == "__main__":
    asyncio.run(execute())