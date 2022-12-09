import csv
import logging
import os

from beanie import free_fall_migration

from backend.common.models.payer_backbone import UMP


class Forward:
    @free_fall_migration(document_models=[UMP])
    async def add_legacy_policy_label(self, session):
        current_path = os.path.dirname(os.path.realpath(__file__))
        fixture_path = os.path.join(current_path, "../fixtures/legacy_payer_labels.csv")
        with open(fixture_path) as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                name = row[0]
                legacy_policy_label = row[1]
                payer = await UMP.find({"name": name}).first_or_none()
                if payer is None:
                    logging.warn(f"Payer name not found: {name}")
                    continue
                if payer.legacy_policy_label is not None:
                    continue
                payer.legacy_policy_label = legacy_policy_label
                await payer.save()


class Backward:
    ...
