import csv
import os

from beanie import free_fall_migration

from backend.common.core.enums import SearchableType
from backend.common.models.search_codes import SearchCodeSet


class Forward:
    @free_fall_migration(document_models=[SearchCodeSet])
    async def add_legacy_policy_label(self, session):
        existing_tokens = await SearchCodeSet.find({"type": SearchableType.UNIVERSAL}).exists()
        if existing_tokens:
            return

        current_path = os.path.dirname(os.path.realpath(__file__))
        fixture_path = os.path.join(current_path, "../fixtures/universal_tokens.csv")
        search_tokens: set[str] = set()
        with open(fixture_path) as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                search_token = row[0]
                search_tokens.add(search_token)
        universal_tokens = SearchCodeSet(type=SearchableType.UNIVERSAL, codes=search_tokens)
        await universal_tokens.create()


class Backward:
    ...
